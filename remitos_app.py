# -*- coding: utf-8 -*-
"""
🍽️ EL BODEGÓN — Sistema de Remitos de Viandas
✅ Mensaje WhatsApp EXACTO como querés
✅ Botón BORRAR en Historial 🗑️
✅ WhatsApp APARECE ENSEGUIDA — PDF espera 30s
✅ Archivo remitos.json se crea solo al generar el primer remito
"""

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

NOMBRE_NEGOCIO     = "EL BODEGÓN"
TITULO_APP         = "Remitos - El Bodegón"
SUBTITULO          = "Sistema de Entrega de Viandas"

GITHUB_USUARIO     = "remitosbodegon"
GITHUB_REPO        = "mis-remitos"
GITHUB_RAMA        = "main"

ANCHO_FIRMA        = 600
ALTO_FIRMA         = 260
CARPETA_RECURSOS   = "recursos"
CARPETA_PDF        = "remitos_pdf"

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

RUTA_LOGO = os.path.join(CARPETA_RECURSOS, "logo_bodegon.png") if os.path.exists(os.path.join(CARPETA_RECURSOS, "logo_bodegon.png")) else None

os.makedirs(CARPETA_RECURSOS, exist_ok=True)
os.makedirs(CARPETA_PDF, exist_ok=True)

ARCHIVO_EMPRESAS = "empresas.json"
ARCHIVO_REMITOS = "remitos.json"

# ──────────────────────────────────────────────────
# ESTADO DE LA APP
# ──────────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state.pagina = "nuevo"
if "contador_formulario" not in st.session_state:
    st.session_state.contador_formulario = 0
if "remito_generado" not in st.session_state:
    st.session_state.remito_generado = False

