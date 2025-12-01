from fastapi import APIRouter, Depends
from database import get_supabase
import re
from collections import Counter

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ==================================================
# 1) KPIs del dashboard (el front YA los carga)
# ==================================================
@router.get("/stats/")
def get_dashboard_stats():
    return {
        "total_projects": 12,
        "available_units": 54,
        "sold_units": 33,
        "total_zones": 7
    }


# ==================================================
# 2) MENSAJES POR DÍA — EL FRONT LO LLAMA DIRECTO
# ==================================================
@router.get("/whatsapp/daily/")
def get_daily_whatsapp_stats(conn=Depends(get_supabase)):
    rows = conn("historial_conversaciones_diarias")

    contador = {}
    for row in rows:
        fecha = row.get("fecha")
        if fecha:
            contador[fecha] = contador.get(fecha, 0) + 1

    return [
        {"fecha": fecha, "total": total}
        for fecha, total in sorted(contador.items())
    ]


# ==================================================
# 3) MENSAJES POR USUARIO — EL FRONT LO USARÁ PARA GRAFICA
# ==================================================
@router.get("/whatsapp/by-user/")
def get_messages_by_user(conn=Depends(get_supabase)):
    rows = conn("historial_conversaciones_diarias")

    contador = {}
    for row in rows:
        usuario = row.get("nombreusuario") or row.get("idusuario")
        if usuario:
            contador[usuario] = contador.get(usuario, 0) + 1

    return [
        {"usuario": usuario, "total": total}
        for usuario, total in sorted(contador.items(), key=lambda x: -x[1])
    ]


# ==================================================
# 4) PREGUNTAS/PALABRAS MÁS FRECUENTES
# ==================================================
@router.get("/whatsapp/faq/")
def get_faq_from_messages(conn=Depends(get_supabase), top: int = 15):

    rows = conn("historial_conversaciones_diarias")

    texto_total = ""
    for row in rows:
        contenido = row.get("historial_conversacion", "")
        if contenido:
            texto_total += " " + contenido.lower()

    texto_total = re.sub(r"[^a-zA-Z0-9áéíóúñü ]", " ", texto_total)
    palabras = texto_total.split()

    stopwords = {
        "hola","buenas","gracias","por","favor","ok","si","de","la","el","y","a","en",
        "que","se","lo","me","es","un","una","para","tu","mi","los","las","del"
    }

    palabras_filtradas = [p for p in palabras if p not in stopwords and len(p) > 3]

    conteo = Counter(palabras_filtradas)

    return [
        {"palabra": palabra, "total": total}
        for palabra, total in conteo.most_common(top)
    ]


# ==================================================
# 5) ÚLTIMOS MENSAJES — PARA TABLA
# ==================================================
@router.get("/whatsapp/last/")
def get_last_messages(conn=Depends(get_supabase), limit: int = 20):
    rows = conn("historial_conversaciones_diarias")

    rows_sorted = sorted(
        rows,
        key=lambda x: x.get("fecha_creacion") or "",
        reverse=True
    )

    return rows_sorted[:limit]
