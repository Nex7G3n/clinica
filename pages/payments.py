import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager
from utils.auth import require_auth, get_current_user
from utils.helpers import (
    show_success_message, show_error_message, format_currency, 
    create_chart_payments_by_method, create_chart_monthly_revenue,
    PDFGenerator
)

@require_auth(['administrador', 'recepcionista'])
def show_payments():
    """Página de gestión de pagos"""
    st.title("💰 Pagos y Facturación")
    
    db = DatabaseManager()
    user = get_current_user()
    
    # Tabs para diferentes funciones
    tab1, tab2, tab3, tab4 = st.tabs(["💳 Registrar Pago", "📋 Lista de Pagos", "📊 Estadísticas", "🧾 Facturación"])
    
    with tab1:
        show_payment_form(db, user)
    
    with tab2:
        show_payments_list(db, user)
    
    with tab3:
        show_payment_statistics(db, user)
    
    with tab4:
        show_invoicing(db, user)

def show_payment_form(db, user):
    """Formulario para registrar pagos"""
    st.subheader("💳 Registrar Nuevo Pago")
    
    # Obtener citas atendidas sin pago
    today = date.today()
    start_date = today - timedelta(days=30)  # Últimos 30 días
    
    # Aquí se necesitaría una consulta más compleja para obtener citas sin pago
    # Por simplicidad, obtenemos todas las citas atendidas
    df_appointments = db.get_appointments(estado='atendida')
    
    if df_appointments.empty:
        st.info("No hay citas atendidas disponibles para registrar pagos")
        return
    
    with st.form("payment_form", clear_on_submit=True):
        # Selector de cita
        appointment_options = {}
        for _, apt in df_appointments.iterrows():
            date_str = apt['fecha']
            appointment_options[f"{date_str} - {apt['paciente_nombre']} - Dr. {apt['medico_nombre']}"] = apt['id']
        
        selected_appointment_key = st.selectbox(
            "Seleccionar Cita *",
            options=list(appointment_options.keys())
        )
        
        # Información del pago
        col1, col2 = st.columns(2)
        
        with col1:
            monto = st.number_input("Monto a Pagar *", min_value=0.0, step=0.01, format="%.2f")
            metodo_pago = st.selectbox("Método de Pago *", options=["efectivo", "tarjeta", "transferencia"])
        
        with col2:
            fecha_pago = st.date_input("Fecha de Pago", value=date.today())
            hora_pago = st.time_input("Hora de Pago", value=datetime.now().time())
        
        observaciones = st.text_area("Observaciones", max_chars=500)
        
        submitted = st.form_submit_button("💰 Registrar Pago", use_container_width=True)
        
        if submitted:
            if selected_appointment_key and monto > 0:
                try:
                    cita_id = appointment_options[selected_appointment_key]
                    
                    payment_id = db.create_payment(
                        cita_id=cita_id,
                        monto=monto,
                        metodo_pago=metodo_pago,
                        observaciones=observaciones if observaciones else None
                    )
                    
                    show_success_message(f"Pago registrado exitosamente (ID: {payment_id})")
                    
                except Exception as e:
                    show_error_message(f"Error al registrar pago: {str(e)}")
            else:
                show_error_message("Por favor complete todos los campos obligatorios")

