import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager
from utils.auth import get_current_user, require_auth
from utils.helpers import create_chart_appointments_by_day, create_chart_patients_by_age, format_currency
import plotly.express as px

@require_auth()
def show_dashboard():
    """Muestra el dashboard principal"""
    st.title("📊 Dashboard")
    
    db = DatabaseManager()
    user = get_current_user()
    
    # Obtener estadísticas generales
    stats = db.get_stats_dashboard()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Pacientes Activos",
            value=stats['total_pacientes']
        )
    
    with col2:
        st.metric(
            label="📅 Citas Hoy",
            value=stats['citas_hoy']
        )
    
    with col3:
        st.metric(
            label="👨‍⚕️ Médicos Activos",
            value=stats['total_medicos']
        )
    
    with col4:
        st.metric(
            label="💰 Ingresos del Mes",
            value=format_currency(stats['ingresos_mes'])
        )
    
    st.divider()
    
    # Gráficos según el rol del usuario
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Citas de la Semana")
        
        # Obtener citas de los últimos 7 días
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Si es doctor, mostrar solo sus citas
        medico_id = user['id'] if user['rol'] == 'doctor' else None
        
        appointments_week = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            df_day = db.get_appointments(date_filter=current_date.isoformat(), medico_id=medico_id)
            appointments_week.append({
                'fecha': current_date.strftime('%d/%m'),
                'citas': len(df_day)
            })
        
        df_week = pd.DataFrame(appointments_week)
        
        if not df_week.empty:
            fig = px.bar(
                df_week,
                x='fecha',
                y='citas',
                title='Citas por Día (Última Semana)',
                color='citas',
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de citas para mostrar")
    
    with col2:
        st.subheader("👥 Distribución de Pacientes")
        
        # Solo mostrar si tiene permisos para ver todos los pacientes
        if user['rol'] in ['administrador', 'recepcionista']:
            df_patients = db.get_patients()
            
            if not df_patients.empty:
                # Distribución por sexo
                gender_counts = df_patients['sexo'].value_counts()
                
                fig = px.pie(
                    values=gender_counts.values,
                    names=['Masculino' if x == 'M' else 'Femenino' if x == 'F' else 'Otro' for x in gender_counts.index],
                    title='Pacientes por Sexo'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de pacientes para mostrar")
        else:
            st.info("Sin permisos para ver estadísticas de pacientes")
    
    # Citas del día actual
    st.subheader("📋 Citas de Hoy")
    
    today = date.today().isoformat()
    medico_filter = user['id'] if user['rol'] == 'doctor' else None
    df_today = db.get_appointments(date_filter=today, medico_id=medico_filter)
    
    if not df_today.empty:
        # Ordenar por hora
        df_today = df_today.sort_values('hora')
        
        for index, row in df_today.iterrows():
            status_color = {
                'pendiente': '🟡',
                'atendida': '🟢',
                'cancelada': '🔴'
            }
            
            with st.expander(
                f"{status_color.get(row['estado'], '⚪')} {row['hora']} - {row['paciente_nombre']} ({row['estado'].upper()})"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Paciente:** {row['paciente_nombre']}")
                    st.write(f"**DNI:** {row['dni']}")
                    st.write(f"**Médico:** {row['medico_nombre']}")
                
                with col2:
                    st.write(f"**Estado:** {row['estado'].title()}")
                    st.write(f"**Motivo:** {row['motivo'] or 'No especificado'}")
                    if row['observaciones']:
                        st.write(f"**Observaciones:** {row['observaciones']}")
                
                # Acciones rápidas para médicos
                if user['rol'] == 'doctor' and row['estado'] == 'pendiente':
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Marcar como Atendida", key=f"attend_{row['id']}"):
                            db.update_appointment_status(row['id'], 'atendida')
                            st.success("Cita marcada como atendida")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"❌ Cancelar", key=f"cancel_{row['id']}"):
                            db.update_appointment_status(row['id'], 'cancelada', 'Cancelada por el médico')
                            st.success("Cita cancelada")
                            st.rerun()
    else:
        st.info("No hay citas programadas para hoy")
    
    # Próximas citas (solo para médicos)
    if user['rol'] == 'doctor':
        st.subheader("🔮 Próximas Citas")
        
        # Obtener citas de los próximos 3 días
        future_appointments = []
        for i in range(1, 4):  # Próximos 3 días
            future_date = (date.today() + timedelta(days=i)).isoformat()
            df_future = db.get_appointments(date_filter=future_date, medico_id=user['id'])
            if not df_future.empty:
                future_appointments.append(df_future)
        
        if future_appointments:
            df_future_all = pd.concat(future_appointments, ignore_index=True)
            df_future_all = df_future_all.sort_values(['fecha', 'hora'])
            
            for index, row in df_future_all.head(5).iterrows():  # Mostrar solo las próximas 5
                st.write(f"📅 **{row['fecha']}** a las **{row['hora']}** - {row['paciente_nombre']}")
        else:
            st.info("No hay citas programadas para los próximos días")
    
    # Recordatorios y notificaciones
    st.subheader("🔔 Notificaciones")
    
    notifications = []
    
    # Verificar citas sin atender del día anterior
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    medico_filter = user['id'] if user['rol'] == 'doctor' else None
    df_yesterday = db.get_appointments(date_filter=yesterday, medico_id=medico_filter, estado='pendiente')
    
    if not df_yesterday.empty:
        notifications.append({
            'type': 'warning',
            'message': f"Hay {len(df_yesterday)} citas pendientes del día anterior"
        })
    
    # Verificar pacientes sin historial médico reciente (para médicos)
    if user['rol'] == 'doctor':
        # Esta sería una consulta más compleja, por simplicidad se omite
        pass
    
    if notifications:
        for notif in notifications:
            if notif['type'] == 'warning':
                st.warning(notif['message'])
            elif notif['type'] == 'info':
                st.info(notif['message'])
    else:
        st.success("✅ No hay notificaciones pendientes")

if __name__ == "__main__":
    show_dashboard()
