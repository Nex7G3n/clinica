import streamlit as st
import pandas as pd
from datetime import datetime, date
from database.db_manager import DatabaseManager
from utils.auth import require_auth, can_manage_patients
from utils.helpers import (
    show_success_message, show_error_message, validate_email, 
    validate_phone, validate_dni, get_age_from_birthdate,
    paginate_dataframe, show_pagination_controls
)

@require_auth(['administrador', 'doctor', 'recepcionista'])
def show_patient_management():
    """Página de gestión de pacientes"""
    st.title("👥 Gestión de Pacientes")
    
    db = DatabaseManager()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Pacientes", "➕ Nuevo Paciente", "✏️ Editar Paciente", "📄 Documentos"])
    
    with tab1:
        show_patients_list(db)
    
    with tab2:
        show_new_patient_form(db)
    
    with tab3:
        show_edit_patient_form(db)
    
    with tab4:
        show_patient_documents(db)

def show_patients_list(db):
    """Muestra la lista de pacientes"""
    st.subheader("📋 Lista de Pacientes")
    
    # Filtros de búsqueda
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Buscar paciente (nombre o DNI)", key="patient_search")
    
    with col2:
        if st.button("🔍 Buscar", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🔄 Limpiar", use_container_width=True):
            st.session_state.patient_search = ""
            st.rerun()
    
    # Obtener pacientes
    df_patients = db.get_patients(search_term if search_term else None)
    
    if df_patients.empty:
        st.info("No se encontraron pacientes" if search_term else "No hay pacientes registrados")
        return
    
    # Agregar columna de edad
    df_patients['edad'] = df_patients['fecha_nacimiento'].apply(get_age_from_birthdate)
    
    # Configurar columnas para mostrar
    columns_to_show = ['nombre_completo', 'dni', 'edad', 'sexo', 'telefono', 'email', 'estado']
    df_display = df_patients[columns_to_show].copy()
    
    # Renombrar columnas para mostrar
    df_display.columns = ['Nombre Completo', 'DNI', 'Edad', 'Sexo', 'Teléfono', 'Email', 'Estado']
    
    # Paginación
    page_size = 10
    df_paginated, current_page, total_pages = paginate_dataframe(df_display, page_size)
    
    # Mostrar tabla
    st.dataframe(
        df_paginated,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Estado": st.column_config.SelectboxColumn(
                "Estado",
                options=["activo", "inactivo"],
                required=True,
            )
        }
    )
    
    # Controles de paginación
    show_pagination_controls(current_page, total_pages)
    
    # Mostrar estadísticas
    st.subheader("📊 Estadísticas")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pacientes", len(df_patients))
    
    with col2:
        st.metric("Pacientes Activos", len(df_patients[df_patients['estado'] == 'activo']))
    
    with col3:
        avg_age = df_patients['edad'].mean() if 'edad' in df_patients.columns else 0
        st.metric("Edad Promedio", f"{avg_age:.1f}" if avg_age else "N/A")
    
    with col4:
        male_count = len(df_patients[df_patients['sexo'] == 'M'])
        st.metric("Pacientes Masculinos", male_count)

