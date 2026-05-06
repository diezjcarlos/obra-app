import streamlit as st
import pandas as pd
from datetime import date
import io

# Configuración de la página
st.set_page_config(page_title="Seguimiento de Obra", page_icon="🏗️")

# 1. Incorporar imagen del logo
# Asegúrate de tener un archivo llamado 'logo.png' en tu repositorio
try:
    st.image("logo.png", width=200)
except:
    st.warning("⚠️ No se encontró el archivo 'logo.png'. Por favor, súbelo al repositorio.")

st.title("Control de Avance de Obra")
st.markdown("---")

# 2. Formulario de entrada de datos
with st.form("formulario_obra"):
    col1, col2 = st.columns(2)
    
    with col1:
        trabajador = st.text_input("Nombre del Trabajador")
        fecha = st.date_input("Fecha de envío", date.today())
    
    tareas = [
        "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos",
        "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables",
        "Identificación y etiquetado", "Conexionado de cables en bornes o regletas",
        "Instalación y conexionado de mecanismos", "Fijación de carril DIN y mecanismos en cuadro eléctrico",
        "Cableado interno del cuadro eléctrico", "Configuración de equipos domóticos y/o automáticos",
        "Conexionado de sensores/actuadores de equipos domóticos/automáticos", "Pruebas de continuidad",
        "Pruebas de aislamiento", "Verificación de tierras", "Programación del automatismo",
        "Pruebas de funcionamiento"
    ]
    tarea_seleccionada = st.selectbox("Selecciona la tarea:", tareas)
    
    estados = [
        "Avance de la tarea en torno al 25% aprox.",
        "Avance de la tarea en torno al 50% aprox.",
        "Avance de la tarea en torno al 75% aprox.",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ]
    estado_seleccionado = st.selectbox("Estado de la tarea:", estados)
    
    comentarios = st.text_area("Observaciones adicionales")
    
    submit_button = st.form_submit_button("Registrar Datos")

# 3. Gestión de datos (Persistencia temporal en sesión)
if "historico" not in st.session_state:
    st.session_state.historico = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado", "Observaciones"])

if submit_button:
    nuevo_registro = {
        "Fecha": fecha,
        "Trabajador": trabajador,
        "Tarea": tarea_seleccionada,
        "Estado": estado_seleccionado,
        "Observaciones": comentarios
    }
    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("✅ Registro añadido correctamente.")

# 4. Visualización de la tabla
st.subheader("Registros actuales")
st.dataframe(st.session_state.historico)

# 5. Generación de Excel para descarga
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Seguimiento')
    return output.getvalue()

excel_data = to_excel(st.session_state.historico)

st.download_button(
    label="📥 Descargar Reporte en Excel",
    data=excel_data,
    file_name=f"reporte_obra_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 6. Envío por correo (Nota aclaratoria)
st.markdown("---")
st.subheader("Envio a Oficina Central")
if st.button("📧 Enviar Reporte por Correo"):
    st.info("Para activar el envío real, debes configurar un servidor SMTP. Actualmente, descarga el Excel y envíalo manualmente.")
    # Nota: El envío automático requiere configurar secretos (API keys o contraseñas de apps) 
    # en el panel de Streamlit Cloud por seguridad.
