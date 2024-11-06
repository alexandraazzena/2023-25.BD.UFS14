import azure.functions as func
import datetime
import json
import logging
import re
from pypdf import PdfReader
from io import BytesIO
import requests

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
@app.route(route="ricerca_keyword_pdf", auth_level=func.AuthLevel.ANONYMOUS)
def ricerca_keyword_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Endpoint chiamato.")

    url = req.params.get('url_da_validare')
    
    if not url or not controllo_validita_url(url):
        return func.HttpResponse("URL non valido o mancante.", status_code=400)
    
    try:
        # Scarica il PDF dall'URL
        response = requests.get(url)
        response.raise_for_status()  # Alza eccezione se l'URL non risponde correttamente
        
        # Converte il PDF scaricato in binario
        testo = estrai_testo_pdf(BytesIO(response.content))
        
        # Parole chiave da cercare
        keywords = ["LD₅₀", "LD50", "LD 50", "Ld50", "Ld₅₀"]
        
        # Estrae i contesti
        contesti = []
        for keyword in keywords:
            contesti.extend(estrai_contesto(testo, keyword))
        
        # Concatena i contesti estratti
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
        testo_estratto += oggetto_pagina.extract_text() or ""
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