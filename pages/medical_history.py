import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.db_manager import DatabaseManager
from utils.auth import require_auth, get_current_user, can_access_medical_records
from utils.helpers import show_success_message, show_error_message, format_datetime, PDFGenerator

@require_auth(['administrador', 'doctor'])
def show_medical_history():
    """Página de historial médico"""
    st.title("📋 Historial Médico")
    
    db = DatabaseManager()
    user = get_current_user()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3 = st.tabs(["🔍 Consultar Historial", "➕ Nueva Consulta", "📄 Generar Receta"])
    
    with tab1:
        show_patient_history(db, user)
    
    with tab2:
        show_new_medical_record_form(db, user)
    
    with tab3:
        show_prescription_generator(db, user)

def show_patient_history(db, user):
    """Mostrar historial de un paciente"""
    st.subheader("🔍 Consultar Historial del Paciente")
    
    # Selector de paciente
    df_patients = db.get_patients()
    
    if df_patients.empty:
        st.info("No hay pacientes registrados")
        return
    
    patient_options = {}
    for _, patient in df_patients.iterrows():
        patient_options[f"{patient['nombre_completo']} - {patient['dni']}"] = patient['id']
    
    selected_patient_key = st.selectbox(
        "Seleccionar Paciente",
        options=list(patient_options.keys())
    )
    
    if selected_patient_key:
        patient_id = patient_options[selected_patient_key]
        patient_data = db.get_patient_by_id(patient_id)
        
        # Información del paciente
        st.subheader("👤 Información del Paciente")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Nombre:** {patient_data['nombre_completo']}")
            st.write(f"**DNI:** {patient_data['dni']}")
            st.write(f"**Sexo:** {'Masculino' if patient_data['sexo'] == 'M' else 'Femenino' if patient_data['sexo'] == 'F' else 'Otro'}")
        
        with col2:
            st.write(f"**Fecha Nacimiento:** {patient_data['fecha_nacimiento']}")
            st.write(f"**Teléfono:** {patient_data['telefono'] or 'No especificado'}")
            st.write(f"**Email:** {patient_data['email'] or 'No especificado'}")
        
        with col3:
            st.write(f"**Grupo Sanguíneo:** {patient_data['grupo_sanguineo'] or 'No especificado'}")
            st.write(f"**Alergias:** {patient_data['alergias'] or 'Ninguna conocida'}")
            st.write(f"**Enfermedades Crónicas:** {patient_data['enfermedades_cronicas'] or 'Ninguna conocida'}")
        
        st.divider()
        
        # Historial médico
        st.subheader("📋 Historial de Consultas")
        
        df_history = db.get_patient_medical_history(patient_id)
        
        if df_history.empty:
            st.info("El paciente no tiene historial médico registrado")
        else:
            for _, record in df_history.iterrows():
                with st.expander(f"📅 {format_datetime(record['fecha'])} - Dr. {record['medico_nombre']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Motivo de Consulta:**")
                        st.write(record['motivo_consulta'])
                        
                        if record['diagnostico']:
                            st.write(f"**Diagnóstico:**")
                            st.write(record['diagnostico'])
                    
                    with col2:
                        if record['receta']:
                            st.write(f"**Receta:**")
                            st.write(record['receta'])
                        
                        if record['examenes_solicitados']:
                            st.write(f"**Exámenes Solicitados:**")
                            st.write(record['examenes_solicitados'])
                    
                    if record['observaciones']:
                        st.write(f"**Observaciones:**")
                        st.write(record['observaciones'])

