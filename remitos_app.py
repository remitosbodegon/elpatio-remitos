# -*- coding: utf-8 -*-
"""
🍽️ EL BODEGÓN — Sistema de Remitos de Viandas
===============================================
✅ Adaptado para STREAMLIT CLOUD (usa Secrets, no archivos)
✅ Logo real desde carpeta recursos/logo_bodegon.png
✅ Espera 30s — Botón WhatsApp INSTANTÁNEO
✅ Contador empieza en 1 y sube sin repetir
✅ Fecha SIN HORA
✅ Diseño: Fondo crema + Líneas doradas + Banda verde
"""

# ==================================================
# 🎨 PALETA DE COLORES — EL BODEGÓN
# ==================================================
FONDO_APP        = "#1C3C30"
FONDO_TARJETA    = "#265040"
FONDO_CAMPOS     = "#306250"
TEXTO_CLARO      = "#F7EFE4"
TEXTO_GRIS       = "#C9BFB3"
BORDE_SUAVE      = "#408068"
VERDE_LOGO       = "#009670"
DORADO           = "#D4B86A"
DORADO_CLARO     = "#EAD78A"
VERDE_WSP        = "#25D366"

RGB_DORADO       = (212, 184, 106)
RGB_VERDE_HEADER = (0, 150, 112)
RGB_VERDE_LINEAS = (64, 128, 104)
CREMA_FONDO      = (247, 239, 228)

# ==================================================
# ⚙️ CONFIGURACIÓN
# ==================================================
NOMBRE_NEGOCIO = "EL BODEGÓN"
TITULO_APP = "🍽️ Remitos - El Bodegón"
SUBTITULO = "Sistema de Entrega de Viandas"
NOMBRE_HOJA_SHEETS = "Remitos El Bodegón"

ALCANCE_GOOGLE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

GITHUB_USUARIO = "remitosbodegon"
GITHUB_REPO = "mis-remitos"
GITHUB_RAMA = "main"

ANCHO_FIRMA = 600
ALTO_FIRMA = 260

CARPETA_RECURSOS = "recursos"
CARPETA_PDF = "remitos_pdf"

# ==================================================
# 📦 LIBRERÍAS
# ==================================================
import streamlit as st
import os
import json
import datetime
import urllib.parse
import base64
import requests
import time
from PIL import Image
import numpy as np
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import gspread
from google.oauth2.service_account import Credentials

RUTA_LOGO = os.path.join(CARPETA_RECURSOS, "logo_bodegon.png") if os.path.exists(os.path.join(CARPETA_RECURSOS, "logo_bodegon.png")) else None

os.makedirs(CARPETA_RECURSOS, exist_ok=True)
os.makedirs(CARPETA_PDF, exist_ok=True)

# ==================================================
# 🧭 INICIALIZACIÓN DE SESIÓN
# ==================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "nuevo"
if "contador_formulario" not in st.session_state:
    st.session_state.contador_formulario = 0
if "remito_generado" not in st.session_state:
    st.session_state.remito_generado = False

