from file_function import controllo_validita_url, crea_dizionario

def test_controllo_validita_url():
    assert controllo_validita_url('https://google.com')== True
    assert controllo_validita_url('http://google.com')== True
    assert controllo_validita_url('https//google.com')== False

def test_crea_diz():

    # Esecuzione della funzione da testare
    output = crea_dizionario(nomi_links)

    # Verifica che il risultato sia un dizionario
    assert isinstance(output, dict), "Il risultato non è un dizionario"

    # Verifica che ogni chiave sia una stringa
    for chiave in output.keys():
        assert isinstance(chiave, str), f"La chiave {chiave} non è una stringa"

    # Verifica che ogni valore sia una stringa
    for valore in output.values():
        assert isinstance(valore, str), f"Il valore {valore} non è una stringa"
