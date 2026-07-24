'''Test de login y protección de rutas privadas'''
from tests.conftest import register_and_login

#client busca el fixture en conftest con esta función y la ejecuta
def test_register_user(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "test@neocare.com", "password":"password123", "full_name":"Usuario Test",
    })

    #evalúa una condición lógica -> verdadera continua, falsa detiene ejecución script
    assert res.status_code == 201
    assert "id" in res.json()
    #la contraseña no se devuele (ni cifrada) NUNCA
    assert "password" not in res.json()
    assert "hashed_password" not in res.json()

def test_register_duplicate(client):
    client.post("/api/v1/auth/register", json={
        "email": "dup@neocare.com", "password":"password123", "full_name":"Usuario Duplicado A",
    })
    res = client.post("/api/v1/auth/register", json={
        "email": "dup@neocare.com", "password":"different23", "full_name":"Usuario Duplicado B",
    })
    assert res.status_code == 400

def test_login_correct_credentials_token(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@neocare.com", "password":"password123", "full_name":"Test Login",
    })
    res = client.post(
        "/api/v1/auth/login", 
        data={"username": "login@neocare.com", "password":"password123"},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
    )
    
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={
        "email": "wrongpass@neocare.com", "password":"different23", "full_name":"Contraseña Equivocada A",
    })
    res = client.post(
        "/api/v1/auth/login", 
        data={"username": "wrongpass@neocare.com", "password":"incorrecta"},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
    )
    assert res.status_code == 401

def test_protected_route_valid_token_rejected(client):
    res=client.get("/api/v1/users/me")
    assert res.status_code == 401

def test_protected_route_invalid_token_rejected(client):
    #esta prueba tiene que fallar por meter mal la contraseña
    res = client.get("/api/v1/users/me", headers={"Authorization":"Bearer invalid_token"})
    assert res.status_code == 401

def test_protected_route_valid_token_works(client):
    headers = register_and_login(client, email="protected@neocare.com")
    res=client.get("/api/v1/users/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "protected@neocare.com"

def test_password_stored_string(client, db_session):
    """Aunque llegue un número al JSON, este se guarda y valida como texto"""
    res = client.post("/api/v1/auth/register", json={
        "email":"numeric@neocare.com", "password":12345678, "full_name":"Contraseña numérica",
    })
    assert res.status_code == 201
    from app.models.models import User
    user = db_session.query(User).filter(User.email == "numeric@neocare.com").first()
    assert isinstance(user.hashed_password, str)
    #pide los datos tanto al fixture client como a db_session para comprobar qué quedó guardado de verdad