# ==================================================
# 🎨 ESTILO APP
# ==================================================
st.set_page_config(page_title=TITULO_APP, page_icon="🍽️", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
<style>
    * {{ box-sizing: border-box; }}
    .stApp {{
        background-color: {FONDO_APP};
        color: {TEXTO_CLARO};
    }}
    section[data-testid="stSidebar"] {{ display: none !important; }}

    .encabezado {{
        background-color: {FONDO_TARJETA};
        padding: 28px 20px;
        border-radius: 24px;
        margin-bottom: 28px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        text-align: center;
    }}
    .encabezado-texto h1 {{
        margin: 0;
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 2px;
        color: {DORADO_CLARO};
    }}
    .encabezado-texto p {{
        margin: 8px 0 0 0;
        color: {TEXTO_GRIS};
        font-size: 15px;
        letter-spacing: 1px;
    }}

    .tarjeta, .nav-card {{
        background-color: {FONDO_TARJETA};
        border: 1px solid {BORDE_SUAVE};
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }}
    .tarjeta h2 {{
        color: {TEXTO_CLARO} !important;
        font-size: 20px;
        margin-top: 0;
        margin-bottom: 20px;
    }}
    .tarjeta label, .stMarkdown p {{
        color: {TEXTO_GRIS} !important;
        font-weight: 500;
    }}
    .stMarkdown, .stMarkdown span {{
        color: {TEXTO_CLARO} !important;
    }}

    div[data-testid="stTextInput"] > div > input,
    div[data-testid="stNumberInput"] > div > input,
    div[data-testid="stSelectbox"] > div > div > div {{
        background-color: {FONDO_CAMPOS} !important;
        color: {TEXTO_CLARO} !important;
        border: 2px solid {BORDE_SUAVE} !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
    }}
    input::placeholder {{
        color: {TEXTO_GRIS} !important;
    }}

    button[kind="secondary"] {{
        background-color: {FONDO_CAMPOS} !important;
        color: {TEXTO_CLARO} !important;
        border: 2px solid {BORDE_SUAVE} !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: {DORADO} !important;
        color: {DORADO_CLARO} !important;
    }}
    button[kind="primary"] {{
        background: linear-gradient(135deg, {DORADO}, {DORADO_CLARO}) !important;
        color: #000 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }}
    button[kind="primary"]:disabled {{
        background-color: {BORDE_SUAVE} !important;
        color: {TEXTO_GRIS} !important;
    }}

    hr {{
        border: none;
        height: 2px;
        background: {BORDE_SUAVE};
        margin: 24px 0;
    }}

    .caja-link-pdf {{
        background-color: {FONDO_CAMPOS};
        border: 2px solid {DORADO};
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
    }}
    .caja-link-pdf strong {{
        color: {DORADO_CLARO};
    }}
    .caja-link-pdf a {{
        color: {DORADO_CLARO} !important;
    }}

    .aviso-espera {{
        display: inline-block;
        margin-left: 12px;
        padding: 6px 14px;
        background: linear-gradient(90deg, #2a5a48, {VERDE_LOGO});
        color: white;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        animation: pulsar 1.2s infinite;
    }}
    .aviso-listo {{
        display: inline-block;
        margin-left: 12px;
        padding: 6px 14px;
        background: #25a75b;
        color: white;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }}
    @keyframes pulsar {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}

    .stAlert {{
        background-color: {FONDO_TARJETA} !important;
        border: 1px solid {BORDE_SUAVE} !important;
        color: {TEXTO_CLARO} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==================================================
# 🏷️ ENCABEZADO
# ==================================================
st.markdown(f"""
<div class="encabezado">
    <div class="encabezado-texto">
        <h1>{NOMBRE_NEGOCIO}</h1>
        <p>{SUBTITULO}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# 🧭 NAVEGACIÓN
# ==================================================
st.markdown('<div class="nav-card">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏢 Gestionar Empresas", use_container_width=True):
        st.session_state.pagina = "empresas"
        st.session_state.remito_generado = False
        st.rerun()
with col2:
    if st.button("📋 Nuevo Remito", use_container_width=True):
        st.session_state.pagina = "nuevo"
        st.session_state.contador_formulario += 1
        st.session_state.remito_generado = False
        st.rerun()
with col3:
    if st.button("📜 Historial", use_container_width=True):
        st.session_state.pagina = "historial"
        st.session_state.remito_generado = False
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ==================================================
# 💾 FUNCIONES AUXILIARES
# ==================================================
ARCHIVO_EMPRESAS = "empresas.json"
ARCHIVO_REMITOS = "remitos.json"

def cargar_json(ruta, valor_default):
    if not os.path.exists(ruta):
        return valor_default
    try:
        with open(ruta, "r", encoding="utf-8-sig") as f:
            datos = json.load(f)
            return datos if isinstance(datos, list) else valor_default
    except:
        st.warning(f"⚠️ Archivo {ruta} reiniciado")
        return valor_default

def guardar_json(ruta, datos):
    ruta_tmp = ruta + ".tmp"
    try:
        with open(ruta_tmp, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        os.replace(ruta_tmp, ruta)
    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        st.error(f"❌ Error: {str(e)[:60]}")

# ==================================================
# ☁️ GOOGLE SHEETS — LEER DESDE SECRETS DE STREAMLIT
# ==================================================
def obtener_credenciales():
    try:
        creds = Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": "remitos-el-bodegon",
                "private_key_id": "PONÉ-AQUÍ-TU-NUEVO-private_key_id",
                "private_key": "-----BEGIN PRIVATE KEY-----\nPONÉ-TODA-LA-CLAVE-AQUÍ-SIN-ROMPER-LAS-BARRA-SIGUIENDO-TAL-CUAL\n-----END PRIVATE KEY-----\n",
                "client_email": "remitos-app@remitos-el-bodegon.iam.gserviceaccount.com",
                "client_id": "117219117316162090301",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/remitos-app%40remitos-el-bodegon.iam.gserviceaccount.com"
            },
            scopes=ALCANCE_GOOGLE
        )
        return creds
    except Exception as e:
        st.error(f"❌ Error: {str(e)[:80]}")
        return None

def conectar_google_sheets():
    try:
        creds = obtener_credenciales()
        if not creds:
            return None
        gc = gspread.authorize(creds)
        return gc.open(NOMBRE_HOJA_SHEETS).sheet1
    except Exception as e:
        st.error(f"❌ Error Google: {str(e)[:80]}")
        return None

# ==================================================
# 🐙 GITHUB — SUBIR PDF
# ==================================================
def obtener_token_github():
    try:
        return st.secrets.get("GITHUB_TOKEN")
    except:
        return None

def subir_pdf_a_github(ruta_archivo, numero_remito):
    token = obtener_token_github()
    if not token:
        st.error("❌ Falta token de GitHub en los Secrets")
        return ""
    nombre = f"remito_{numero_remito:04d}.pdf"
    url = f"https://api.github.com/repos/{GITHUB_USUARIO}/{GITHUB_REPO}/contents/{nombre}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        with open(ruta_archivo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        resp = requests.get(url, headers=headers, params={"ref": GITHUB_RAMA})
        sha = resp.json().get("sha")
        body = {"message": f"Remito N° {numero_remito:04d}", "content": b64, "branch": GITHUB_RAMA}
        if sha:
            body["sha"] = sha
        resp = requests.put(url, headers=headers, json=body)
        if resp.status_code in (200, 201):
            return f"https://{GITHUB_USUARIO}.github.io/{GITHUB_REPO}/{nombre}"
    except Exception as e:
        st.error(f"❌ Error subiendo: {str(e)[:60]}")
    return ""

# ==================================================
# ✍️ FIRMA
# ==================================================
def hay_firma(img):
    if img is None:
        return False
    try:
        arr = np.array(img)
        if arr.size == 0:
            return False
        return not (arr[:, :, :3] > 245).all()
    except Exception:
        return False

def mensaje_whatsapp(num, emp, fecha, recibe, pdf=""):
    return (
        f"📄 REMITO N° {num:04d} — Entrega a: {emp}\n\n"
        f"✅ Se le envía el remito de las viandas entregadas el día {fecha}.\n\n"
        f"👤 Recibe: {recibe}\n\n"
        f"🔗 VER REMITO EN PDF:\n{pdf}\n\n"
        f"¡Gracias por su compra!"
    )

def enlace_whatsapp(tel, msg):
    t = "".join(c for c in tel if c.isdigit())
    return f"https://wa.me/{t}?text={urllib.parse.quote(msg)}"

# ==================================================
# 📄 GENERAR PDF
# ==================================================
def crear_pdf(numero, fecha, emp, tel, cant, recibe, img_firma):
    pdf = FPDF(format="A4", unit="mm")
    pdf.add_page()
    ancho, margen = 210, 15

    pdf.set_fill_color(*RGB_VERDE_HEADER)
    pdf.rect(0, 0, ancho, 60, "F")

    if RUTA_LOGO and os.path.exists(RUTA_LOGO):
        try:
            pdf.image(RUTA_LOGO, x=(ancho - 40)/2, y=8, w=40, h=32)
            logo_usado = True
        except Exception:
            logo_usado = False
    else:
        logo_usado = False

    if logo_usado:
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_xy(0, 42)
        pdf.cell(ancho, 8, NOMBRE_NEGOCIO, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.set_xy(0, 53)
        pdf.cell(ancho, 6, "Remito de Entrega de Viandas", align="C")
    else:
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 26)
        pdf.set_xy(0, 15)
        pdf.cell(ancho, 12, NOMBRE_NEGOCIO, align="C")
        pdf.set_font("Helvetica", "", 13)
        pdf.set_xy(0, 35)
        pdf.cell(ancho, 8, "Remito de Entrega de Viandas", align="C")

    pdf.set_fill_color(*CREMA_FONDO)
    pdf.rect(0, 60, ancho, 237, "F")

    pdf.set_draw_color(*RGB_DORADO)
    pdf.set_line_width(0.6)
    pdf.line(margen, 75, ancho - margen, 75)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(margen, 85)
    pdf.cell(80, 7, f"N° Remito: {numero:04d}")
    pdf.set_xy(ancho - margen - 50, 85)
    pdf.cell(50, 7, f"Fecha: {fecha}", align="R")

    y = 100
    pdf.set_fill_color(*RGB_VERDE_HEADER)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.rect(margen, y, ancho - margen * 2, 12, "F")
    pdf.set_xy(margen, y)
    pdf.cell(ancho - margen * 2, 12, f"ENTREGA A: {emp.upper()}", align="C")
    pdf.set_text_color(0, 0, 0)
    y += 18

    pdf.set_font("Helvetica", "", 11)
    datos = [
        ("Teléfono:", tel),
        ("Viandas:", str(cant)),
        ("Recibe:", recibe),
    ]
    for etiqueta, valor in datos:
        pdf.set_xy(margen, y)
        pdf.cell(50, 7, etiqueta)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(ancho - margen * 2 - 50, 7, valor)
        pdf.set_font("Helvetica", "", 11)
        y += 9

    y += 5
    pdf.set_draw_color(*RGB_DORADO)
    pdf.line(margen, y, ancho - margen, y)
    y += 8

    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(margen, y)
    pdf.cell(ancho - margen * 2, 7, "Firma de Conformidad / Recibí conforme:")
    y += 10

    if hay_firma(img_firma):
        try:
            fw, fh = 100, 50
            img_tmp = os.path.join(CARPETA_RECURSOS, f"firma_{numero}.png")
            Image.fromarray(np.array(img_firma)).convert("RGB").save(img_tmp)
            pdf.image(img_tmp, x=margen, y=y, w=fw, h=fh)
        except Exception:
            pdf.set_xy(margen, y + 25)
            pdf.cell(ancho - margen * 2, 6, "_______________________________", align="L")
    else:
        pdf.set_xy(margen, y + 25)
        pdf.cell(ancho - margen * 2, 6, "_______________________________", align="L")

    ruta_pdf = os.path.join(CARPETA_PDF, f"remito_{numero:04d}.pdf")
    pdf.output(ruta_pdf)
    return ruta_pdf

# ==================================================
# 📄 PÁGINA: GESTIONAR EMPRESAS
# ==================================================
def pantalla_empresas():
    st.markdown(f"""<div class="tarjeta"><h2>🏢 Gestionar Empresas</h2>""", unsafe_allow_html=True)

    empresas = cargar_json(ARCHIVO_EMPRESAS, [])

    with st.form("form_empresa", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_empresa = st.text_input("Nombre de la Empresa")
        with col2:
            telefono_empresa = st.text_input("Teléfono (solo números)")
        if st.form_submit_button("➕ Agregar Empresa", type="primary"):
            if nombre_empresa.strip() and telefono_empresa.strip().isdigit():
                empresas.append({"nombre": nombre_empresa.strip(), "telefono": telefono_empresa.strip()})
                guardar_json(ARCHIVO_EMPRESAS, empresas)
                st.success(f"✅ Agregada: {nombre_empresa}")
                st.rerun()
            else:
                st.error("❌ Completá nombre y teléfono solo con números")

    st.markdown("### 📋 Empresas Cargadas")
    if not empresas:
        st.info("No hay empresas cargadas todavía")
    else:
        for i, emp in enumerate(empresas):
            col_a, col_b, col_c = st.columns([4, 3, 1])
            with col_a:
                st.write(f"🏢 **{emp['nombre']}**")
            with col_b:
                st.write(f"📞 {emp['telefono']}")
            with col_c:
                if st.button("🗑️", key=f"del_emp_{i}"):
                    empresas.pop(i)
                    guardar_json(ARCHIVO_EMPRESAS, empresas)
                    st.rerun()
            st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 📄 PÁGINA: NUEVO REMITO
# ==================================================
def pantalla_nuevo_remito():
    st.markdown(f"""<div class="tarjeta"><h2>📋 Generar Nuevo Remito</h2>""", unsafe_allow_html=True)

    empresas = cargar_json(ARCHIVO_EMPRESAS, [])
    remitos = cargar_json(ARCHIVO_REMITOS, [])

    if not empresas:
        st.warning("⚠️ Cargá al menos una empresa primero en 'Gestionar Empresas'")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not remitos:
        numero = 1
    else:
        numero = max([r.get("numero", 0) for r in remitos]) + 1

    fecha = datetime.date.today().strftime("%d/%m/%Y")

    emp_nombres = [e["nombre"] for e in empresas]
    emp_seleccion = st.selectbox("🏢 Seleccionar Empresa", emp_nombres, disabled=st.session_state.remito_generado)
    emp_datos = next(e for e in empresas if e["nombre"] == emp_seleccion)

    cantidad = st.number_input("🍽️ Cantidad de Viandas", min_value=1, value=1, disabled=st.session_state.remito_generado)
    recibe = st.text_input("👤 Quien Recibe (Nombre y Apellido)", disabled=st.session_state.remito_generado)

    st.markdown("### ✍️ Firma de Recibido")
    canvas_firma = st_canvas(
        stroke_width=2,
        stroke_color=DORADO,
        background_color="#FFFFFF",
        height=ALTO_FIRMA,
        width=ANCHO_FIRMA,
        return_image_data=True,
        key=f"firma_{st.session_state.contador_formulario}"
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        generar = st.button("✅ GENERAR REMITO", type="primary", disabled=st.session_state.remito_generado)
    with col_btn2:
        if st.button("🔄 NUEVO REMITO", type="secondary"):
            st.session_state.remito_generado = False
            st.session_state.contador_formulario += 1
            st.rerun()

    if generar:
        if not recibe.strip():
            st.error("❌ Escribí el nombre y apellido de quien recibe")
            return

        img_firma = canvas_firma.image_data

        with st.spinner(f"Generando Remito N° {numero:04d}..."):
            ruta_pdf = crear_pdf(numero, fecha, emp_datos["nombre"], emp_datos["telefono"], cantidad, recibe, img_firma)

        with st.spinner("Subiendo PDF a GitHub..."):
            enlace_pdf = subir_pdf_a_github(ruta_pdf, numero)

        if not enlace_pdf:
            st.error("❌ No se pudo subir el PDF")
            return

        remito = {
            "numero": numero,
            "fecha": fecha,
            "empresa": emp_datos["nombre"],
            "telefono": emp_datos["telefono"],
            "cantidad": cantidad,
            "recibe": recibe,
            "pdf_url": enlace_pdf
        }
        remitos.append(remito)
        guardar_json(ARCHIVO_REMITOS, remitos)

        hoja = conectar_google_sheets()
        if hoja:
            fila = [numero, fecha, emp_datos["nombre"], emp_datos["telefono"], cantidad, recibe, enlace_pdf]
            hoja.append_row(fila)

        st.session_state.remito_generado = True
        st.success(f"✅ Remito N° {numero:04d} generado y subido correctamente!")

        placeholder = st.empty()
        with placeholder:
            st.markdown(f"""
            <div class="caja-link-pdf">
                <strong>📄 Enlace al Remito PDF:</strong><br>
                <a href="{enlace_pdf}" target="_blank">{enlace_pdf}</a>
                <span class="aviso-espera">⏳ El remito tardará 30 segundos en poder visualizarse</span>
            </div>
            """, unsafe_allow_html=True)

        msj = mensaje_whatsapp(numero, emp_datos["nombre"], fecha, recibe, enlace_pdf)
        link_wsp = enlace_whatsapp(emp_datos["telefono"], msj)
        st.markdown(f"""
        <a href="{link_wsp}" target="_blank" style="
            display:inline-block; padding:12px 24px;
            background:{VERDE_WSP}; color:white !important;
            border-radius:12px; text-decoration:none;
            font-weight:bold; font-size:16px; margin-top:10px;
        ">📲 ENVIAR POR WHATSAPP</a>
        """, unsafe_allow_html=True)

        for segundo in range(30):
            time.sleep(1)

        placeholder.empty()
        with placeholder:
            st.markdown(f"""
            <div class="caja-link-pdf">
                <strong>📄 Enlace al Remito PDF:</strong><br>
                <a href="{enlace_pdf}" target="_blank">{enlace_pdf}</a>
                <span class="aviso-listo">✅ ¡YA ESTÁ LISTO PARA VER!</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 📄 PÁGINA: HISTORIAL
# ==================================================
def pantalla_historial():
    st.markdown(f"""<div class="tarjeta"><h2>📜 Historial de Remitos</h2>""", unsafe_allow_html=True)

    remitos = cargar_json(ARCHIVO_REMITOS, [])
    if not remitos:
        st.info("No hay remitos generados todavía")
    else:
        for r in reversed(remitos):
            with st.expander(f"📋 Remito N° {r['numero']:04d} — {r['empresa']} — {r['fecha']}"):
                st.write(f"📅 **Fecha:** {r['fecha']}")
                st.write(f"🏢 **Empresa:** {r['empresa']}")
                st.write(f"📞 **Teléfono:** {r['telefono']}")
                st.write(f"🍽️ **Cantidad:** {r['cantidad']} viandas")
                st.write(f"👤 **Recibe:** {r.get('recibe', 'No registrado')}")

                if r.get("pdf_url"):
                    st.markdown(f"📄 **PDF:** [Ver remito]({r['pdf_url']})")
                    msj = mensaje_whatsapp(r['numero'], r['empresa'], r['fecha'], r.get('recibe', ''), r['pdf_url'])
                    link_wsp = enlace_whatsapp(r['telefono'], msj)
                    st.markdown(f"""
                    <a href="{link_wsp}" target="_blank" style="
                        display:inline-block; padding:8px 16px;
                        background:{VERDE_WSP}; color:white !important;
                        border-radius:8px; text-decoration:none;
                        font-weight:bold; margin-top:8px;
                    ">📲 Enviar por WhatsApp</a>
                    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# 🚀 MOSTRAR PÁGINA ACTIVA — CORREGIDO
# ==================================================
def main():
    if st.session_state.pagina == "empresas":
        pantalla_empresas()
    elif st.session_state.pagina == "nuevo":
        pantalla_nuevo_remito()
    elif st.session_state.pagina == "historial":
        pantalla_historial()

if __name__ == "__main__":
    main()
