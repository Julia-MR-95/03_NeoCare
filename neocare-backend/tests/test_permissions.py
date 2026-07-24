"""Pruebas del modelo de tablero compartido y del cálculo automático de horas"""
from tests.conftest import register_and_login

def test_shared_board_visible(client):
    """Todos los usuarios deben ver el mismo tablero,  no uno propio vacío"""
    julia_headers=register_and_login(client, email="julia5@neocare.com")
    client.post("/api/v1/boards/", json={"title":"Tablero de J"}, headers=julia_headers)

    carlos_headers=register_and_login(client, email="carlos5@neocare.com")
    res=client.get("/api/v1/boards", headers=carlos_headers)
    assert res.status_code==200
    titles=[b["title"] for b in res.json()]
    assert "Tablero de J" in titles

def test_users_list_doesnt_leak_hashed_password(client):
    "GET /users/ no debe filtrar las contraseñas hasheadas"
    headers=register_and_login(client, email="privacidad@neocare.com")
    res=client.get("/api/v1/users/", headers=headers)
    assert res.status_code==200
    for user in res.json():
        assert "hashed_password" not in user
        assert "password" not in user

def test_moving_card_completed_automatic_worklog(client):
    """Se calcula el tiempo de forma automática al mover una tarjeta a la columna 'Completado'"""
    headers=register_and_login(client, email="autohoras@neocare.com")
    board=client.post("/api/v1/boards", json={"title":"T"}, headers=headers).json()
    pendiente=client.post("/api/v1/lists/", json={"title": "Pendiente","board_id":board["id"],"order":0}, headers=headers).json()
    completado=client.post("/api/v1/lists/", json={"title": "Completado","board_id":board["id"],"order":1}, headers=headers).json()

    card=client.post("/api/v1/cards/", json={"title":"Tarea rápida test","list_id":pendiente["id"],"order":0}, headers=headers).json()

    res=client.patch(f"/api/v1/cards/{card['id']}/move", json={"list_id":completado['id'],"order":0}, headers=headers)
    assert res.status_code==200
    assert res.json()["completed_at"] is not None

    logs=client.get("/api/v1/worklogs/cards/{card['id']}", headers=headers).json()
    automatic_logs=[l for l in logs if l["is_automatic"]]
    #recorre logs y se queda solo c/lq cumplen la condicion l["is_automatic"]=True
    assert len(automatic_logs)==1
    assert automatic_logs[0]["hours"]>=0.25 #mínimo de 0.25h aunque hayan pasado segundos

def test_removing_card_completed_removes_automatic_worklog(client):
    """Si se saca la tarjeta de Completado, el registro automático de horas debe desaparecer"""
    headers= register_and_login(client, email="autohoras2@neocare.com")
    board=client.post("/api/v1/boards", json={"title":"T"}, headers=headers).json()
    pendiente=client.post("/api/v1/lists/", json={"title": "Pendiente","board_id":board["id"],"order":0}, headers=headers).json()
    completado=client.post("/api/v1/lists/", json={"title": "Completado","board_id":board["id"],"order":1}, headers=headers).json()

    #la metemos en Completado
    card=client.post("/api/v1/cards/", json={"title":"Salida Completado", "list_id":pendiente['id'],"order":0}, headers=headers).json()
    client.patch(f"/api/v1/worklogs/card/{card['id']}/move", json={"list_id":completado['id'], "order":0}, headers=headers)
    #la sacamos de Completado
    res=client.patch(f"/api/v1/worklogs/card/{card['id']}/move", json={"list_id":pendiente['id'],"order":0}, headers=headers)
    assert res.json()["completed_at"] is None

    logs=client.get(f"/api/v1/worklogs/card/{card['id']}", headers=headers).json()
    assert len([l for l in logs if l["is_automstic"]])==0