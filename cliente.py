import requests
import os
from datetime import date

BASE = "http://127.0.0.1:8000/api/clientes"
HEADERS = {"X-API-KEY": "UNICA-2026"}

nuevo = {
    "nombre": "Ana Torres",
    "email": "ana@tecnova.com",
    "estado": "ACTIVO",
    "fechaRegistro": str(date.today())
}

r = requests.post(BASE, json=nuevo, headers=HEADERS)
print("POST:", r.status_code, r.json())

r = requests.get(BASE, headers=HEADERS)
print("GET LIST:", r.status_code, r.json())
