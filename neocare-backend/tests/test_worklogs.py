"""Pruebas de registro de horas trabajadas: validación, permisos y agregación"""
from datetime import datetime, timedelta, timezone
from tests.conftest import register_and_login

def _setup_card(client, headers):
    board=client.post("/api/v1/boards/", json={"title": "Test"}, headers=headers).json()
    lst=client.post("/api/v1/lists/", json={"title": "Pendiente", "board_id":board["id"], "order":0}, headers=headers).json()
    card=client.post("/api/v1/cards/", json={"title":"Test tarea", "list_id":lst["id"], "order":0}, headers=headers).json()
    return card["id"]

def test_create_worklog(client):
    headers=register_and_login(client)
    card_id=_setup_card(client, headers)

    res=client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":2.5,"date":datetime.now(timezone.utc).isoformat(),"note":"Avance inicial",
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["hours"] == 2.5


def test_create_worklog_below_minimum_forbidden(client):
    """El mínimo son 0.25h (15min), válido tanto en Pydantic como en el endpoint(FastAPI)"""
    headers=register_and_login(client)
    card_id=_setup_card(client, headers)

    res=client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":0.1,"date":datetime.now(timezone.utc).isoformat(),
    }, headers=headers)
    assert res.status_code == 422
    #rechazado por el schema de Pydantic (field(ge=0.25))
    #los datos mandados no son correctos en valor/formato

def test_create_worklog_failure_future_date(client):
    headers=register_and_login(client)
    card_id=_setup_card(client, headers)
    future_date=(datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

    res=client.post("/api/v1/worklogs/", json={"card_id":card_id, "hours":1, "date":future_date}, headers=headers)
    assert res.status_code == 422

def test_create_worklog_long_note_fails(client):
    headers=register_and_login(client)
    card_id=_setup_card(client, headers)

    res=client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":1,"date":datetime.now(timezone.utc).isoformat(), "note": "x" * 201, #límite 200
    }, headers=headers)
    assert res.status_code == 422

def test_auth_user_log_hours(client):
    """En el tablero compartido, cualquier usuario autenticado puede registrar horas en cualquier tarjeta"""
    julia_headers=register_and_login(client, email="julia@neocare.com")
    carlos_headers=register_and_login(client, email="carlos@neocare.com")
    card_id=_setup_card(client, julia_headers)

    res=client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":1.5,"date":datetime.now(timezone.utc).isoformat(),
    }, headers=carlos_headers)
    assert res.status_code == 201

def test_user_edit_own_worklog(client):
    julia_headers=register_and_login(client, email="julia@neocare.com")
    carlos_headers=register_and_login(client, email="carlos@neocare.com")
    card_id=_setup_card(client, julia_headers)

    log = client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":2,"date":datetime.now(timezone.utc).isoformat(),
    }, headers=julia_headers).json()

    res=client.put(f"/api/v1/worklogs/{log['id']}", json={"hours":5}, headers=carlos_headers)
    assert res.status_code == 404 
    #se filtra por user_id, plq no existe wl para carlos

def test_update_note_changes_doesnt_erase_hours(client):
    """Actualizar la nota no debe borrar las horas"""
    headers =register_and_login(client)
    card_id=_setup_card(client, headers)
    log=client.post("/api/v1/worklogs/", json={
        "card_id":card_id,"hours":3,"date":datetime.now(timezone.utc).isoformat(),
    }, headers=headers).json()

    res=client.put(f"/api/v1/worklogs/{log['id']}", json={"note":"Sólo cambio la nota"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["hours"] == 3 #debe mantenerse en 3, no cambiar a None o 0

def test_card_total_hours_all_users(client):
    """Se debe sumar el total de horas de TODOS los usuarios en "card.total_hours"""
    julia_headers=register_and_login(client,email="julia3@neocare.com")
    carlos_headers=register_and_login(client, email="carlos3@neocare.com")
    card_id=_setup_card(client, julia_headers)

    client.post("/api/v1/worklogs/", json={"card_id":card_id,"hours":2,"date":datetime.now(timezone.utc).isoformat()}, headers=julia_headers)
    client.post("/api/v1/worklogs/", json={"card_id":card_id,"hours":1.5,"date":datetime.now(timezone.utc).isoformat()}, headers=carlos_headers)

    card=client.get(f"/api/v1/cards/{card_id}", headers=julia_headers).json()
    assert card["total_hours"] == 3.5
    assert len(card["hours_per_user"]) == 2

def test_worklogs_card_own_entries(client):
    """Cada usuario ve las horas de todo el tablero"""
    julia_headers=register_and_login(client, email="julia4@neocare.com")
    carlos_headers=register_and_login(client, email="carlos4@neocare.com")
    card_id=_setup_card(client, julia_headers)

    client.post("/api/v1/worklogs/", json={"card_id":card_id,"hours":2,"date":datetime.now(timezone.utc).isoformat()}, headers=carlos_headers)

    #print("Post status:", res.status_code)
    #print("Post body:", res.json())

    julia_view=client.get(f"/api/v1/cards/{card_id}", headers=julia_headers).json()

    #print("GET BODY:", julia_view)

    #assert len(julia_view) ==1
    #assert julia_view[0]["hours"] == 2
    assert len(julia_view["hours_per_user"]) == 1
    assert julia_view["hours_per_user"][0]["user_email"] == "carlos4@neocare.com"
    assert julia_view["hours_per_user"][0]["total_hours"] == 2    