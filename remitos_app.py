# -*- coding: utf-8 -*-
"""
🍽️ EL BODEGÓN — Sistema de Remitos de Viandas
===============================================
✅ SIN Google — Guarda en JSON y lo sube a GitHub automáticamente
✅ Botón BORRAR que actualiza el archivo en GitHub
✅ Buscador de remitos
✅ Fecha y HORA automáticas
✅ Fondo oscuro / PDF / WhatsApp
✅ ✅ ESTILO CORREGIDO ✅ ✅
"""

# ==================================================
# 🎨 CONFIGURACIÓN — MODIFICÁ LO QUE NECESITÉS
# ==================================================
NOMBRE_NEGOCIO = "EL BODEGÓN"
TITULO_APP = "🍽️ Remitos - El Bodegón"
SUBTITULO = "Sistema de Entrega de Viandas"

# Colores — Fondo oscuro
COLOR_FONDO = "#121212"
COLOR_TEXTO = "#E0E0E0"
COLOR_ACENTO = "#4CAF50"
COLOR_CAJAS = "#1E1E1E"

# Configuración GitHub
USUARIO_GITHUB = "remitosbodegon"
REPO_GITHUB = "mis-remitos"
ENLACE_BASE = f"https://{USUARIO_GITHUB}.github.io/{REPO_GITHUB}"

# ==================================================
# 📦 LIBRERÍAS
# ==================================================
import streamlit as st
import json
import os
import base64
import requests
from datetime import datetime
from fpdf import FPDF

# ==================================================
# 🎨 ESTILO DE LA APP — PRIMERO DE TODO ✅
# ==================================================
st.set_page_config(page_title=TITULO_APP, page_icon="🍽️", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }}
    h1, h2, h3 {{ color: {COLOR_ACENTO}; }}
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div > div {{
        background-color: {COLOR_CAJAS}; color: {COLOR_TEXTO};
    }}
    </style>
