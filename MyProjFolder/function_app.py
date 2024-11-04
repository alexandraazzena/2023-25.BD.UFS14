import azure.functions as func
import logging
import requests
from io import BytesIO
from PyPDF2 import PdfReader

app = func.FunctionApp()

@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    url_da_validare = req.params.get('url_da_validare')

    if url_da_validare:
        url_valido = controllo_validita_url(url_da_validare)
        if url_valido:
            return func.HttpResponse("URL valido")
        else:
            return func.HttpResponse("URL non valido", status_code=400)

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name or a valid URL.",
            status_code=200
        )

# Funzione per verificare se un URL è valido
def controllo_validita_url(url):
    return url.startswith('http://') or url.startswith('https://')

# Funzione per scaricare il PDF e restituirlo come binario
@app.route(route="scarica_pdf", auth_level=func.AuthLevel.ANONYMOUS)
def scarica_pdf(req: func.HttpRequest) -> func.HttpResponse:
    url = req.params.get('url')
    if not url:
        return func.HttpResponse("URL non fornito.", status_code=400)

    try:
        response = requests.get(url)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            contenuto_pdf_binario = BytesIO(response.content)
            return func.HttpResponse(contenuto_pdf_binario.getvalue(), mimetype="application/pdf")
        else:
            return func.HttpResponse("Il contenuto scaricato non è un PDF.", status_code=400)
    except Exception as e:
        logging.error(f"Errore nel download del PDF: {e}")
        return func.HttpResponse("Errore durante il download del PDF.", status_code=500)

# Funzione per estrarre il testo da un PDF inviato come corpo della richiesta
@app.route(route="estrai_testo", auth_level=func.AuthLevel.ANONYMOUS)
def estrai_testo(req: func.HttpRequest) -> func.HttpResponse:
    try:
        file_bytes = req.get_body()
        reader = PdfReader(BytesIO(file_bytes))
        testo_estratto = "".join(page.extract_text() for page in reader.pages)
        return func.HttpResponse(testo_estratto, mimetype="text/plain")
    except Exception as e:
        logging.error(f"Errore nell'estrazione del testo: {e}")
        return func.HttpResponse("Errore nell'estrazione del testo dal PDF.", status_code=500)
