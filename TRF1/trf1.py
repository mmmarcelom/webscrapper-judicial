# TRF 1

# Declarar a custom class TRF5_webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options

#from selenium.webdriver.support.ui import Select

from selenium import webdriver
from selenium.webdriver.common.by import By

class TRF5_Driver(webdriver.Chrome):
    
    implict_wait_value = 1
    loader_css = r"span#_viewRoot\:status\.start[style='display: none;']"
    
    def set_implicitly_wait(self, seconds):
        self.implict_wait_value = seconds
        self.implicitly_wait(seconds)
    
    # wait loader function
    def wait_loader(self, seconds=implict_wait_value):
        previous_implicit_wait = self.implict_wait_value
        self.implicitly_wait(1)
        i = 0
        while True:
            i+=1
            if i > seconds: break
            if self.find_elements(By.CSS_SELECTOR, self.loader_css):
                self.implicitly_wait(previous_implicit_wait)
                return
    
        self.implicitly_wait(previous_implicit_wait)
        raise Exception("Elemento nunca carregou")
    
    def login(self, username, password):

        self.get('https://pje1g.trf1.jus.br/pje')

        loginIframe = self.find_element(By.ID, "ssoFrame")
        self.switch_to.frame(loginIframe)
        self.find_element(By.ID, "username").send_keys(username)
        self.find_element(By.ID, "password").send_keys(password)
        self.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    def consultar_processo(self, consulta, wait_seconds=10):
        self.get("https://pje1g.trf1.jus.br/pje/Processo/ConsultaProcesso/listView.seam")
        
        if 'nome' in consulta.keys():
            self.find_element(By.CSS_SELECTOR, r"#fPP\:j_id145\:nomeParte").send_keys(consulta['nome'])
        
        if 'cpf' in consulta.keys():
            self.find_element(By.CSS_SELECTOR, r"#fPP\:dpDec\:documentoParte").send_keys(consulta['cpf'])

        if 'numero' in consulta.keys():
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:numeroSequencial").send_keys(consulta['numero'][0:7])
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:numeroDigitoVerificador").send_keys(consulta['numero'][8:10])
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:Ano").send_keys(consulta['numero'][11:15])
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:ramoJustica").send_keys(consulta['numero'][16])
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:respectivoTribunal").send_keys(consulta['numero'][18:20])
            self.find_element(By.CSS_SELECTOR, r"#fPP\:numeroProcesso\:NumeroOrgaoJustica").send_keys(consulta['numero'][21:25])
            
        self.find_element(By.CSS_SELECTOR, r"#fPP\:searchProcessos").click()
        self.wait_loader(seconds=wait_seconds)
    
        rows = self.find_elements(By.CSS_SELECTOR, r"#fPP\:processosTable\:tb .rich-table-row")
        if len(rows) == 0: return []
        lawsuits = []
        for row in rows:
            cells = row.find_elements(By.CLASS_NAME, "rich-table-cell")
            lawsuits.append({ "processo": cells[1].text })
        
        return lawsuits
    
# Iniciar o driver e fazer login...


import time
import requests
import os
import sys
from dotenv import load_dotenv
load_dotenv()

project_path = os.path.dirname(os.path.abspath(sys.argv[0])).replace('.venv\\Lib\\site-packages', '')
chromedriver_path = f'{project_path}/chromedriver.exe'

s = Service(chromedriver_path)

default_implicitly_wait = 10

options = Options()
options.add_argument('--headless=new')

driver = TRF5_Driver(service=s, options=options)
driver.set_implicitly_wait(default_implicitly_wait)

print("Iniciando no modo headless...")

driver.login(
    username=os.environ.get("TRF1_login"), 
    password=os.environ.get("TRF1_password")
)

print("Login realizado...")

time.sleep(10)

# Importar a lista...

import csv

def save(array, output_file, method):
    with open(f'{project_path}/{output_file}', method, encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        for row in array:
            writer.writerow(row)

def get_list(todo_file, done_file):
    todo = []
    with open(f'{project_path}/{todo_file}', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            todo.append(row[0])

    done = []
    with open(f'{project_path}/{done_file}', 'r', encoding='UTF-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            done.append(row[0])

    todo_list = set(todo) - set(done)
    
    return list(todo_list)

# ====================================================================================
# Iniciar consulta..


webapp_url = "https://script.google.com/macros/s/AKfycbw2OgtEWL7tFq4SckC2OjYtSVjKaIyVzv7z2tgslVuq3GcoVx_wDb6WuJLGLO2aMg47lA/exec"

todo_list = get_list("unafisco_todo.csv", "done.csv")

print("Processos restantes: ", len(todo_list))

for nome in todo_list:
    consulta = { "nome": nome }

    try:

        # Fecha todas as janelas exceto a de pesquisa do processo
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()
        driver.switch_to.window(driver.window_handles[0])

        print("Iniciando consulta: ", consulta)
        processos = driver.consultar_processo(consulta=consulta, wait_seconds=120)

        # Abrir o primeiro processo
        driver.find_element(By.CSS_SELECTOR, ".rich-table-firstrow > .rich-table-cell:nth-child(2) > a").click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        time.sleep(5)

        # Pegar dados da capa
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(5)

        navbar = driver.find_element(By.CSS_SELECTOR, '.dropdown.drop-menu.mais-detalhes')
        if not 'open' in navbar.get_attribute('class'): 
            navbar.click()
            time.sleep(5)
        
        processo = navbar.find_element(By.CSS_SELECTOR, ".titulo-topo").text
        partes = []
        polo = driver.find_element(By.CSS_SELECTOR, '#poloAtivo > table > tbody')
        for tr in polo.find_elements(By.TAG_NAME, 'tr'):
            pessoa = tr.find_element(By.CSS_SELECTOR, 'td > span > span').text.split(' - ')
            partes.append( {"nome": pessoa[0], "cpf": pessoa[1].replace('CPF: ','')[0:14] } )


        tabela = driver.find_element(By.CSS_SELECTOR, '#maisDetalhes > dl')
        dts = tabela.find_elements(By.TAG_NAME, 'dt')
        dds = tabela.find_elements(By.TAG_NAME, 'dd')
        capa = {}
        for i in range(len(dts)):
            capa[dts[i].text] = dds[i].text

        data = { 
            "nomeProcurado": consulta["nome"],
            "processo": processo,
            "partes": partes,
            "assunto": capa['Assunto'].replace(' /', '').split('\n'),
            "classeJudicial": capa['Classe judicial']
        }
        requests.post(url=webapp_url, json=data)
        save([[consulta["nome"]]], 'done.csv', 'a')
        print("Salvo")
        
    except Exception as e:
        print(e)