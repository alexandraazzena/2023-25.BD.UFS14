from jsonschema import validate
from pytest_snapshot.plugin import Snapshot
from lezione3 import schema

# TEST test_sample lezione1
def func(x):
    return x + 1

def test_answer():
    assert func(4) == 5

'''
# TEST
def test_jsonschema_success(instance, schema):
    validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema)
'''

# TEST
def test_jsonschema_success():
    assert my_validate(instance={"name" : "Eggs", "price" : 34.99}, schema=schema) == True

# WRAPPER 
def my_validate(instance, schema):
    try:
        validate(instance=instance, schema=schema)
        return True
    except: 
        return False
    

# SNAPSHOOT TEST
#(scrivo requirement.test.txt in cui inserisco solo librerie di test)

def test_function_output_with_snapshot(snapshot: Snapshot):
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.

    pierino = func(5)
    pierino_stringa = str(pierino)

    snapshot.assert_match(str(pierino_stringa), 'foo_output.txt')


# CREO CSV
frutti = '''frutti,prezzo,colore,sapore
pera,100,rossa,dolce
mela,500,blu,gustosa
ananas,300,gialla,piccante 
'''

def test_function_output_with_snapshot_csv(snapshot: Snapshot):
    snapshot.snapshot_dir = 'snapshots'  # This line is optional.

    snapshot.assert_match(frutti, 'frutta.csv')