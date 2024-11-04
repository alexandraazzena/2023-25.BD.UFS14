import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

# 1. Azure Function per il controllo della vaidità dell'url
@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    url_da_validare = req.params.get('url_da_validare')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    '''if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )'''
    if url_da_validare:
        url_valido = controllo_validita_url(url_da_validare)
        if url_valido:
            return func.HttpResponse(f"URL valido")
        else:
             return func.HttpResponse('URL non valido')
    
    
def controllo_validita_url(url):
    return url.startswith('http://') or url.startswith('https://')

# 2. Azure function per estrazione parole chiave
import re
from PyPDF2 import PdfReader
from io import BytesIO

app = func.FunctionApp()

#Funzione per estrarre tutto il testo dai PDF
def estrai_testo_pdf(contenuto_pdf_binario):
    reader = PdfReader(contenuto_pdf_binario)
    lunghezza_pdf = len(reader.pages)
    testo_estratto = ""
    for pagina in range(lunghezza_pdf):
        oggetto_pagina = reader.pages[pagina]
        testo_estratto += oggetto_pagina.extract_text()
    return testo_estratto

# Funzione per estrarre contesto attorno alle parole chiave
def estrai_contesto(testo_estratto, keyword, context_lines=2):
    if testo_estratto is None:
        return []

    righe = testo_estratto.split('\n')
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)  #Permette di trovare la parola chiave comunque sia scritta

    risultati = []
    for i, riga in enumerate(righe):
        if pattern.search(riga):
            start = max(0, i - context_lines)
            end = min(len(righe), i + context_lines + 1)
            contesto = "\n".join(righe[start:end])
            contesto = pattern.sub(f"**{keyword}**", contesto)  #Parola chiave messa in grassetto
            risultati.append(contesto)
    return risultati

# Caricare PDF e cercare parole chiave
@app.route(route="ricerca_keyword_pdf", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def ricerca_keyword_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Endpoint ricerca_keyword_pdf è stato chiamato.")
    
    try:
        # Riceve il PDF come file binario
        file_bytes = req.get_body()

        # Parole chiave da cercare
        keywords = ["LD₅₀", "LD50", "LD 50", "Ld50", "Ld₅₀"]
        
        # Estrae il testo dal PDF
        testo_estratto = estrai_testo_pdf(BytesIO(file_bytes))

        # Ricerca delle parole chiave
        contesti_estratti = estrai_contesto(testo_estratto, keywords)

        # Concatenare i contesti estratti in una stringa
        risultato = "\n\n".join(contesti_estratti) if contesti_estratti else "Nessun contesto trovato."

        # Restituisce i contesti come HttpResponse
        return func.HttpResponse(
            risultato,
            mimetype="text/plain",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Errore durante l'elaborazione del PDF: {e}")
        return func.HttpResponse("Errore durante l'elaborazione della richiesta.", status_code=500)


# svariate prove fallite

'''
import azure.functions as func
import json
import re
import logging

app = func.FunctionApp()

# Funzione per estrarre il contesto attorno a una parola chiave
def estrai_contesto(testo_estratto, keyword, context_lines=2):
    if testo_estratto is None:
        return []

    righe = testo_estratto.split('\n')
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)

    risultati = []
    for i, riga in enumerate(righe):
        if pattern.search(riga):
            start = max(0, i - context_lines)
            end = min(len(righe), i + context_lines + 1)
            contesto = "\n".join(righe[start:end])
            contesto = pattern.sub(f"**{keyword}**", contesto)
            risultati.append(contesto)
    return risultati

# Endpoint per estrarre il contesto attorno a una parola chiave in un testo
@app.route(route="estrai_contesto", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def estrai_contesto_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Endpoint estrai_contesto è stato chiamato.")

    try:
        # Estrae i parametri dal corpo della richiesta
        body = req.get_json()
        testo_estratto = body.get("testo")
        keyword = body.get("keyword")
        context_lines = body.get("context_lines", 2)

        if not testo_estratto or not keyword:
            return func.HttpResponse(
                "I parametri 'testo' e 'keyword' sono obbligatori.",
                status_code=400
            )

        # Chiama la funzione per estrarre i contesti
        contesti_estratti = estrai_contesto(testo_estratto, keyword, context_lines)

        # Restituisce i contesti estratti come JSON
        return func.HttpResponse(
            json.dumps(contesti_estratti, ensure_ascii=False),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as e:
        logging.error(f"Errore nel parsing del JSON: {e}")
        return func.HttpResponse("Errore nel parsing del JSON.", status_code=400)
    except Exception as e:
        logging.error(f"Errore durante l'estrazione del contesto: {e}")
        return func.HttpResponse("Errore durante l'elaborazione della richiesta.", status_code=500)'''



'''def scarica_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        if 'application/pdf' in response.headers.get('Content-Type', ''):
            contenuto_pdf_binario = BytesIO(response.content)
            return contenuto_pdf_binario
        else:
            logging.warning(f"Il contenuto scaricato da {url} non è un PDF.")
            return None
    else:
        logging.error(f"Impossibile scaricare il PDF da {url}.")
        return None

# Funzione principale per gestire l'endpoint HTTP
@app.route(route="download_pdf", auth_level=func.AuthLevel.ANONYMOUS)
def download_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Download PDF endpoint è stato chiamato.')

    url = req.params.get('url')
    if not url:
        return func.HttpResponse("URL non fornito. Specifica un URL come parametro della query string.", status_code=400)

    # Scarica il PDF utilizzando la funzione helper
    pdf_content = scarica_pdf(url)
    if pdf_content:
        return func.HttpResponse(pdf_content.getvalue(), mimetype="application/pdf")
    else:
        return func.HttpResponse("Errore durante il download del PDF o contenuto non è un PDF.", status_code=400)'''





'''import azure.functions as func
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

    # Controlla se l'URL da validare è presente
    if url_da_validare:
        url_valido = controllo_validita_url(url_da_validare)
        if url_valido:
            return func.HttpResponse("URL valido", status_code=200)
        else:
            return func.HttpResponse("URL non valido", status_code=400)

    # Controlla se il nome è presente
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.", status_code=200)

    # Messaggio predefinito
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
        # Controlla il codice di stato e il tipo di contenuto
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            contenuto_pdf_binario = BytesIO(response.content)
            return func.HttpResponse(contenuto_pdf_binario.getvalue(), mimetype="application/pdf", status_code=200)
        else:
            return func.HttpResponse("Il contenuto scaricato non è un PDF.", status_code=400)
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nel download del PDF: {e}")
        return func.HttpResponse("Errore durante il download del PDF.", status_code=500)

# Funzione per estrarre il testo da un PDF inviato come corpo della richiesta
@app.route(route="estrai_testo", auth_level=func.AuthLevel.ANONYMOUS)
def estrai_testo(req: func.HttpRequest) -> func.HttpResponse:
    try:
        file_bytes = req.get_body()
        if not file_bytes:
            return func.HttpResponse("Nessun file fornito nel corpo della richiesta.", status_code=400)

        reader = PdfReader(BytesIO(file_bytes))
        testo_estratto = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        
        if not testo_estratto:
            return func.HttpResponse("Nessun testo estratto dal PDF.", status_code=204)  # No Content
        
        return func.HttpResponse(testo_estratto, mimetype="text/plain", status_code=200)
    except Exception as e:
        logging.error(f"Errore nell'estrazione del testo: {e}")
        return func.HttpResponse("Errore nell'estrazione del testo dal PDF.", status_code=500)
'''