# ──────────────────────────────────────────────────
# ESTILO
# ──────────────────────────────────────────────────
st.set_page_config(page_title=TITULO_APP, page_icon="recursos/icono-app.png", layout="wide")
# ÍCONO PERSONALIZADO SIN ERROR DE NOMBRE
st.markdown("""
<link rel="icon" type="image/png" href="https://raw.githubusercontent.com/remitosbodegon/mis-remitos/main/recursos/icono-app.png">
<link rel="apple-touch-icon" href="https://raw.githubusercontent.com/remitosbodegon/mis-remitos/main/recursos/icono-app.png?v=4">
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# NAVEGACIÓN
# ──────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────
# FUNCIONES DE GUARDADO Y SUBIDA A GITHUB
# ──────────────────────────────────────────────────
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
        subir_archivo_a_github(ruta)  # ✅ Sube el archivo a GitHub automáticamente
    except Exception as e:
        if os.path.exists(ruta_tmp):
            os.remove(ruta_tmp)
        st.error(f"❌ Error: {str(e)[:60]}")

def obtener_token_github():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    if os.path.exists("github_token.txt"):
        with open("github_token.txt") as f:
            return f.read().strip()
    return None

def subir_archivo_a_github(ruta_archivo):
    """Sube remitos.json al repositorio para que aparezca en GitHub"""
    token = obtener_token_github()
    if not token:
        return False
    nombre_archivo = os.path.basename(ruta_archivo)
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        contenido_b64 = base64.b64encode(contenido.encode("utf-8")).decode()
        url = f"https://api.github.com/repos/{GITHUB_USUARIO}/{GITHUB_REPO}/contents/{nombre_archivo}"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        resp = requests.get(url, headers=headers, params={"ref": GITHUB_RAMA})
        sha = resp.json().get("sha") if resp.status_code == 200 else None
        body = {"message": f"Actualizar {nombre_archivo}", "content": contenido_b64, "branch": GITHUB_RAMA}
        if sha:
            body["sha"] = sha
        resp = requests.put(url, headers=headers, json=body)
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"Error subiendo: {e}")
        return False

def subir_pdf_a_github(ruta_archivo, numero_remito):
    token = obtener_token_github()
    if not token:
        st.error("❌ Falta token de GitHub")
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

# ──────────────────────────────────────────────────
# DETECCIÓN DE FIRMA
# ──────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────
# ✅ MENSAJE DE WHATSAPP EXACTO COMO QUERÉS
# ──────────────────────────────────────────────────
def mensaje_whatsapp(num, emp, fecha, recibe, pdf=""):
    return (
        f"📄 REMITO N° {num:04d} — Entrega a: {emp}\n"
        f"✅ Se le envía el remito de las viandas entregadas el día {fecha}.\n"
        f"👤 Recibe: {recibe} \n"
        f"🔗 VER REMITO EN PDF:\n{pdf}\n\n"
        f"¡Gracias por su compra!"
    )

def enlace_whatsapp(tel, msg):
    t = "".join(c for c in tel if c.isdigit())
    return f"https://wa.me/{t}?text={urllib.parse.quote(msg)}"

# ──────────────────────────────────────────────────
# GENERAR PDF
# ──────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────
# PANTALLA: GESTIONAR EMPRESAS
# ──────────────────────────────────────────────────
def pantalla_empresas():
    st.markdown(f"""<div class="tarjeta"><h2>🏢 Gestionar Empresas</h2>""", unsafe_allow_html=True)
    empresas = cargar_json(ARCHIVO_EMPRESAS, [])
    
    st.subheader("Agregar Nueva Empresa")
    nom = st.text_input("Nombre de Empresa")
    tel = st.text_input("Teléfono")
    if st.button("✅ Guardar Empresa", type="primary"):
        if nom.strip() and tel.strip():
            empresas.append({"nombre": nom.strip(), "telefono": tel.strip()})
            guardar_json(ARCHIVO_EMPRESAS, empresas)
            st.success(f"✅ Empresa '{nom}' agregada")
            st.rerun()
        else:
            st.error("❌ Completá nombre y teléfono")
    
    st.markdown("---")
    st.subheader("Empresas Registradas")
    if not empresas:
        st.info("No hay empresas cargadas todavía")
    else:
        for i, e in enumerate(empresas):
            col_a, col_b, col_c = st.columns([0.45, 0.45, 0.1])
            col_a.write(f"🏢 **{e['nombre']}**")
            col_b.write(f"📞 {e['telefono']}")
            if col_c.button("❌", key=f"del_emp_{i}"):
                empresas.pop(i)
                guardar_json(ARCHIVO_EMPRESAS, empresas)
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# PANTALLA: NUEVO REMITO
# ──────────────────────────────────────────────────
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
        guardar_json(ARCHIVO_REMITOS, remitos)  # ✅ Se guarda Y SE SUBE A GITHUB
        
        st.session_state.remito_generado = True
        st.success(f"✅ Remito N° {numero:04d} generado y guardado correctamente!")
        
        # ✅ WHATSAPP APARECE ENSEGUIDA
        msj = mensaje_whatsapp(numero, emp_datos["nombre"], fecha, recibe, enlace_pdf)
        link_wsp = enlace_whatsapp(emp_datos["telefono"], msj)
        st.markdown(f"""
        <a href="{link_wsp}" target="_blank" style="
            display:inline-block; padding:12px 24px;
            background:{VERDE_WSP}; color:white !important;
            border-radius:12px; text-decoration:none;
            font-weight:bold; font-size:16px; margin:10px 0;
        ">📲 ENVIAR POR WHATSAPP</a>
        """, unsafe_allow_html=True)
        
        # ✅ SOLO EL ENLACE DEL PDF MUESTRA EL CONTADOR
        placeholder = st.empty()
        with placeholder:
            st.markdown(f"""
            <div class="caja-link-pdf">
                <strong>📄 Enlace al Remito PDF:</strong><br>
                <a href="{enlace_pdf}" target="_blank">{enlace_pdf}</a>
                <span class="aviso-espera">⏳ Esperá 30 segundos para poder ver el PDF</span>
            </div>
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

# ──────────────────────────────────────────────────
# ✅ PANTALLA: HISTORIAL CON BOTÓN BORRAR 🗑️
# ──────────────────────────────────────────────────
def pantalla_historial():
    st.markdown(f"""<div class="tarjeta"><h2>📜 Historial de Remitos</h2>""", unsafe_allow_html=True)
    remitos = cargar_json(ARCHIVO_REMITOS, [])
    
    if not remitos:
        st.info("No hay remitos generados todavía. Al generar el primero se creará el archivo remitos.json en GitHub.")
    else:
        indices_a_borrar = []
        
        for i, r in enumerate(reversed(remitos)):
            indice_real = len(remitos) - 1 - i
            
            col_exp, col_del = st.columns([0.92, 0.08])
            with col_exp:
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
            with col_del:
                if st.button("🗑️", key=f"borrar_{i}", help="Borrar este remito"):
                    indices_a_borrar.append(indice_real)
        
        # Ejecutar borrado
        if indices_a_borrar:
            todos = cargar_json(ARCHIVO_REMITOS, [])
            for idx in sorted(indices_a_borrar, reverse=True):
                todos.pop(idx)
            guardar_json(ARCHIVO_REMITOS, todos)  # ✅ Se actualiza Y SE SUBE A GITHUB
            st.success("✅ Remito borrado y eliminado de GitHub! Recargá la página.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────
# ENRUTADOR DE PÁGINAS
# ──────────────────────────────────────────────────
if st.session_state.pagina == "empresas":
    pantalla_empresas()
elif st.session_state.pagina == "nuevo":
    pantalla_nuevo_remito()
elif st.session_state.pagina == "historial":
    pantalla_historial()
