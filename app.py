import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Seguimiento de Obra - Fundación Masaveu", page_icon="🏗️")

# 1. Incorporar imagen del logo de la empresa
# El archivo debe llamarse 'logo.png' en tu repositorio de GitHub
try:
    st.image("logo.png", width=250)
except:
    st.info("💡 Nota: Sube un archivo 'logo.png' a GitHub para visualizar el logo aquí.")

st.title("Parte de Seguimiento de Obra")
st.markdown("---")

# --- ESTADO DE LA SESIÓN (Para mantener los datos temporalmente) ---
if "historico" not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado", "Observaciones"])

# --- FORMULARIO DE ENTRADA ---
with st.form("formulario_obra"):
    col1, col2 = st.columns(2)
    
    with col1:
        trabajador = st.text_input("Nombre del trabajador:")
    with col2:
        fecha_envio = st.date_input("Fecha de envío:", date.today())
    
    # Desplegable de Tareas
    tareas = [
        "Trazado y marcado de cajas, tubos y cuadros",
        "Ejecución rozas en paredes y techos",
        "Montaje de soportes",
        "Colocación tubos y conductos",
        "Tendido de cables",
        "Identificación y etiquetado",
        "Conexionado de cables en bornes o regletas",
        "Instalación y conexionado de mecanismos",
        "Fijación de carril DIN y mecanismos en cuadro eléctrico",
        "Cableado interno del cuadro eléctrico",
        "Configuración de equipos domóticos y/o automáticos",
        "Conexionado de sensores/actuadores de equipos domóticos/automáticos",
        "Pruebas de continuidad",
        "Pruebas de aislamiento",
        "Verificación de tierras",
        "Programación del automatismo",
        "Pruebas de funcionamiento"
    ]
    tarea_seleccionada = st.selectbox("Seleccione la tarea realizada:", tareas)
    
    # Desplegable de Estados
    estados = [
        "Avance de la tarea en torno al 25% aprox.",
        "Avance de la tarea en torno al 50% aprox.",
        "Avance de la tarea en torno al 75% aprox.",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ]
    estado_seleccionado = st.selectbox("Estado de avance:", estados)
    
    observaciones = st.text_area("Observaciones o incidencias:")
    
    btn_registrar = st.form_submit_button("Añadir al registro")

# Al pulsar "Registrar", añadimos a la tabla actual
if btn_registrar:
    if trabajador:
        nuevo_registro = {
            "Fecha": fecha_envio.strftime("%d/%m/%Y"),
            "Trabajador": trabajador,
            "Tarea": tarea_seleccionada,
            "Estado": estado_seleccionado,
            "Observaciones": observaciones
        }
        st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([nuevo_registro])], ignore_index=True)
        st.success("Registro añadido a la tabla temporal.")
    else:
        st.error("Por favor, introduce el nombre del trabajador.")

# --- VISUALIZACIÓN Y DESCARGA ---
st.markdown("### Registros en este informe")
st.table(st.session_state.historico)

# Función para convertir DataFrame a Excel
def generar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Seguimiento_Obra')
    return output.getvalue()

if not st.session_state.historico.empty:
    excel_data = generar_excel(st.session_state.historico)
    
    col_down, col_mail = st.columns(2)
    
    with col_down:
        st.download_button(
            label="💾 Descargar Excel en el móvil",
            data=excel_data,
            file_name=f"Parte_Obra_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_mail:
        if st.button("📧 Enviar por correo a Oficina"):
            try:
                # Datos del servidor (Configurar en Streamlit Secrets)
                smtp_server = "smtp.gmail.com" # Cambiar si usas otro proveedor
                smtp_port = 587
                remitente = st.secrets["email_user"]
                password = st.secrets["email_password"]
                destinatario = "ana@fundacionmasaveu.com"

                # Configurar el mensaje
                msg = MIMEMultipart()
                msg['From'] = remitente
                msg['To'] = destinatario
                msg['Subject'] = f"Nuevo Parte de Obra - {trabajador} - {date.today()}"
                
                cuerpo = f"Se ha generado un nuevo informe de obra.\n\nTrabajador: {trabajador}\nFecha: {fecha_envio}"
                msg.attach(MIMEText(cuerpo, 'plain'))

                # Adjuntar el Excel
                part = MIMEBase('application', "octet-stream")
                part.set_payload(excel_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="Parte_{date.today()}.xlsx"')
                msg.attach(part)

                # Envío
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(remitente, password)
                server.send_message(msg)
                server.quit()

                st.success(f"Correo enviado correctamente a {destinatario}")
            except Exception as e:
                st.error(f"Error al enviar: {e}")
                st.warning("Asegúrate de que los Secrets 'email_user' y 'email_password' están configurados.")
else:
    st.info("La tabla está vacía. Registra una tarea para habilitar la descarga y el envío.")

st.markdown("---")
st.caption("App de seguimiento interno - Fundación Masaveu")