def show_new_medical_record_form(db, user):
    """Formulario para nuevo registro médico"""
    st.subheader("➕ Registrar Nueva Consulta")
    
    with st.form("new_medical_record_form", clear_on_submit=True):
        # Selector de paciente
        df_patients = db.get_patients()
        
        if df_patients.empty:
            st.error("No hay pacientes registrados")
            st.form_submit_button("Registrar Consulta", disabled=True)
            return
        
        patient_options = {}
        for _, patient in df_patients.iterrows():
            patient_options[f"{patient['nombre_completo']} - {patient['dni']}"] = patient['id']
        
        selected_patient_key = st.selectbox("Seleccionar Paciente *", options=list(patient_options.keys()))
        
        # Verificar si hay una cita asociada
        st.info("💡 Tip: Si esta consulta está relacionada con una cita específica, la asociación se puede hacer después.")
        
        # Información de la consulta
        motivo_consulta = st.text_area("Motivo de Consulta *", max_chars=1000, height=100)
        diagnostico = st.text_area("Diagnóstico", max_chars=1000, height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            receta = st.text_area("Receta Médica", max_chars=1000, height=150)
        
        with col2:
            examenes_solicitados = st.text_area("Exámenes Solicitados", max_chars=1000, height=150)
        
        observaciones = st.text_area("Observaciones Generales", max_chars=1000, height=100)
        
        # Fecha y hora de la consulta
        col1, col2 = st.columns(2)
        with col1:
            fecha_consulta = st.date_input("Fecha de Consulta", value=date.today())
        with col2:
            hora_consulta = st.time_input("Hora de Consulta", value=datetime.now().time())
        
        submitted = st.form_submit_button("📝 Registrar Consulta", use_container_width=True)
        
        if submitted:
            if selected_patient_key and motivo_consulta:
                try:
                    patient_id = patient_options[selected_patient_key]
                    
                    # Crear registro médico
                    record_id = db.create_medical_record(
                        paciente_id=patient_id,
                        medico_id=user['id'],
                        motivo_consulta=motivo_consulta,
                        diagnostico=diagnostico if diagnostico else None,
                        receta=receta if receta else None,
                        examenes_solicitados=examenes_solicitados if examenes_solicitados else None,
                        observaciones=observaciones if observaciones else None
                    )
                    
                    show_success_message(f"Consulta registrada exitosamente (ID: {record_id})")
                    
                except Exception as e:
                    show_error_message(f"Error al registrar consulta: {str(e)}")
            else:
                show_error_message("Por favor complete los campos obligatorios (paciente y motivo de consulta)")

def show_prescription_generator(db, user):
    """Generador de recetas en PDF"""
    st.subheader("📄 Generar Receta Médica")
    
    # Selector de paciente
    df_patients = db.get_patients()
    
    if df_patients.empty:
        st.info("No hay pacientes registrados")
        return
    
    patient_options = {}
    for _, patient in df_patients.iterrows():
        patient_options[f"{patient['nombre_completo']} - {patient['dni']}"] = patient['id']
    
    selected_patient_key = st.selectbox("Seleccionar Paciente", options=list(patient_options.keys()), key="prescription_patient")
    
    if selected_patient_key:
        patient_id = patient_options[selected_patient_key]
        patient_data = db.get_patient_by_id(patient_id)
        
        # Mostrar datos del paciente
        st.info(f"👤 Paciente: {patient_data['nombre_completo']} - DNI: {patient_data['dni']}")
        
        # Formulario para la receta
        with st.form("prescription_form"):
            st.write("**Información del Médico:**")
            st.write(f"Dr. {user['nombre_completo']}")
            st.write(f"Especialidad: {user['especialidad'] or 'No especificada'}")
            
            st.divider()
            
            prescription_text = st.text_area(
                "Prescripción Médica *",
                placeholder="Ingrese los medicamentos, dosis, frecuencia y duración del tratamiento...",
                height=300,
                max_chars=2000
            )
            
            # Información adicional
            col1, col2 = st.columns(2)
            with col1:
                diagnosis_for_prescription = st.text_input("Diagnóstico", max_chars=200)
            with col2:
                prescription_date = st.date_input("Fecha de la Receta", value=date.today())
            
            generate_pdf = st.form_submit_button("📄 Generar Receta PDF", use_container_width=True)
            
            if generate_pdf:
                if prescription_text:
                    try:
                        # Generar PDF de la receta
                        pdf_generator = PDFGenerator()
                        
                        # Datos para el PDF
                        prescription_data = {
                            'receta': prescription_text,
                            'diagnostico': diagnosis_for_prescription,
                            'fecha': prescription_date.isoformat()
                        }
                        
                        doctor_data = {
                            'nombre_completo': user['nombre_completo'],
                            'especialidad': user['especialidad'] or 'Medicina General'
                        }
                        
                        pdf_bytes = pdf_generator.generate_prescription(
                            patient_data, doctor_data, prescription_data
                        )
                        
                        # Botón de descarga
                        st.download_button(
                            label="📥 Descargar Receta PDF",
                            data=pdf_bytes,
                            file_name=f"receta_{patient_data['dni']}_{prescription_date.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        show_success_message("Receta generada exitosamente")
                        
                        # Opcional: Guardar en el historial médico
                        if st.checkbox("Guardar en historial médico del paciente"):
                            if st.button("💾 Guardar en Historial"):
                                db.create_medical_record(
                                    paciente_id=patient_id,
                                    medico_id=user['id'],
                                    motivo_consulta="Emisión de receta médica",
                                    diagnostico=diagnosis_for_prescription if diagnosis_for_prescription else None,
                                    receta=prescription_text,
                                    observaciones=f"Receta generada el {prescription_date.strftime('%d/%m/%Y')}"
                                )
                                show_success_message("Receta guardada en el historial médico")
                        
                    except Exception as e:
                        show_error_message(f"Error al generar la receta: {str(e)}")
                else:
                    show_error_message("Por favor ingrese la prescripción médica")

if __name__ == "__main__":
    show_medical_history()
