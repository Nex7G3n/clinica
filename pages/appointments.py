import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from database.db_manager import DatabaseManager
from utils.auth import require_auth, get_current_user
from utils.helpers import show_success_message, show_error_message, format_date
import calendar

@require_auth(['administrador', 'doctor', 'recepcionista'])
def show_appointment_management():
    """Página de gestión de citas"""
    st.title("📅 Gestión de Citas")
    
    db = DatabaseManager()
    user = get_current_user()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Citas", "➕ Nueva Cita", "📅 Calendario", "📊 Estadísticas"])
    
    with tab1:
        show_appointments_list(db, user)
    
    with tab2:
        show_new_appointment_form(db, user)
    
    with tab3:
        show_calendar_view(db, user)
    
    with tab4:
        show_appointment_stats(db, user)

def show_appointments_list(db, user):
    """Lista de citas"""
    st.subheader("📋 Lista de Citas")
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_date = st.date_input("Fecha", value=date.today(), key="appointments_date_filter")
    
    with col2:
        filter_status = st.selectbox("Estado", options=["Todos", "pendiente", "atendida", "cancelada"])
    
    with col3:
        # Solo mostrar filtro de médico si el usuario es administrador o recepcionista
        if user['rol'] in ['administrador', 'recepcionista']:
            df_doctors = db.get_users('doctor')
            doctor_options = ["Todos"] + [f"{doc['nombre_completo']}" for _, doc in df_doctors.iterrows()]
            selected_doctor = st.selectbox("Médico", options=doctor_options)
            
            if selected_doctor != "Todos":
                doctor_id = df_doctors[df_doctors['nombre_completo'] == selected_doctor]['id'].iloc[0]
            else:
                doctor_id = None
        else:
            doctor_id = user['id']  # Solo mostrar citas del médico actual
            st.info(f"Mostrando citas de: {user['nombre_completo']}")
    
    with col4:
        if st.button("🔍 Filtrar", use_container_width=True):
            st.rerun()
    
    # Obtener citas según filtros
    status_filter = filter_status if filter_status != "Todos" else None
    df_appointments = db.get_appointments(
        date_filter=filter_date.isoformat(),
        medico_id=doctor_id,
        estado=status_filter
    )
    
    if df_appointments.empty:
        st.info("No se encontraron citas con los filtros seleccionados")
        return
    
    # Ordenar por hora
    df_appointments = df_appointments.sort_values('hora')
    
    # Mostrar citas
    for _, appointment in df_appointments.iterrows():
        status_colors = {
            'pendiente': '🟡',
            'atendida': '🟢',
            'cancelada': '🔴'
        }
        
        status_icon = status_colors.get(appointment['estado'], '⚪')
        
        with st.expander(
            f"{status_icon} {appointment['hora']} - {appointment['paciente_nombre']} ({appointment['estado'].upper()})"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Paciente:** {appointment['paciente_nombre']}")
                st.write(f"**DNI:** {appointment['dni']}")
                st.write(f"**Médico:** {appointment['medico_nombre']}")
                st.write(f"**Fecha:** {format_date(appointment['fecha'])}")
                st.write(f"**Hora:** {appointment['hora']}")
            
            with col2:
                st.write(f"**Estado:** {appointment['estado'].title()}")
                if appointment['motivo']:
                    st.write(f"**Motivo:** {appointment['motivo']}")
                if appointment['observaciones']:
                    st.write(f"**Observaciones:** {appointment['observaciones']}")
            
            # Acciones
            st.write("**Acciones:**")
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if appointment['estado'] == 'pendiente':
                    if st.button("✅ Marcar Atendida", key=f"attend_{appointment['id']}"):
                        db.update_appointment_status(appointment['id'], 'atendida')
                        show_success_message("Cita marcada como atendida")
                        st.rerun()
            
            with action_col2:
                if appointment['estado'] == 'pendiente':
                    if st.button("❌ Cancelar", key=f"cancel_{appointment['id']}"):
                        db.update_appointment_status(appointment['id'], 'cancelada', 'Cancelada por usuario')
                        show_success_message("Cita cancelada")
                        st.rerun()
            
            with action_col3:
                if user['rol'] == 'doctor' and appointment['estado'] == 'atendida':
                    if st.button("📋 Ver/Editar Historial", key=f"history_{appointment['id']}"):
                        st.session_state.selected_patient_id = appointment['paciente_id']
                        st.session_state.selected_appointment_id = appointment['id']
                        st.info("Funcionalidad de historial médico disponible en la sección correspondiente")

def show_new_appointment_form(db, user):
    """Formulario para nueva cita"""
    st.subheader("➕ Agendar Nueva Cita")
    
    with st.form("new_appointment_form", clear_on_submit=True):
        # Selección de paciente
        df_patients = db.get_patients()
        
        if df_patients.empty:
            st.error("No hay pacientes registrados. Debe registrar un paciente primero.")
            st.form_submit_button("Crear Cita", disabled=True)
            return
        
        patient_options = {}
        for _, patient in df_patients.iterrows():
            patient_options[f"{patient['nombre_completo']} - {patient['dni']}"] = patient['id']
        
        selected_patient_key = st.selectbox("Seleccionar Paciente *", options=list(patient_options.keys()))
        
        # Selección de médico
        if user['rol'] in ['administrador', 'recepcionista']:
            df_doctors = db.get_users('doctor')
            
            if df_doctors.empty:
                st.error("No hay médicos registrados.")
                st.form_submit_button("Crear Cita", disabled=True)
                return
            
            doctor_options = {}
            for _, doctor in df_doctors.iterrows():
                doctor_options[f"Dr. {doctor['nombre_completo']} - {doctor['especialidad'] or 'Sin especialidad'}"] = doctor['id']
            
            selected_doctor_key = st.selectbox("Seleccionar Médico *", options=list(doctor_options.keys()))
            medico_id = doctor_options[selected_doctor_key]
        else:
            medico_id = user['id']
            st.info(f"Cita asignada a: Dr. {user['nombre_completo']}")
        
        # Fecha y hora
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_cita = st.date_input("Fecha de la Cita *", min_value=date.today())
        
        with col2:
            # Generar opciones de hora (de 8:00 a 18:00, cada 30 minutos)
            time_options = []
            start_time = time(8, 0)  # 8:00 AM
            end_time = time(18, 0)   # 6:00 PM
            
            current_time = datetime.combine(date.today(), start_time)
            end_datetime = datetime.combine(date.today(), end_time)
            
            while current_time <= end_datetime:
                time_options.append(current_time.time())
                current_time += timedelta(minutes=30)
            
            hora_cita = st.selectbox("Hora de la Cita *", options=time_options, format_func=lambda x: x.strftime('%H:%M'))
        
        # Información adicional
        motivo = st.text_area("Motivo de la Consulta", max_chars=500)
        observaciones = st.text_area("Observaciones", max_chars=500)
        
        # Verificar disponibilidad
        st.write("**Verificar Disponibilidad**")
        if st.form_submit_button("🔍 Verificar Disponibilidad", use_container_width=True):
            # Verificar si ya existe una cita en esa fecha y hora para el médico
            existing_appointments = db.get_appointments(
                date_filter=fecha_cita.isoformat(),
                medico_id=medico_id
            )
            
            if not existing_appointments.empty:
                conflicting_appointments = existing_appointments[
                    existing_appointments['hora'] == hora_cita.strftime('%H:%M:%S')
                ]
                
                if not conflicting_appointments.empty:
                    st.error(f"⚠️ Ya existe una cita programada para el Dr. en esa fecha y hora")
                else:
                    st.success("✅ Horario disponible")
            else:
                st.success("✅ Horario disponible")
        
        # Botón de creación
        submitted = st.form_submit_button("📅 Crear Cita", use_container_width=True)
        
        if submitted:
            if selected_patient_key and fecha_cita and hora_cita:
                try:
                    paciente_id = patient_options[selected_patient_key]
                    
                    # Verificar disponibilidad nuevamente
                    existing_appointments = db.get_appointments(
                        date_filter=fecha_cita.isoformat(),
                        medico_id=medico_id
                    )
                    
                    conflicting_appointments = existing_appointments[
                        existing_appointments['hora'] == hora_cita.strftime('%H:%M:%S')
                    ] if not existing_appointments.empty else pd.DataFrame()
                    
                    if not conflicting_appointments.empty:
                        show_error_message("Ya existe una cita programada en esa fecha y hora")
                    else:
                        appointment_id = db.create_appointment(
                            paciente_id=paciente_id,
                            medico_id=medico_id,
                            fecha=fecha_cita.isoformat(),
                            hora=hora_cita.strftime('%H:%M:%S'),
                            motivo=motivo if motivo else None,
                            observaciones=observaciones if observaciones else None
                        )
                        
                        show_success_message(f"Cita creada exitosamente (ID: {appointment_id})")
                
                except Exception as e:
                    show_error_message(f"Error al crear cita: {str(e)}")
            else:
                show_error_message("Por favor complete todos los campos obligatorios")

def show_calendar_view(db, user):
    """Vista de calendario de citas"""
    st.subheader("📅 Calendario de Citas")
    
    # Selector de mes y año
    col1, col2 = st.columns(2)
    
    with col1:
        selected_year = st.selectbox("Año", options=range(2024, 2027), index=1)  # 2025 por defecto
    
    with col2:
        selected_month = st.selectbox("Mes", options=range(1, 13), 
                                    format_func=lambda x: calendar.month_name[x])
    
    # Obtener citas del mes
    start_date = date(selected_year, selected_month, 1)
    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    # Filtro de médico para administradores y recepcionistas
    medico_filter = None
    if user['rol'] in ['administrador', 'recepcionista']:
        df_doctors = db.get_users('doctor')
        doctor_options = ["Todos"] + [f"Dr. {doc['nombre_completo']}" for _, doc in df_doctors.iterrows()]
        selected_doctor = st.selectbox("Filtrar por Médico", options=doctor_options)
        
        if selected_doctor != "Todos":
            doctor_name = selected_doctor.replace("Dr. ", "")
            medico_filter = df_doctors[df_doctors['nombre_completo'] == doctor_name]['id'].iloc[0]
    else:
        medico_filter = user['id']
    
    # Crear calendario simple
    st.write(f"**Citas para {calendar.month_name[selected_month]} {selected_year}**")
    
    # Generar días del mes
    month_calendar = calendar.monthcalendar(selected_year, selected_month)
    
    # Obtener todas las citas del mes
    all_appointments = []
    current_date = start_date
    while current_date <= end_date:
        day_appointments = db.get_appointments(
            date_filter=current_date.isoformat(),
            medico_id=medico_filter
        )
        if not day_appointments.empty:
            all_appointments.append((current_date, len(day_appointments)))
        current_date += timedelta(days=1)
    
    # Mostrar calendario en formato de tabla
    days_of_week = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    # Crear DataFrame para el calendario
    calendar_data = []
    for week in month_calendar:
        week_data = {}
        for i, day in enumerate(week):
            if day == 0:
                week_data[days_of_week[i]] = ""
            else:
                current_day = date(selected_year, selected_month, day)
                appointment_count = next((count for d, count in all_appointments if d == current_day), 0)
                if appointment_count > 0:
                    week_data[days_of_week[i]] = f"{day} ({appointment_count})"
                else:
                    week_data[days_of_week[i]] = str(day)
        calendar_data.append(week_data)
    
    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(calendar_df, use_container_width=True, hide_index=True)
    
    # Leyenda
    st.write("*Los números entre paréntesis indican la cantidad de citas programadas*")
    
    # Vista detallada de un día específico
    st.subheader("🔍 Ver Citas de un Día Específico")
    selected_date = st.date_input("Seleccionar Fecha", value=date.today())
    
    day_appointments = db.get_appointments(
        date_filter=selected_date.isoformat(),
        medico_id=medico_filter
    )
    
    if not day_appointments.empty:
        st.write(f"**Citas para el {format_date(selected_date.isoformat())}:**")
        
        for _, apt in day_appointments.sort_values('hora').iterrows():
            status_colors = {'pendiente': '🟡', 'atendida': '🟢', 'cancelada': '🔴'}
            status_icon = status_colors.get(apt['estado'], '⚪')
            
            st.write(f"{status_icon} **{apt['hora']}** - {apt['paciente_nombre']} (Dr. {apt['medico_nombre']}) - {apt['estado'].title()}")
    else:
        st.info(f"No hay citas programadas para el {format_date(selected_date.isoformat())}")

def show_appointment_stats(db, user):
    """Estadísticas de citas"""
    st.subheader("📊 Estadísticas de Citas")
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Fecha Fin", value=date.today())
    
    # Obtener estadísticas
    medico_filter = user['id'] if user['rol'] == 'doctor' else None
    
    # Métricas por día en el rango
    current_date = start_date
    stats_data = []
    
    while current_date <= end_date:
        day_appointments = db.get_appointments(date_filter=current_date.isoformat(), medico_id=medico_filter)
        
        total = len(day_appointments)
        pendientes = len(day_appointments[day_appointments['estado'] == 'pendiente']) if not day_appointments.empty else 0
        atendidas = len(day_appointments[day_appointments['estado'] == 'atendida']) if not day_appointments.empty else 0
        canceladas = len(day_appointments[day_appointments['estado'] == 'cancelada']) if not day_appointments.empty else 0
        
        stats_data.append({
            'fecha': current_date,
            'total': total,
            'pendientes': pendientes,
            'atendidas': atendidas,
            'canceladas': canceladas
        })
        
        current_date += timedelta(days=1)
    
    df_stats = pd.DataFrame(stats_data)
    
    if not df_stats.empty and df_stats['total'].sum() > 0:
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Citas", df_stats['total'].sum())
        with col2:
            st.metric("Atendidas", df_stats['atendidas'].sum())
        with col3:
            st.metric("Pendientes", df_stats['pendientes'].sum())
        with col4:
            st.metric("Canceladas", df_stats['canceladas'].sum())
        
        # Gráfico de citas por día
        import plotly.express as px
        
        fig = px.line(
            df_stats,
            x='fecha',
            y=['total', 'atendidas', 'pendientes', 'canceladas'],
            title='Citas por Día',
            labels={'value': 'Número de Citas', 'fecha': 'Fecha'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribución por estado
        total_by_status = {
            'Atendidas': df_stats['atendidas'].sum(),
            'Pendientes': df_stats['pendientes'].sum(),
            'Canceladas': df_stats['canceladas'].sum()
        }
        
        fig_pie = px.pie(
            values=list(total_by_status.values()),
            names=list(total_by_status.keys()),
            title='Distribución por Estado'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No hay citas en el rango de fechas seleccionado")

if __name__ == "__main__":
    show_appointment_management()
