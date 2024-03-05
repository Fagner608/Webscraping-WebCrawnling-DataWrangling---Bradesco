import pandas as pd
from datetime import date
from os import path, makedirs
from shutil import move, copy
from json import load


#  classe para carregar relatórios
class wor_tables():


    def __init__(self, date_work: date):
        self.date_work = date_work
        self.processing = False
        self.__load_tables_codes()
        self.read_reports()
        self.production_report_to_storm()
        self.comission_repor_to_storm()
        self.zz()


    def __load_tables_codes(self):
        with open("./data/tables_cod.json", mode = 'r', encoding ='utf-8') as fp:
            dados = load(fp)
            table_code = dados['orgao']
            setattr(self, 'tables_code', table_code)


    def read_reports(self):
            path_to_read = f"./relatórios/{self.date_work.year}/{self.date_work.month}/relatorio_{self.date_work}.csv"
            
            tables_code = getattr(self, 'tables_code')
            if path.exists(path_to_read):
                dados = pd.read_csv(path_to_read, encoding = 'latin-1', sep = ';')
                dados = dados[~dados['CONTRATO'].isna()]
                dados.CONTRATO = dados.CONTRATO.astype(dtype = int)
                dados['PRAZO CONTRATO'] = dados['PRAZO CONTRATO'].astype(dtype = int)
                dados['CÓDIGO DE USUARIO'] = dados['CÓDIGO DE USUARIO'].astype(dtype = int)
                dados['CPF CLIENTE'] = dados['CPF CLIENTE'].astype(dtype = int)
                dados['VALOR BRUTO'] = dados['VALOR BRUTO'].map(lambda x: str(x).replace(".", ","))
                dados['VALOR LANÇAMENTO'] = dados['VALOR LANÇAMENTO'].map(lambda x: str(x).replace(".", ","))
                dados = dados[~dados['VALOR LANÇAMENTO'].str.contains("0|0.0")]
                dados['CÓDIGO PRODUTO'] = dados['CÓDIGO PRODUTO'].map(lambda x: str(int(x)))
                dados['CÓDIGO PRODUTO'] = dados['CÓDIGO PRODUTO'].map(tables_code)
                setattr(self, 'report', dados)
                self.processing = True


    def production_report_to_storm(self):
        if self.processing:
            dados = getattr(self, 'report')
            path_to_saving= f"../Importados_storm/Producao/{self.date_work.year}/{self.date_work.month}/"
            makedirs(path_to_saving, exist_ok = True)
            columnas_to_rename = ['PROPOSTA',
                                'DATA CADASTRO',
                                'BANCO',
                                'ORGAO',
                                'CODIGO TABELA',
                                'TIPO DE OPERACAO',
                                'NUMERO PARCELAS',
                                'VALOR PARCELAS',
                                'VALOR OPERACAO',
                                'VALOR LIBERADO',
                                'VALOR QUITAR',
                                'USUARIO BANCO',
                                'SITUACAO',
                                'DATA DE PAGAMENTO',
                                'CPF',
                                'NOME',
                                'FORMALIZACAO DIGITAL'
                                ]
            
            production_report = dados[[
                                'CONTRATO',
                                'DATA BASE CONTRATO',
                                'NOME CONVÊNIO',
                                'CÓDIGO PRODUTO',
                                'PRAZO CONTRATO',
                                'VALOR BRUTO',
                                'REMUNERAÇÃO VALOR PAGO',
                                'CÓDIGO DE USUARIO',
                                'DATA EFETIVA CONTRATO',
                                'CPF CLIENTE',
                                'NOME CLIENTE'
                                    
                                ]]
            production_report.insert(2, 'BANCO', 'BANCO BRADESCO')
            production_report.insert(5, 'TIPO DE OPERACAO', '')
            production_report.insert(7, 'VALOR PARCELAS', '')
            production_report.insert(10, 'VALOR QUITAR', '')
            production_report.insert(12, 'SITUACAO', 'PAGO')
            production_report.insert(15, 'FORMALIZACAO DIGITAL', 'SIM')
            production_report.columns = columnas_to_rename
            production_report['TIPO DE OPERACAO'] = 0
            setattr(self, 'production', production_report)
            production_report.to_csv(path_to_saving + f"producao_{self.date_work}.csv", sep = ';', index = False)




    def comission_repor_to_storm(self):
        if self.processing:
            dados = getattr(self, 'report')
            path_to_saving= f"../Importados_storm/Comissao/{self.date_work.year}/{self.date_work.month}/"
            makedirs(path_to_saving, exist_ok = True)
            columnas_to_rename_comission = ['#ADE#',
                                        '#VALOR_BASE#',
                                        '#VALOR_BASE_BRUTO#',
                                        '#VALOR_CMS#',
                                        '#PRAZO#',
                                        '#CODIGO_TABELA#',
                                        '#DATA_DIGITACAO#'
                                        ]
            
            comission_repor = dados[['CONTRATO', 'VALOR CONTRATO', 'VALOR BRUTO', 'VALOR LANÇAMENTO', 'PRAZO CONTRATO', 'CÓDIGO TABELA', 'DATA BASE CONTRATO']]
            comission_repor.columns = columnas_to_rename_comission
            setattr(self, 'comission', comission_repor)
            comission_repor.to_csv(path_to_saving + f"comissao_{self.date_work}.csv", sep = ';', index = False)




    def zz(self):
         if self.processing:
            production = getattr(self,'production' )
            comission = getattr(self,'comission' )
            zz_path = f"../zz_Bradesco.xlsx/"
            if path.exists(path = zz_path):
                copy("../zz_Bradesco.xlsx", './zx_bradesco.xlsx')
                comission = pd.concat([comission, pd.read_excel("./zx_bradesco.xlsx", sheet_name = 'comissao')])
                production = pd.concat([production, pd.read_excel("./zx_bradesco.xlsx", sheet_name = 'producao')])


            writer = pd.ExcelWriter(f'./zx_bradesco.xlsx', engine = "xlsxwriter")
            comission.drop_duplicates(subset =['#ADE#'], inplace = True)
            production.drop_duplicates(subset =['PROPOSTA'], inplace = True)
            production.to_excel(writer, index =False, sheet_name = 'producao')
            comission.to_excel(writer, index =False, sheet_name = 'comissao')
            writer.close()
            copy("./zx_bradesco.xlsx", '../zz_Bradesco.xlsx')
                   