def show_payments_list(db, user):
    """Lista de pagos registrados"""
    st.subheader("📋 Lista de Pagos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("Fecha Fin", value=date.today())
    
    with col3:
        if st.button("🔍 Filtrar", use_container_width=True):
            st.rerun()
    
    # Obtener pagos
    df_payments = db.get_payments(start_date.isoformat(), end_date.isoformat())
    
    if df_payments.empty:
        st.info("No se encontraron pagos en el rango de fechas seleccionado")
        return
    
    # Mostrar resumen
    total_pagos = len(df_payments)
    total_monto = df_payments['monto'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pagos", total_pagos)
    with col2:
        st.metric("Monto Total", format_currency(total_monto))
    with col3:
        promedio = total_monto / total_pagos if total_pagos > 0 else 0
        st.metric("Promedio por Pago", format_currency(promedio))
    
    st.divider()
    
    # Tabla de pagos
    df_display = df_payments[[
        'fecha_pago', 'paciente_nombre', 'medico_nombre', 
        'monto', 'metodo_pago', 'observaciones'
    ]].copy()
    
    df_display.columns = [
        'Fecha Pago', 'Paciente', 'Médico', 
        'Monto', 'Método', 'Observaciones'
    ]
    
    # Formatear monto
    df_display['Monto'] = df_display['Monto'].apply(lambda x: format_currency(x))
    df_display['Método'] = df_display['Método'].str.title()
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Botón de exportación
    if st.button("📥 Exportar a Excel"):
        try:
            from utils.helpers import export_to_excel
            
            excel_data = export_to_excel(
                {'Pagos': df_payments},
                f'pagos_{start_date}_{end_date}.xlsx'
            )
            
            st.download_button(
                label="📥 Descargar Excel",
                data=excel_data,
                file_name=f'pagos_{start_date}_{end_date}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except ImportError:
            st.error("Funcionalidad de exportación no disponible")

def show_payment_statistics(db, user):
    """Estadísticas de pagos"""
    st.subheader("📊 Estadísticas de Pagos")
    
    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=90), key="stats_start")
    
    with col2:
        end_date = st.date_input("Fecha Fin", value=date.today(), key="stats_end")
    
    # Obtener datos
    df_payments = db.get_payments(start_date.isoformat(), end_date.isoformat())
    
    if df_payments.empty:
        st.info("No hay datos de pagos para mostrar estadísticas")
        return
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pagos", len(df_payments))
    
    with col2:
        total_ingresos = df_payments['monto'].sum()
        st.metric("Ingresos Totales", format_currency(total_ingresos))
    
    with col3:
        promedio_diario = total_ingresos / ((end_date - start_date).days + 1)
        st.metric("Promedio Diario", format_currency(promedio_diario))
    
    with col4:
        pago_promedio = df_payments['monto'].mean()
        st.metric("Pago Promedio", format_currency(pago_promedio))
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pagos por Método")
        fig_methods = create_chart_payments_by_method(df_payments)
        if fig_methods:
            st.plotly_chart(fig_methods, use_container_width=True)
    
    with col2:
        st.subheader("Ingresos por Médico")
        revenue_by_doctor = df_payments.groupby('medico_nombre')['monto'].sum().reset_index()
        revenue_by_doctor = revenue_by_doctor.sort_values('monto', ascending=False)
        
        if not revenue_by_doctor.empty:
            import plotly.express as px
            fig = px.bar(
                revenue_by_doctor,
                x='medico_nombre',
                y='monto',
                title='Ingresos por Médico'
            )
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tendencia mensual
    st.subheader("Tendencia de Ingresos")
    fig_monthly = create_chart_monthly_revenue(df_payments)
    if fig_monthly:
        st.plotly_chart(fig_monthly, use_container_width=True)

def show_invoicing(db, user):
    """Generación de facturas"""
    st.subheader("🧾 Generación de Facturas")
    
    # Obtener configuración de la clínica
    clinic_config = db.get_clinic_config()
    if not clinic_config:
        st.warning("⚠️ No se ha configurado la información de la clínica. Vaya a Configuración para completar los datos.")
        clinic_config = {
            'nombre_clinica': 'Clínica Médica',
            'direccion': 'Dirección no configurada',
            'telefono': 'Teléfono no configurado',
            'email': 'email@clinica.com'
        }
    
    # Selector de pago para facturar
    df_payments = db.get_payments()
    
    if df_payments.empty:
        st.info("No hay pagos registrados para generar facturas")
        return
    
    payment_options = {}
    for _, payment in df_payments.iterrows():
        payment_info = f"{payment['fecha_pago']} - {payment['paciente_nombre']} - {format_currency(payment['monto'])}"
        payment_options[payment_info] = payment['id']
    
    selected_payment_key = st.selectbox(
        "Seleccionar Pago para Facturar",
        options=list(payment_options.keys())
    )
    
    if selected_payment_key:
        payment_id = payment_options[selected_payment_key]
        
        # Obtener datos del pago seleccionado
        selected_payment = df_payments[df_payments['id'] == payment_id].iloc[0]
        
        # Mostrar información del pago
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Información del Pago:**")
            st.write(f"Fecha: {selected_payment['fecha_pago']}")
            st.write(f"Paciente: {selected_payment['paciente_nombre']}")
            st.write(f"Médico: {selected_payment['medico_nombre']}")
        
        with col2:
            st.write(f"Monto: {format_currency(selected_payment['monto'])}")
            st.write(f"Método: {selected_payment['metodo_pago'].title()}")
            if selected_payment['observaciones']:
                st.write(f"Observaciones: {selected_payment['observaciones']}")
        
        # Generar factura
        if st.button("📄 Generar Factura PDF", use_container_width=True):
            try:
                # Obtener datos del paciente
                # Esto requeriría una consulta adicional para obtener el paciente por nombre
                # Por simplicidad, simulamos los datos del paciente
                patient_data = {
                    'nombre_completo': selected_payment['paciente_nombre'],
                    'dni': '12345678'  # Esto debería obtenerse de la base de datos
                }
                
                # Generar PDF
                pdf_generator = PDFGenerator()
                pdf_bytes = pdf_generator.generate_invoice(
                    selected_payment.to_dict(),
                    patient_data,
                    clinic_config
                )
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Factura PDF",
                    data=pdf_bytes,
                    file_name=f"factura_{payment_id}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                show_success_message("Factura generada exitosamente")
                
            except Exception as e:
                show_error_message(f"Error al generar factura: {str(e)}")

if __name__ == "__main__":
    show_payments()
