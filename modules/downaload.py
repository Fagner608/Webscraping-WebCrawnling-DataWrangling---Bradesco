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
import shutil
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver import Keys, ActionChains
import calendar
from requests import openBrowser
import zipfile



class download_repors():

    def __init__(self, driver: WebDriver, date: datetime.date):
        self.driver = driver
        self.navigate_page()
        self.date = date
        self.download_reports()
        
    def navigate_page(self):
        self.driver.get('https://www.intergrall.com.br/callcenter/pbc/bp_pbc_extrato_financeiro.php?nivel=PHR&titulo=PBC-Extrato+Financeiro&tipo_popup=AJ')
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#uraModal_JanelaNotificacao_header_btnClose'))).click()
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button.btn:nth-child(2)'))).click()
        
        return self.driver
    


    def __move_file(self, date: datetime.date):
        os.makedirs(f"./relatórios/{date.year}/{date.month}/", exist_ok = True)
        while os.listdir("./download") == 0:
            continue
        with zipfile.ZipFile(f"./download/{os.listdir('./download')[0]}") as fp:
            fp.extractall("./download")

        shutil.copy("./download/" + os.listdir('./download')[0], f'./relatórios/{date.year}/{date.month}/relatorio_{date}.csv')
        for i in os.listdir('./download'):
            os.remove(f"./download/{i}")



    def download_reports(self):
        time.sleep(3)
        # tabela_html = self.driver.find_element(By.CSS_SELECTOR, '.table')
        # tabela_html = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.table')))
        tabela_html = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.table')))
        linhas = tabela_html.find_elements(By.CSS_SELECTOR, 'tr')


        date = self.date
        while date < date.today():
            data_1 = date
            data_2 = data_1 + datetime.timedelta(days = 1)


            for i in  linhas:
                button = i.find_elements(By.CSS_SELECTOR, 'td')
                for j in button:
                    if j.text == "":
                        if search(f"{data_1.strftime('%d/%m/%Y')}", i.text) and search(f"{data_2.strftime('%d/%m/%Y')}", i.text):
                            while True:
                                j.click()
                                try:
                                    WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.modal-dialog')))
                                    WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btn_ok'))).click()
                                    continue
                                except:
                                    WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#uraModal__header_btnClose'))).click()
                                    self.__move_file(date  = date)
                                    return 
            date = date + datetime.timedelta(days = 1)



