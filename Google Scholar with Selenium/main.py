# -*- coding: utf-8 -*-
"""



"""

import os
import schedule
import time
from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta, time
import re
import pandas as pd

def verifica_captcha(driver):
    try:
        driver.find_element(By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")
        input("Tekan enter untuk menyelesaikan reCaptcha")
        return True
    except Exception:
        return True


def try_parse_int(string: str):
    try:
        integer = int(string)
        return integer
    except Exception:
        return 0

def job():
    words = input("Apa yang ingin Anda telusuri?")
    n_artigos = input("Berapa banyak artikel yang ingin Anda kumpulkan?")
    n_artigos = int(n_artigos)
    restricao = input("Apakah Anda ingin mempersempit berdasarkan tahun ? y/n")
    string_ano = ''
    if(str.lower(restricao) == "y"):
        ano = input("Dari tahun berapa Anda ingin mengumpulkan referensi?")
        string_ano = '&as_ylo='+str(ano)
    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    data = []
    contador = 0
    page = 0
    while contador <= n_artigos:
        page_str = '&start='+str(page)
        driver.get('https://scholar.google.com.br/scholar?hl=en&as_sdt=0%2C5&q='+words+string_ano+page_str)
        sleep(3)
        verifica_captcha(driver)
        if page == 0:
            results = driver.find_element(By.ID,'gs_ab_md')
            results = results.find_element(By.CLASS_NAME,'gs_ab_mdw')
            results = results.get_attribute('innerHTML')
            print(results)
            n_res = results.split(' ')[1].replace('.','')
            n_res = int(n_res)
            if n_res < n_artigos:
                n_artigos = n_res
        all = driver.find_elements(By.CLASS_NAME,'gs_ri')
        for element in all:
            contador+=1
            journal,fonte = '',''
            titulo = element.find_element(By.TAG_NAME,'a')
            link = titulo.get_attribute('href')
            titulo_str = titulo.get_attribute('innerHTML')
            titulo_str = titulo_str.replace('<b>','').replace('</b>','').replace('&nbsp;','')
            autor = element.find_element(By.CLASS_NAME,'gs_a')
            autor_str = autor.get_attribute('innerHTML').replace('&nbsp;','')
            autor_str = re.sub('<[^<]+?>', '', autor_str)
            autor_split = autor_str.split('-')
            if (len(autor_split) == 3):
                autores_nome, journal ,fonte = autor_split
            elif (len(autor_split) == 2):
                autores_nome,fonte = autor_split
            else:
                autores_nome = autor_split[0]
            autores_nome_split = autores_nome.split(',')
            autor_principal = autores_nome_split[0]
            journal_split = journal.split(',')
            ano = journal_split[-1]
            citacoes = element.find_element(By.CLASS_NAME,'gs_fl')
            citacoes_tag = citacoes.find_elements(By.TAG_NAME,'a')
            citacoes_numero = citacoes_tag[2].get_attribute('innerHTML')
            citacoes_numero_split = citacoes_numero.split(' ')
            numero_citacoes = citacoes_numero_split[-1]
            numero_citacoes = try_parse_int(numero_citacoes)
            # # TODO: Incluir verificador de Recaptcha que funcione na linha 85 para coletar o BibTex
            # citacoes_tag[1].click()
            # sleep(3)
            # board = driver.find_element(By.ID,'gs_citi')
            # bibtex = board.find_elements(By.TAG_NAME,'a')
            # bibtex[0].click()
            # sleep(2)
            # verifica_captcha(driver)
            # ref = driver.find_element(By.TAG_NAME,'pre')
            # reference = ref.get_attribute('innerHTML')
            # driver.back()
            # sleep(2)
            # cancel = driver.find_element(By.TAG_NAME,'a')
            # cancel.click()
            # sleep(1)
            data.append([titulo_str,autor_principal,ano,journal,fonte,numero_citacoes,link])
        page += 10
    df = pd.DataFrame(data, columns = ['Judul', 'Author Journal','Tahun','Journal','Website Journal','Citations','Link'])
    now = datetime.now()
    date_time = now.strftime("%d-%m-%Y_%H-%M-%S")
    df.to_excel('referensi'+str(date_time)+'.xlsx')
    print (f"Referensi berhasil dikumpulkan!")
    sleep(1)
    driver.quit()
    return schedule.CancelJob

job()
print("Obrigado! Volte sempre :)")


