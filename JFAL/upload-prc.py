webapp_url = "https://script.google.com/macros/s/AKfycbwkfUAHv6SE2R2tghhbU80xwuraZE9mmljqv31tnWixWXJJRbT5RV-ISvyqbe2t32Mb/exec"

def send_pdf_to_driver(filepath):

    import requests
    import base64

    with open(filepath, 'rb') as file:
        file_contents = file.read()
        encoded_pdf = base64.b64encode(file_contents).decode('utf-8')
        data = {
            "spreadsheetId": "1hvUaTjeG_d4-yEBmjQltwk8GwLahSK2xggC0r155r3Q",
            "sheetName": "Guias",
            "folderId": "1N4Z7o8WmCBv2KdWA5cvmBe-E9pn5bjVj",
            "filename": filepath.split('\\')[-1], 
            "file": encoded_pdf
        }
        
        response = requests.post(webapp_url, json=data)
        print(response.status_code)

import os
import shutil

folder = "C:/Projetos/webscrappers/JFAL/PDFs"
done_folder = "C:/Projetos/webscrappers/JFAL/PDFs/Enviados"

files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

for file in files:
    try:
        send_pdf_to_driver(file)
        shutil.move(file, done_folder)
        print(file)
    except Exception as e:
        print(e)
        exit