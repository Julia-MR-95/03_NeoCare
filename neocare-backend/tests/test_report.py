"""Pruebas de los informes: horas por tarjeta y horas por usuario"""
from datetime import datetime, timezone
from tests.conftest import register_and_login

def _setup_board_two_cards(client, headers): #función de uso interno
    board = client.post("/api/v1/boards/", json={"title":"Tablero"}, headers=headers).json()
    lst=client.post("/api/v1/lists/", json={"title":"Pendiente","board_id":board["id"], "order":0}, headers=headers).json()
    card1=client.post("/api/v1/cards", json={"title":"Tarea 1","list_id":lst["id"],"order":0}, headers=headers).json()
    card2=client.post("/api/v1/cards", json={"title":"Tarea 2","list_id":lst["id"],"order":1}, headers=headers).json()
    return board["id"], card1["id"], card2["id"]

def test_hours_by_card_report(client):
    headers=register_and_login(client, email="reportes1@neocare.com")
    board_id, card1, card2 = _setup_board_two_cards(client, headers)

    client.post("/api/v1/worklogs/", json={"card_id":card1, "hours":3,"date":datetime.now(timezone.utc).isoformat}, headers=headers)
    client.post("/api/v1/worklogs/", json={"card_id":card2, "hours":1,"date":datetime.now(timezone.utc).isoformat}, headers=headers)

    res=client.get(f"/api/v1/reports/board/{board_id}/hours-by-card", headers=headers)
    assert res.status_code == 200
    data={row["card_id"]:row["total_hours"] for row in res.json()} #dicc indexado por horas
    assert data[card1]== 3
    assert data[card2]==1

def test_hours_by_user_report(client):
    julia_headers=register_and_login(client, email="reportes2@neocare.com")
    carlos_headers=register_and_login(client, email="reportes3@neocare.com")
    board_id, card1, _ = _setup_board_two_cards(client, julia_headers)

    client.post("/api/v1/worklogs/", json={"card_id":card1,"hours":4,"date":datetime.now(timezone.utc).isoformat()}, headers=carlos_headers)

    res=client.get(f"/api/v1/reports/board/{board_id}/hours-by-user", headers=julia_headers)
    assert res.status_code == 200
    totals={row["user_email"]:row["total_hours"] for row in res.json()} #dicc indexado por mail
    assert totals["reportes2@neocare.com"]==2
    assert totals["reportes3@neocare.com"]==4

def test_any_auth_user_views_board_reports(client):
    "Cualquier usuario autenticado puede ver los informes del tablero compartido"
    owner_headers=register_and_login(client, email="dueno@neocare.com")
    other_headers=register_and_login(client, email="invitado@neocare.com")
    board_id, _, _ = _setup_board_two_cards(client, owner_headers)

    res=client.get(f"/api/v1/reports/board/{board_id}/hours-by-card", headers=other_headers)
    assert res.status_code==200

def test_report_nonexistent_board_404(client):
    headers=register_and_login(client, email="reportes4@neocare.com")
    res=client.get("/api/v1/reports/board/99999/hours-by-card", headers=headers)

    assert res.status_code==404