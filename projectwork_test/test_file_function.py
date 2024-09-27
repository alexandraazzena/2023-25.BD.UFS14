from file_function import controllo_validita_url, crea_dizionario
from jsonschema import validate

# ASSERT
def test_controllo_validita_url():
    assert controllo_validita_url('https://google.com')== True
    assert controllo_validita_url('http://google.com')== True
    assert controllo_validita_url('https//google.com')== False
    #assert controllo_validita_url('https://goo!!gle.com')== False


# JSON SCHEMA SENZA VALIDATE
'''def test_crea_diz():

    # Esecuzione della funzione da testare
    output = crea_dizionario([('a','b'), ('c', 'd'), ('e', 'f')])

    # Verifica che il risultato sia un dizionario
    assert isinstance(output, dict) == True

    # Verifica che ogni chiave sia una stringa
    for chiave in output.keys():
        assert isinstance(chiave, str) == True

    # Verifica che ogni valore sia una stringa
    for valore in output.values():
        assert isinstance(valore, str) == True
'''

# JSON SCHEMA CON VALIDATE
schema = {
    "type" : "object",
    "properties" : {
        "nomi" : {"type" : "string"},
        "link" : {"type" : "string"},
    },
}

# TEST
def test_jsonschema_success():
    assert my_validate(instance={"nomi" : "aaa", "link" : "bbb"}, schema=schema) == True

# WRAPPER 
def my_validate(instance, schema):
    try:
        validate(instance=instance, schema=schema)
        return True
    except: 
        return False


# SNAPSHOT
def test_function_output_with_snapshot(snapshot):
    output = str(crea_dizionario([('a','b'), ('c', 'd'), ('e', 'f')]))
    snapshot.assert_match(output, 'project_work_snap.txt')