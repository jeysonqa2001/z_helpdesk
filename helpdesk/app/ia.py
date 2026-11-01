import requests
from flask import current_app


def consultar_ia(prompt: str) -> str:
    cfg = current_app.config
    modelo = cfg.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    r = requests.post(
        url,
        headers={"x-goog-api-key": cfg["GEMINI_API_KEY"]},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def analizar_ticket(ticket) -> str:
    prompt = f"""Eres un analista de mesa de ayuda. Del siguiente ticket entrega:
1) Resumen (1 línea)  2) Sentimiento del usuario  3) Prioridad sugerida (Baja/Media/Alta/Crítica)
4) Respuesta sugerida para el cliente.

Título: {ticket.titulo}
Descripción: {ticket.descripcion}"""
    return consultar_ia(prompt)