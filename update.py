#!/usr/bin/env python3
"""
update_typeform.py – Crear o actualizar un formulario en Typeform a partir de un fichero JSON.

Uso básico:
    python update_typeform.py --token TU_TOKEN --json wineclub-es.json           # crea nuevo formulario
    python update_typeform.py --token TU_TOKEN --json wineclub-es.json --form-id abCdEf   # actualiza formulario existente

Variables de entorno opcionales:
    TYPEFORM_TOKEN     – se usa si no pasas --token
    TYPEFORM_FORM_ID   – se usa si no pasas --form-id (en modo actualización)

Requisitos:
    pip install requests

Notas:
  * Si no facilitas --form-id, el script hará un POST y mostrará el ID creado.
  * Con --form-id realiza un PUT que reemplaza todo el contenido del formulario (full update).
  * Maneja errores de red y de API con mensajes claros.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

API_BASE = "https://api.typeform.com"


def load_json(path: Path):
    if not path.exists():
        sys.exit(f"[ERROR] El fichero JSON '{path}' no existe.")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        sys.exit(f"[ERROR] JSON inválido en '{path}': {e}")


def request_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def create_form(token: str, payload: dict):
    url = f"{API_BASE}/forms"
    resp = requests.post(url, headers=request_headers(token), json=payload, timeout=20)
    handle_response(resp, expect_status=201)
    form_id = resp.json().get("id")
    print(f"[OK] Formulario creado con ID: {form_id}")
    return form_id


def update_form(token: str, form_id: str, payload: dict):
    url = f"{API_BASE}/forms/{form_id}"
    resp = requests.put(url, headers=request_headers(token), json=payload, timeout=20)
    handle_response(resp, expect_status=200)
    print(f"[OK] Formulario {form_id} actualizado correctamente.")


def handle_response(resp: requests.Response, expect_status: int):
    if resp.status_code != expect_status:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        sys.exit(
            f"[ERROR] API devolvió {resp.status_code} (esperado {expect_status}).\n\nDetalles: {detail}"
        )


def parse_args():
    p = argparse.ArgumentParser(
        description="Crear o actualizar un formulario en Typeform a partir de un JSON",
    )
    p.add_argument("--json", required=True, type=Path, help="Ruta al fichero JSON del formulario")
    p.add_argument("--token", help="Personal Access Token de Typeform (o variable TYPEFORM_TOKEN)")
    p.add_argument(
        "--form-id",
        help="ID del formulario existente a actualizar. Si se omite se creará uno nuevo (POST)",
    )
    return p.parse_args()


def main():
    args = parse_args()

    token = args.token or os.getenv("TYPEFORM_TOKEN")
    if not token:
        sys.exit("[ERROR] Debes proporcionar un --token o la variable de entorno TYPEFORM_TOKEN.")

    form_data = load_json(args.json)

    if args.form_id or os.getenv("TYPEFORM_FORM_ID"):
        form_id = args.form_id or os.getenv("TYPEFORM_FORM_ID")
        update_form(token, form_id, form_data)
    else:
        create_form(token, form_data)


if __name__ == "__main__":
    main()
