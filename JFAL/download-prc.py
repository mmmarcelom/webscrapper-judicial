import os
import sys
import time
import json
import csv

def download_prc(barcode):

    # Fecha todas as janelas exceto a de pesquisa do processo
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])

    id_input_consulta = "consultaDocumentoForm:numeroDocDecoration:numeroDoc"
    driver.find_element(By.ID, id_input_consulta).clear()
    driver.find_element(By.ID, id_input_consulta).send_keys(barcode.replace("B",""))

    driver.find_element(By.ID, "consultaDocumentoForm:botaoConsultar").click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(3)
    #driver.maximize_window()

    prc_number = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/table/tbody/tr[1]/td/b").text.replace('REQUISIÇÃO DE PAGAMENTO ','')
    driver.execute_script(f"document.title='{prc_number}';window.print();")
    print(prc_number)
    time.sleep(5)

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

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

kernel_path = os.path.dirname(os.path.abspath(sys.argv[0]))
print("kernel_path: ", kernel_path)

chromedriver_path = kernel_path.replace('JFAL', 'chromedriver.exe')
print("chromedriver_path: ", chromedriver_path)

project_path = kernel_path.replace('.venv/Lib/site-packages', 'JFAL')
download_folder = 'C:/Projetos/webscrappers/JFAL/PDFs'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', {
    'download.prompt_for_download': False,
    'printing.print_preview_sticky_settings.appState': json.dumps({
        "recentDestinations": [{"id": "Save as PDF", "origin": "local"}],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isLandscapeEnabled": True
    })
})
chrome_options.add_argument('--kiosk-printing')
chrome_options.add_argument('--kiosk-mode')

driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)

home_url = 'https://pje.jfal.jus.br/pje/Processo/ConsultaDocumento/listView.seam'
driver.get(home_url)

print("Acessando página do PJE..")

todo_list = get_list("todo.csv", "done.csv")

print("Carregando a lista...")
print(len(todo_list))

for barcode in todo_list:
    print("Buscando barcode: ", barcode)
    download_prc(barcode)
    save([[barcode]], 'done.csv', 'a')
    print("Salvo")