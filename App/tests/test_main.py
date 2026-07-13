'''
Archivos para ejecutar tests automaticos en Github
'''

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#Comprender archivos fuente
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()


#Hacer checkeo de salud
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["estado"] == "saludable"

#Testear la falta de contenido
def test_debate_sin_contenido():
    response = client.post("/debate", json={"tipo_entrada": "texto"})
    assert response.status_code == 400

#Debatir sin una url en especifico.
def test_debate_sin_url_rss():
    response = client.post("/debate", json={"tipo_entrada": "rss"})
    assert response.status_code == 400
