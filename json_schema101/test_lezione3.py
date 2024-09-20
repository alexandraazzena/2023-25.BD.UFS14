from jsonschema import validate
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
    
