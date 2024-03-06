from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from re import search
import os
from pathlib import Path
import time
import datetime
import locale
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver import Keys, ActionChains
import calendar
from dotenv import dotenv_values


# classe para acesar

class openBrowser():

    def __init__(self, user_credencials: dict = dotenv_values("./data/.env")) -> WebDriver:
        print(user_credencials)
        self.password = user_credencials['PASSWORD_LOGIN']
        self.login = user_credencials['LOGIN']
        self.__mkDirDownload()
        

    def __mkDirDownload(self) -> None:
        os.makedirs("download", exist_ok=True)
        for file in os.listdir('download'):
            os.remove(f"download\\{file}")
            
    def initialize_driver(self):
        
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", fr"{str(Path().absolute())}\\download")
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
        driver = webdriver.Firefox(options=options)
        
        
        driver.maximize_window()
        driver.get("https://www.intergrall.com.br/callcenter/cc_login.php")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#login"))).send_keys(self.login)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#password"))).send_keys(self.password)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id = 'loginBtn']"))).click()
        try:
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#messageError')))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#password"))).send_keys(self.password)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id = 'loginBtn']"))).click()
        except TimeoutException:
            pass

        return driver
    

    # classe para extrair tabelas
class get_tables():

    def __init__(self, driver: WebDriver, date: datetime.date):
        self.date = date
        self.driver = driver
        self.to_extract()
        self.calendar_manipulate()



    def click_button_css_selector(self, path: str, name_button: str):
        driver = self.driver
        try:
            button = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'{path}')))
            driver.execute_script("arguments[0].click()", button)
        except:
            print(f"Erro o clicar no {name_button}'")
            raise

    def to_extract(self):
        self.driver.get('https://www.intergrall.com.br/callcenter/pbc/bp_pbc_extrato_financeiro.php?nivel=PHR&titulo=PBC-Extrato+Financeiro&tipo_popup=AJ')
        self.click_button_css_selector(path = '#uraModal_JanelaNotificacao_header_btnClose', name_button = 'Close')
        self.click_button_css_selector(path = 'button.btn:nth-child(2)', name_button = 'Analítico')
        self.click_button_css_selector(path=  '#btn_cad_extrato_analitico', name_button = 'Solicitar Exportação' )
        return self.driver


    def __calendar_handle(self, path: str, date: datetime.date):

        # self.driver.find_element(By.CSS_SELECTOR, f'{path}').send_keys(date.strftime("%d/%m/%Y"))
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'{path}'))).send_keys(date.strftime("%d/%m/%Y"))
        calendar_year = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.datepicker-days > table:nth-child(1) > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(2)'))).text.upper()
        while date.strftime("%B %Y").upper() != calendar_year:
            if int(calendar_year.split(" ")[1]) < date.year: 
                self.click_button_css_selector(path = '.datepicker-days > table:nth-child(1) > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(3) > i:nth-child(1)', name_button = 'Encontrar mês')
                calendar_year = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.datepicker-days > table:nth-child(1) > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(2)'))).text.upper()
                time.sleep(1)
            else:
                self.click_button_css_selector(path = '.datepicker-days > table:nth-child(1) > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(1) > i:nth-child(1)', name_button = 'Voltar data')
                calendar_year = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.datepicker-days > table:nth-child(1) > thead:nth-child(1) > tr:nth-child(1) > th:nth-child(2)'))).text.upper()
                time.sleep(1)
                

        elements = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.datepicker-days > table:nth-child(1)')))
        calendar_element = elements.find_elements(By.CSS_SELECTOR, 'tbody')
       

        for i in calendar_element:
            result = i.find_elements(By.CSS_SELECTOR, 'tr')
            # obs: o calendário está capturado até aqui
            for j in result:
                # até aqui, o código captura todas as linhas do calendário

                day = j.find_elements(By.CSS_SELECTOR, 'td')

                for k in day:
                
                    
                    if str(k.text) == str(date.day):
                        self.driver.execute_script("arguments[0].click();", k)
                        self.driver.find_element(By.CSS_SELECTOR, '#cod_contrato').click()
                        return  
                            
                

    def request_report(self):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#id_bt_enviar'))).click()
        allert = self.driver.switch_to.alert
        self.driver_alert = allert.text

        if self.driver_alert == 'Nenhum registro encontrado!':
            pass

        else:
            allert = self.driver.switch_to.alert
            allert.accept()
            p = self.driver.current_window_handle
            chwd = self.driver.window_handles
            for w in chwd:

                if(w!=p):
                    self.driver.switch_to.window(w)
                    break
            




    def calendar_manipulate(self):
        mainWin = self.driver.window_handles[1]
        self.driver.switch_to.window(mainWin)
        locale.setlocale(locale.LC_ALL, 'pt_pt.UTF-8')
        
        
        start_date = self.date
        end_date = start_date + datetime.timedelta(days = 1)
        
        print(start_date, "--", end_date)
        for i, j in zip(['#dia_ini_prop', '#dia_fim_prop'], [start_date, end_date]):
            self.__calendar_handle(path = i, date = j)

        self.request_report()
        self.driver.quit()