def show_new_patient_form(db):
    """Formulario para crear nuevo paciente"""
    st.subheader("➕ Registrar Nuevo Paciente")
    
    with st.form("new_patient_form", clear_on_submit=True):
        # Información básica
        st.write("**Información Personal**")
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_completo = st.text_input("Nombre Completo *", max_chars=100)
            dni = st.text_input("DNI *", max_chars=12)
            fecha_nacimiento = st.date_input("Fecha de Nacimiento *", max_value=date.today())
        
        with col2:
            sexo = st.selectbox("Sexo *", options=["M", "F", "Otro"], 
                               format_func=lambda x: "Masculino" if x == "M" else "Femenino" if x == "F" else "Otro")
            telefono = st.text_input("Teléfono", max_chars=20)
            email = st.text_input("Email", max_chars=100)
        
        direccion = st.text_area("Dirección", max_chars=200)
        
        # Información médica
        st.write("**Información Médica**")
        col1, col2 = st.columns(2)
        
        with col1:
            grupo_sanguineo = st.selectbox("Grupo Sanguíneo", 
                                         options=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            alergias = st.text_area("Alergias", max_chars=500)
        
        with col2:
            enfermedades_cronicas = st.text_area("Enfermedades Crónicas", max_chars=500)
        
        # Botón de envío
        submitted = st.form_submit_button("📝 Registrar Paciente", use_container_width=True)
        
        if submitted:
            # Validaciones
            errors = []
            
            if not nombre_completo:
                errors.append("El nombre completo es obligatorio")
            
            if not dni:
                errors.append("El DNI es obligatorio")
            elif not validate_dni(dni):
                errors.append("El formato del DNI no es válido")
            
            if not fecha_nacimiento:
                errors.append("La fecha de nacimiento es obligatoria")
            
            if email and not validate_email(email):
                errors.append("El formato del email no es válido")
            
            if telefono and not validate_phone(telefono):
                errors.append("El formato del teléfono no es válido")
            
            if errors:
                for error in errors:
                    show_error_message(error)
            else:
                try:
                    patient_id = db.create_patient(
                        dni=dni,
                        nombre_completo=nombre_completo,
                        fecha_nacimiento=fecha_nacimiento.isoformat(),
                        sexo=sexo,
                        telefono=telefono if telefono else None,
                        direccion=direccion if direccion else None,
                        email=email if email else None,
                        grupo_sanguineo=grupo_sanguineo if grupo_sanguineo else None,
                        alergias=alergias if alergias else None,
                        enfermedades_cronicas=enfermedades_cronicas if enfermedades_cronicas else None
                    )
                    
                    show_success_message(f"Paciente registrado exitosamente (ID: {patient_id})")
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        show_error_message("Ya existe un paciente con este DNI")
                    else:
                        show_error_message(f"Error al registrar paciente: {str(e)}")

def show_edit_patient_form(db):
    """Formulario para editar paciente"""
    st.subheader("✏️ Editar Paciente")
    
    # Selector de paciente
    df_patients = db.get_patients()
    
    if df_patients.empty:
        st.info("No hay pacientes registrados para editar")
        return
    
    # Crear diccionario para el selectbox
    patient_options = {}
    for _, patient in df_patients.iterrows():
        patient_options[f"{patient['nombre_completo']} - {patient['dni']}"] = patient['id']
    
    selected_patient_key = st.selectbox(
        "Seleccionar Paciente",
        options=list(patient_options.keys()),
        key="edit_patient_selector"
    )
    
    if selected_patient_key:
        patient_id = patient_options[selected_patient_key]
        patient_data = db.get_patient_by_id(patient_id)
        
        if patient_data:
            with st.form("edit_patient_form"):
                # Información básica
                st.write("**Información Personal**")
                col1, col2 = st.columns(2)
                
                with col1:
                    nombre_completo = st.text_input("Nombre Completo *", value=patient_data['nombre_completo'])
                    dni = st.text_input("DNI *", value=patient_data['dni'])
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento *", 
                                                   value=datetime.strptime(patient_data['fecha_nacimiento'], '%Y-%m-%d').date())
                
                with col2:
                    sexo_index = ["M", "F", "Otro"].index(patient_data['sexo'])
                    sexo = st.selectbox("Sexo *", options=["M", "F", "Otro"], index=sexo_index,
                                       format_func=lambda x: "Masculino" if x == "M" else "Femenino" if x == "F" else "Otro")
                    telefono = st.text_input("Teléfono", value=patient_data['telefono'] or "")
                    email = st.text_input("Email", value=patient_data['email'] or "")
                
                direccion = st.text_area("Dirección", value=patient_data['direccion'] or "")
                
                # Información médica
                st.write("**Información Médica**")
                col1, col2 = st.columns(2)
                
                with col1:
                    grupo_options = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                    grupo_index = 0
                    if patient_data['grupo_sanguineo'] and patient_data['grupo_sanguineo'] in grupo_options:
                        grupo_index = grupo_options.index(patient_data['grupo_sanguineo'])
                    
                    grupo_sanguineo = st.selectbox("Grupo Sanguíneo", options=grupo_options, index=grupo_index)
                    alergias = st.text_area("Alergias", value=patient_data['alergias'] or "")
                
                with col2:
                    enfermedades_cronicas = st.text_area("Enfermedades Crónicas", value=patient_data['enfermedades_cronicas'] or "")
                    
                    estado_index = ["activo", "inactivo"].index(patient_data['estado'])
                    estado = st.selectbox("Estado", options=["activo", "inactivo"], index=estado_index)
                
                # Botón de actualización
                submitted = st.form_submit_button("💾 Actualizar Paciente", use_container_width=True)
                
                if submitted:
                    # Validaciones
                    errors = []
                    
                    if not nombre_completo:
                        errors.append("El nombre completo es obligatorio")
                    
                    if not dni:
                        errors.append("El DNI es obligatorio")
                    elif not validate_dni(dni):
                        errors.append("El formato del DNI no es válido")
                    
                    if email and not validate_email(email):
                        errors.append("El formato del email no es válido")
                    
                    if telefono and not validate_phone(telefono):
                        errors.append("El formato del teléfono no es válido")
                    
                    if errors:
                        for error in errors:
                            show_error_message(error)
                    else:
                        try:
                            db.update_patient(
                                patient_id,
                                dni=dni,
                                nombre_completo=nombre_completo,
                                fecha_nacimiento=fecha_nacimiento.isoformat(),
                                sexo=sexo,
                                telefono=telefono if telefono else None,
                                direccion=direccion if direccion else None,
                                email=email if email else None,
                                grupo_sanguineo=grupo_sanguineo if grupo_sanguineo else None,
                                alergias=alergias if alergias else None,
                                enfermedades_cronicas=enfermedades_cronicas if enfermedades_cronicas else None,
                                estado=estado
                            )
                            
                            show_success_message("Paciente actualizado exitosamente")
                            
                        except Exception as e:
                            if "UNIQUE constraint failed" in str(e):
                                show_error_message("Ya existe un paciente con este DNI")
                            else:
                                show_error_message(f"Error al actualizar paciente: {str(e)}")

def show_patient_documents(db):
    """Gestión de documentos de pacientes"""
    st.subheader("📄 Documentos Médicos")
    
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
        options=list(patient_options.keys()),
        key="documents_patient_selector"
    )
    
    if selected_patient_key:
        patient_id = patient_options[selected_patient_key]
        
        # Subir nuevo documento
        st.write("**Subir Nuevo Documento**")
        
        uploaded_file = st.file_uploader(
            "Seleccionar archivo",
            type=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
            key="document_upload"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox(
                "Tipo de Documento",
                options=["Receta", "Examen", "Radiografía", "Informe", "Otro"]
            )
        
        if uploaded_file and st.button("📤 Subir Documento"):
            # Aquí se implementaría la lógica para guardar el archivo
            # Por simplicidad, se simula
            st.success(f"Documento '{uploaded_file.name}' subido exitosamente")
        
        # Lista de documentos (simulada)
        st.write("**Documentos del Paciente**")
        st.info("Funcionalidad de documentos en desarrollo. Aquí se mostrarían los documentos médicos del paciente.")

if __name__ == "__main__":
    show_patient_management()
