
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Obtiene UF, IVP, IPC, UTM, USD->CLP y EUR->CLP desde mindicador.cl,
entregando un JSON simple con:
- valor
- unidad: "Pesos chilenos"
- fecha: "DD-MM-YYYY"

Requiere: requests
    pip install requests
"""

import json
import datetime as dt
import requests

BASE = "https://mindicador.cl/api"
HEADERS = {"Accept": "application/json", "User-Agent": "indicadores-simple/1.0"}
TIMEOUT = 10

INDICADORES = {
    "uf": "UF",
    "ivp": "IVP",
    "ipc": "IPC",
    "utm": "UTM",
    "dolar": "USD_CLP",
    "euro": "EUR_CLP",
}


def _get(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise RuntimeError(f"Error consultando {url}: {e}")


def _parse_fecha_iso(iso: str) -> str:
    """
    Convierte 'YYYY-MM-DDTHH:MM:SS.mmmZ' a 'DD-MM-YYYY'.
    """
    # Ejemplos de mindicador: 2025-12-06T03:00:00.000Z
    dtobj = dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
    return dtobj.strftime("%d-%m-%Y")


def _extraer_ultimo(data: dict):
    """
    De una respuesta de mindicador, toma el último valor disponible.
    - Si viene "serie": usa el primer elemento (más reciente).
    - Si viene "valor"/"fecha": usa esos directamente.
    Devuelve (valor, fecha_dd_mm_yyyy).
    """
    if isinstance(data.get("serie"), list) and data["serie"]:
        latest = data["serie"][0]
        valor = latest.get("valor")
        fecha = latest.get("fecha")
        fecha_fmt = _parse_fecha_iso(fecha)
        return valor, fecha_fmt

    # Algunas rutas pueden devolver un objeto con "valor" y "fecha"
    if "valor" in data and "fecha" in data:
        valor = data["valor"]
        fecha_fmt = _parse_fecha_iso(data["fecha"])
        return valor, fecha_fmt

    raise ValueError("Formato de respuesta no reconocido")


def obtener_indicadores() -> dict:
    resultados = {}
    for code, etiqueta in INDICADORES.items():
        url = f"{BASE}/{code}"
        data = _get(url)
        valor, fecha = _extraer_ultimo(data)

        resultados[etiqueta] = {
            "valor": valor,
            "unidad": "Pesos chilenos",
            "fecha": fecha,
        }

    salida = {
        "fecha_consulta": dt.datetime.now().strftime("%d-%m-%Y"),
        "indicadores": resultados,
    }
    return salida


def main():
    datos = obtener_indicadores()
    print(json.dumps(datos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
