import logging
import requests
from io import BytesIO
from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    url = req.params.get('url')
    if not url:
        return HttpResponse("URL non fornito.", status_code=400)

    try:
        response = requests.get(url)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            contenuto_pdf_binario = BytesIO(response.content)
            return HttpResponse(contenuto_pdf_binario.getvalue(), mimetype="application/pdf")
        else:
            return HttpResponse(f"Il contenuto scaricato da {url} non è un PDF.", status_code=400)
    except Exception as e:
        logging.error(f"Errore nel download del PDF: {e}")
        return HttpResponse("Errore durante il download del PDF.", status_code=500)
