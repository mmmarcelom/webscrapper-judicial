function doPost(e) {
  const data = JSON.parse(e.postData.contents)

  try {
    var decodedFile = Utilities.base64Decode(data.file, Utilities.Charset.UTF_8)
    var blob = Utilities.newBlob(decodedFile, MimeType.PDF, data.filename)
    var folder = DriveApp.getFolderById(data.folderId)
    var pdfFile = folder.createFile(blob).setName(data.filename)
    SpreadsheetApp.openById(data.spreadsheetId).getSheetByName(data.sheetName).appendRow([
      new Date(),
      data.filename,
      pdfFile.getUrl()
    ])
    return ContentService.createTextOutput('File saved to Google Drive').setMimeType(ContentService.MimeType.TEXT);
  } catch (error) {
    return ContentService.createTextOutput('Error: ' + error.message);
  }
}

const example = {
"spreadsheetId": "1hvUaTjeG_d4-yEBmjQltwk8GwLahSK2xggC0r155r3Q",
"sheetName": "Guias",
"folderId": "1N4Z7o8WmCBv2KdWA5cvmBe-E9pn5bjVj",
"filename": 'protocolo_cadastro.pdf', 
"file": "base64_encoded_pdf"
}