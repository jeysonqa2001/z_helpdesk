import requests
from flask import current_app

SISTEMA_BASE = (
    "Eres un analista de mesa de ayuda. Respondes siempre en español, "
    "de forma breve, clara y profesional."
)

SISTEMA_CHAT = (
    "Eres el asistente de soporte técnico de HelpDesk Pro. Ayudas a los técnicos a "
    "diagnosticar problemas, proponer soluciones paso a paso y redactar respuestas "
    "para los solicitantes. Responde siempre en español, de forma breve y práctica. "
    "Si te dan datos de tickets, úsalos; si no tienes información suficiente, dilo "
    "y pide el dato que falta. No inventes números de ticket."
)


def _llamar(mensajes, max_tokens=2000, temperature=0.3) -> str:
    cfg = current_app.config
    clave = cfg.get("AI_API_KEY")
    if not clave or clave == "TU_KEY":
        raise RuntimeError("Falta configurar AI_API_KEY en el archivo .env")

    base = cfg.get("AI_URL", "https://api.groq.com/openai/v1").rstrip("/")
    r = requests.post(
        f"{base}/chat/completions",
        headers={
            "Authorization": f"Bearer {clave}",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg.get("AI_MODEL", "openai/gpt-oss-20b"),
            "messages": mensajes,
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=60,
    )

    if r.status_code != 200:
        try:
            detalle = r.json()["error"]["message"]
        except Exception:
            detalle = r.text[:200]
        raise RuntimeError(f"La IA respondió {r.status_code}: {detalle}")

    try:
        texto = r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError("La IA no devolvió texto. Intenta de nuevo.")

    if not texto or not texto.strip():
        raise RuntimeError("La IA devolvió una respuesta vacía. Intenta de nuevo.")
    return texto.strip()


def consultar_ia(prompt: str) -> str:
    return _llamar([
        {"role": "system", "content": SISTEMA_BASE},
        {"role": "user", "content": prompt},
    ])


def chat_ia(historial, contexto: str = "") -> str:
    """historial: lista de {'role': 'user'|'assistant', 'content': str}"""
    sistema = SISTEMA_CHAT
    if contexto:
        sistema += "\n\nDATOS ACTUALES DEL SISTEMA:\n" + contexto
    return _llamar([{"role": "system", "content": sistema}] + historial,
                   max_tokens=2500, temperature=0.4)


def analizar_ticket(ticket) -> str:
    prompt = f"""Analiza este ticket de soporte y responde con estas 4 secciones:

1) Resumen (1 línea)
2) Sentimiento del usuario
3) Prioridad sugerida (Baja/Media/Alta/Crítica) y por qué
4) Respuesta sugerida para el solicitante

Título: {ticket.titulo}
Descripción: {ticket.descripcion}
Categoría: {ticket.categoria}
Prioridad actual: {ticket.prioridad}
Estado: {ticket.estado}"""
    return consultar_ia(prompt)