""", unsafe_allow_html=True)

st.title(TITULO_APP)
st.subheader(SUBTITULO)

# ==================================================
# 💾 ARCHIVO Y FUNCIONES DE GUARDADO
# ==================================================
ARCHIVO_DATOS = "remitos.json"

def cargar_remitos():
    """Lee los remitos guardados del archivo local"""
    try:
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error leyendo historial: {str(e)[:60]}")
        return []

def subir_archivo_a_github():
    """Sube remitos.json al repositorio para que quede guardado para siempre"""
    try:
        token = st.secrets.get("GITHUB_TOKEN", "")
        if not token:
            return False
        
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            contenido = f.read()
        
        contenido_b64 = base64.b64encode(contenido.encode("utf-8")).decode()
        url = f"https://api.github.com/repos/{USUARIO_GITHUB}/{REPO_GITHUB}/contents/{ARCHIVO_DATOS}"
        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }
        
        resp = requests.get(url, headers=headers)
        sha = resp.json().get("sha") if resp.status_code == 200 else None
        
        datos = {
            "message": "Actualizar historial de remitos",
            "content": contenido_b64,
            "sha": sha
        }
        
        resp = requests.put(url, headers=headers, json=datos)
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"Error subiendo a GitHub: {e}")
        return False

def guardar_remito(datos_remito):
    """Guarda remito nuevo, agrega fecha/hora y lo sube a GitHub"""
    remitos = cargar_remitos()
    ahora = datetime.now()
    datos_remito["fecha_creacion"] = ahora.strftime("%d/%m/%Y")
    datos_remito["hora_creacion"] = ahora.strftime("%H:%M:%S")
    datos_remito["timestamp"] = ahora.strftime("%Y%m%d-%H%M%S")
    remitos.append(datos_remito)
    remitos = sorted(remitos, key=lambda x: x["timestamp"], reverse=True)
    
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(remitos, f, ensure_ascii=False, indent=2)
        subir_archivo_a_github()
        return True
    except Exception as e:
        st.error(f"Error guardando: {str(e)[:60]}")
        return False

# ==================================================
# 📄 GENERAR REMITO EN PDF
# ==================================================
def generar_pdf_remito(numero, empresa, direccion, fecha, viandas, observaciones):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, txt="REMITO DE ENTREGA DE VIANDAS", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, txt=NOMBRE_NEGOCIO, ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(40, 8, txt=f"Remito N°: {numero:04d}")
    pdf.cell(0, 8, txt=f"Fecha: {fecha}", ln=True)
    pdf.cell(40, 8, txt=f"Empresa: {empresa}", ln=True)
    pdf.cell(40, 8, txt=f"Dirección: {direccion}", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(100, 8, txt="Detalle de Viandas", border=1)
    pdf.cell(30, 8, txt="Cantidad", border=1, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 11)
    total = 0
    for v in viandas:
        pdf.cell(100, 7, txt=v["nombre"], border=1)
        pdf.cell(30, 7, txt=str(v["cantidad"]), border=1, align="C")
        pdf.ln()
        total += v["cantidad"]
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(100, 8, txt="TOTAL VIANDAS", border=1)
    pdf.cell(30, 8, txt=str(total), border=1, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, txt=f"Observaciones: {observaciones}")
    pdf.ln(15)
    pdf.cell(90, 8, txt="Firma Recibí: _________________________")
    pdf.cell(90, 8, txt=f"Fecha: {fecha}", ln=True)

    nombre_archivo = f"remito_{numero:04d}.pdf"
    pdf.output(nombre_archivo)
    return nombre_archivo

# ==================================================
# 📤 SUBIR PDF A GITHUB Y OBTENER ENLACE
# ==================================================
def subir_pdf_y_obtener_enlace(nombre_archivo, numero_remito):
    try:
        with open(nombre_archivo, "rb") as f:
            contenido = f.read()
        contenido_b64 = base64.b64encode(contenido).decode()

        token = st.secrets.get("GITHUB_TOKEN", "")
        if not token:
            return f"{ENLACE_BASE}/{nombre_archivo}"

        url = f"https://api.github.com/repos/{USUARIO_GITHUB}/{REPO_GITHUB}/contents/{nombre_archivo}"
        headers = {
            "Authorization": f"token {token}",
            "Content-Type": "application/json"
        }
        respuesta = requests.get(url, headers=headers)
        sha = respuesta.json().get("sha") if respuesta.status_code == 200 else None

        datos = {
            "message": f"Agregar remito N° {numero_remito:04d}",
            "content": contenido_b64,
            "sha": sha
        }
        respuesta = requests.put(url, headers=headers, json=datos)
        return f"{ENLACE_BASE}/{nombre_archivo}"
    except Exception as e:
        return f"{ENLACE_BASE}/{nombre_archivo}"

# ==================================================
# 📱 PESTAÑAS: Generar Remito / Historial
# ==================================================
pantalla = st.radio("", ["📝 Generar Remito", "📋 Historial de Remitos"])

# ──────────────────────────────────────────────────
# PANTALLA 1: GENERAR REMITO
# ──────────────────────────────────────────────────
if pantalla == "📝 Generar Remito":
    st.header("📝 Generar Nuevo Remito")

    remitos_guardados = cargar_remitos()
    ultimo_numero = max([r.get("numero", 0) for r in remitos_guardados], default=0)
    numero_remito = ultimo_numero + 1

    st.info(f"✅ Remito N°: {numero_remito:04d}")

    empresa = st.text_input("Nombre de la Empresa / Cliente")
    direccion_entrega = st.text_input("Dirección de Entrega")
    fecha_remito = st.date_input("Fecha del Remito", value=datetime.now())
    fecha_str = fecha_remito.strftime("%d/%m/%Y")

    st.subheader("📦 Viandas a Entregar")
    cantidad_tipos = st.number_input("Cantidad de tipos de viandas", min_value=1, max_value=10, value=1)
    viandas = []
    for i in range(int(cantidad_tipos)):
        cols = st.columns([3, 1])
        nombre = cols[0].text_input(f"Vianda {i+1}", key=f"v_nom_{i}")
        cant = cols[1].number_input("Cantidad", min_value=1, value=1, key=f"v_cnt_{i}")
        if nombre:
            viandas.append({"nombre": nombre, "cantidad": cant})

    observaciones = st.text_area("Observaciones")

    if st.button("✅ GENERAR REMITO", type="primary"):
        if not empresa or not viandas:
            st.error("Completá el nombre de la empresa y al menos una vianda")
        else:
            nombre_pdf = generar_pdf_remito(numero_remito, empresa, direccion_entrega, fecha_str, viandas, observaciones)
            enlace_pdf = subir_pdf_y_obtener_enlace(nombre_pdf, numero_remito)

            mensaje_whatsapp = f"""Hola! Le enviamos el Remito N° {numero_remito:04d} correspondiente a las viandas entregadas el día {fecha_str}.

