import pytest
from starlette.testclient import TestClient
from fastapi_pagination import add_pagination
from main import app, get_db, get_s3_client, get_bucket
from testdatabase import override_get_db
from testboto import override_get_s3_client, override_get_bucket

add_pagination(app)
client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_s3_client] = override_get_s3_client
app.dependency_overrides[get_bucket] = override_get_bucket

testimagename = 'testmeme.png'

test_db = []

test_add_memes = [
    {
        "file" : testimagename,
        "text": "1" * 88
    },
    {
        "file" : testimagename,
        "text": "!-21fsjfnjFeowujkskdfl/"
    },
    {
        "file" : testimagename,
        "text": "Valid Meme"
    },
]

test_update_memes = [
    {
        "id" : 1,
        "file" : testimagename,
        "text": "1" * 88
    },
    {
        "id" : 2,
        "file" : testimagename,
        "text": "!-21fsjfnjFeowujkskdfl/"
    },
    {
        "id" : 3,
        "file" : testimagename,
        "text": "Valid Meme"
    },
]

test_id = [(1, True),(2, True),(3, False),(5435345, False),(654645654, False)]
test_file = [(testimagename, True)]
test_text = [("ValidMeme", True), ("1"*88, False), ("!rewtnsilg/-", True)]

def is_valid(*argv):
    ret = True
    for tup in argv:
        ret = ret and tup[1]
    return ret

@pytest.mark.parametrize('text', test_text)
@pytest.mark.parametrize('file', test_file)
def test_add_meme(file, text):
    expected = is_valid(file, text)
    file = file[0]
    text = text[0]
    with open(file, 'rb') as f:
        response = client.post('/memes', files={'file' : f}, data={'text' : text})
        print(response)
        result = response.status_code == 201
        assert result == expected
        #assert response.status_code == 201

def test_list_memes():
    response = client.get('/memes')
    print(response)
    assert response.status_code == 200

@pytest.mark.parametrize('id', test_id)
def test_list_meme_by_id(id):
    expected = is_valid(id)
    id = id[0]
    response = client.get(f'/memes/{id}')
    print(response)
    result = response.status_code == 200
    assert result == expected
    #assert response.status_code == 200

@pytest.mark.parametrize('id', test_id)
@pytest.mark.parametrize('text', test_text)
@pytest.mark.parametrize('file', test_file)
def test_update_meme_by_id(id, file, text):
    expected = is_valid(id, file, text)
    id = id[0]
    file = file[0]
    text = text[0]
    with open(file, 'rb') as f:
        response = client.put(f'/memes/{id}', files={'new_file' : f}, data={'text' : text})
    print(response)
    result = response.status_code == 201
    assert result == expected
    #assert response.status_code == 201

@pytest.mark.parametrize('id', test_id)
def test_delete_meme_by_id(id):
    expected = is_valid(id)
    id = id[0]
    response = client.delete(f'/memes/{id}')
    print(response)
    result = response.status_code == 204
    assert result == expected
    #assert response.status_code == 204
