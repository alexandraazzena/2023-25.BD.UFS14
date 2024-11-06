import azure.functions as func
import datetime
import json
import logging
import re
from pypdf import PdfReader
from io import BytesIO

app = func.FunctionApp()

# 1. Azure Function per il controllo della vaidità dell'url
@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    url_da_validare = req.params.get('url_da_validare')

    if url_da_validare:
        url_valido = controllo_validita_url(url_da_validare)
        if url_valido:
            return func.HttpResponse(f"URL valido")
        else:
             return func.HttpResponse('URL non valido')
    
    


# 2. Azure function per estrazione parole chiave
@app.route(route="ricerca_keyword_pdf", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def ricerca_keyword_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Endpoint chiamato.")
    
    try:
        # Riceve il PDF come file binario
        testo = estrai_testo_pdf(BytesIO(req.get_body()))
        # Parole chiave da cercare
        keywords = ["LD₅₀", "LD50", "LD 50", "Ld50", "Ld₅₀"]
        # Estrae il testo dal PDF
        contesti = estrai_contesto(testo, keywords)
        
        # Concatena i contesti estratti in una stringa e restituisce i contesti come HttpResponse
        return func.HttpResponse(
            "\n\n".join(contesti) if contesti else "Nessun contesto trovato.",
            mimetype="text/plain",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Errore: {e}")
        return func.HttpResponse("Errore nell'elaborazione.", status_code=500)




# Funzioni

#Funzione che verifica la validità dell'url
def controllo_validita_url(url):
    return url.startswith('http://') or url.startswith('https://')

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