📄 Ver remito: {enlace_pdf}

Saludos de {NOMBRE_NEGOCIO}"""
            mensaje_codificado = mensaje_whatsapp.replace(" ", "%20").replace("\n", "%0A")
            enlace_whatsapp = f"https://wa.me/?text={mensaje_codificado}"

            datos_remito = {
                "numero": numero_remito,
                "empresa": empresa,
                "direccion_entrega": direccion_entrega,
                "fecha": fecha_str,
                "viandas": viandas,
                "observaciones": observaciones,
                "enlace_pdf": enlace_pdf,
                "enlace_whatsapp": enlace_whatsapp
            }

            if guardar_remito(datos_remito):
                st.success(f"✅ Remito N° {numero_remito:04d} generado y guardado en GitHub!")
                st.markdown(f"📄 [Ver PDF]({enlace_pdf})")
                st.markdown(f"📱 [Enviar por WhatsApp]({enlace_whatsapp})")
            else:
                st.error("No se pudo guardar el remito")

# ──────────────────────────────────────────────────
# PANTALLA 2: HISTORIAL CON BUSCADOR Y BORRAR 🗑️
# ──────────────────────────────────────────────────
else:
    st.header("📋 Historial de Remitos")

    busqueda = st.text_input("🔍 Buscar por empresa, número o fecha...", placeholder="Escribí y buscá en tiempo real")

    remitos = cargar_remitos()

    if not remitos:
        st.info("Todavía no hay remitos guardados. Al generar el primero se creará el archivo remitos.json en GitHub.")
    else:
        if busqueda:
            busq = busqueda.lower()
            remitos = [
                r for r in remitos
                if busq in str(r.get("empresa", "")).lower()
                or busq in str(r.get("numero", "")).lower()
                or busq in str(r.get("fecha_creacion", "")).lower()
            ]

        if not remitos:
            st.warning("No se encontraron remitos con esa búsqueda.")
        else:
            st.info(f"Se encontraron {len(remitos)} remitos")
            
            indices_a_borrar = []
            
            for i, r in enumerate(remitos):
                nro = r.get("numero", "??")
                emp = r.get("empresa", "Sin nombre")
                fch = r.get("fecha_creacion", "??/??/????")
                hor = r.get("hora_creacion", "??:??")

                col1, col2 = st.columns([0.92, 0.08])
                with col1:
                    desplegar = st.expander(f"📋 Remito N° {nro:04d} — {emp} — 📅 {fch} ⏰ {hor}")
                with col2:
                    if st.button("🗑️", key=f"borrar_{i}", help="Borrar este remito"):
                        indices_a_borrar.append(i)
                
                with desplegar:
                    st.write(f"**Empresa:** {emp}")
                    st.write(f"**Dirección:** {r.get('direccion_entrega', '---')}")
                    st.write(f"**Fecha Remito:** {r.get('fecha', fch)}")
                    st.write(f"**Generado el:** {fch} a las {hor}")
                    st.write(f"**Observaciones:** {r.get('observaciones', '---')}")

                    if "viandas" in r:
                        st.write("**Viandas:**")
                        for v in r["viandas"]:
                            st.write(f"- {v['nombre']}: {v['cantidad']}")

                    if r.get("enlace_pdf"):
                        st.markdown(f"📄 [Abrir / Descargar PDF]({r['enlace_pdf']})")
                    if r.get("enlace_whatsapp"):
                        st.markdown(f"📱 [Enviar por WhatsApp]({r['enlace_whatsapp']})")

            # Ejecutar borrado
            if indices_a_borrar:
                todos = cargar_remitos()
                for idx in sorted(indices_a_borrar, reverse=True):
                    todos.pop(idx)
                try:
                    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                        json.dump(todos, f, ensure_ascii=False, indent=2)
                    subir_archivo_a_github()
                    st.success("✅ Remito borrado y actualizado en GitHub! Recargá la página.")
                except Exception as e:
                    st.error(f"❌ No se pudo borrar: {str(e)[:60]}")
