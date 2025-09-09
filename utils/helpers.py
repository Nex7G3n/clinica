import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from fpdf import FPDF
import io
import base64

class PDFGenerator:
    """Generador de PDFs para recetas, facturas y reportes"""
    
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
    
    def generate_prescription(self, patient_data, doctor_data, prescription_data):
        """Genera una receta médica en PDF"""
        
        # Encabezado
        self.pdf.cell(0, 10, 'RECETA MEDICA', 0, 1, 'C')
        self.pdf.ln(10)
        
        # Información del doctor
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, f"Dr. {doctor_data['nombre_completo']}", 0, 1)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, f"Especialidad: {doctor_data['especialidad']}", 0, 1)
        self.pdf.ln(5)
        
        # Información del paciente
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Paciente:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, patient_data['nombre_completo'], 0, 1)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'DNI:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, patient_data['dni'], 0, 1)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Fecha:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, datetime.now().strftime('%d/%m/%Y'), 0, 1)
        self.pdf.ln(10)
        
        # Prescripción
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 8, 'PRESCRIPCION:', 0, 1)
        self.pdf.set_font('Arial', '', 10)
        
        # Dividir el texto en líneas
        prescription_lines = prescription_data['receta'].split('\n')
        for line in prescription_lines:
            self.pdf.cell(0, 6, line, 0, 1)
        
        return self.pdf.output(dest='S').encode('latin1')
    
    def generate_invoice(self, payment_data, patient_data, clinic_config):
        """Genera una factura en PDF"""
        
        # Encabezado
        self.pdf.cell(0, 10, clinic_config.get('nombre_clinica', 'CLINICA MEDICA'), 0, 1, 'C')
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, clinic_config.get('direccion', ''), 0, 1, 'C')
        self.pdf.cell(0, 6, f"Tel: {clinic_config.get('telefono', '')}", 0, 1, 'C')
        self.pdf.ln(10)
        
        # Título
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, 'FACTURA', 0, 1, 'C')
        self.pdf.ln(5)
        
        # Información del paciente
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Cliente:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, patient_data['nombre_completo'], 0, 1)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'DNI:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, patient_data['dni'], 0, 1)
        
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(40, 6, 'Fecha:', 0, 0)
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(0, 6, datetime.now().strftime('%d/%m/%Y'), 0, 1)
        self.pdf.ln(10)
        
        # Detalles del pago
        self.pdf.set_font('Arial', 'B', 10)
        self.pdf.cell(80, 8, 'Descripcion', 1, 0, 'C')
        self.pdf.cell(40, 8, 'Metodo Pago', 1, 0, 'C')
        self.pdf.cell(30, 8, 'Monto', 1, 1, 'C')
        
        self.pdf.set_font('Arial', '', 10)
        self.pdf.cell(80, 8, 'Consulta Medica', 1, 0)
        self.pdf.cell(40, 8, payment_data['metodo_pago'].title(), 1, 0, 'C')
        self.pdf.cell(30, 8, f"${payment_data['monto']:.2f}", 1, 1, 'R')
        
        # Total
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(120, 10, 'TOTAL:', 1, 0, 'R')
        self.pdf.cell(30, 10, f"${payment_data['monto']:.2f}", 1, 1, 'R')
        
        return self.pdf.output(dest='S').encode('latin1')

def create_chart_appointments_by_day(df_appointments):
    """Crea gráfico de citas por día"""
    if df_appointments.empty:
        return None
    
    daily_appointments = df_appointments.groupby('fecha').size().reset_index(name='total_citas')
    
    fig = px.bar(
        daily_appointments,
        x='fecha',
        y='total_citas',
        title='Citas por Día',
        labels={'fecha': 'Fecha', 'total_citas': 'Número de Citas'}
    )
    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Citas",
        showlegend=False
    )
    
    return fig

def create_chart_patients_by_age(df_patients):
    """Crea gráfico de pacientes por rango de edad"""
    if df_patients.empty:
        return None
    
    # Calcular edades
    today = datetime.now().date()
    df_patients['edad'] = df_patients['fecha_nacimiento'].apply(
        lambda x: today.year - datetime.strptime(x, '%Y-%m-%d').date().year
    )
    
    # Crear rangos de edad
    def age_group(age):
        if age < 18:
            return '0-17'
        elif age < 30:
            return '18-29'
        elif age < 50:
            return '30-49'
        elif age < 65:
            return '50-64'
        else:
            return '65+'
    
    df_patients['rango_edad'] = df_patients['edad'].apply(age_group)
    age_counts = df_patients['rango_edad'].value_counts()
    
    fig = px.pie(
        values=age_counts.values,
        names=age_counts.index,
        title='Distribución de Pacientes por Edad'
    )
    
    return fig

def create_chart_payments_by_method(df_payments):
    """Crea gráfico de pagos por método"""
    if df_payments.empty:
        return None
    
    payment_counts = df_payments['metodo_pago'].value_counts()
    
    fig = px.pie(
        values=payment_counts.values,
        names=payment_counts.index,
        title='Pagos por Método de Pago'
    )
    
    return fig

def create_chart_monthly_revenue(df_payments):
    """Crea gráfico de ingresos mensuales"""
    if df_payments.empty:
        return None
    
    # Extraer mes de la fecha de pago
    df_payments['mes'] = pd.to_datetime(df_payments['fecha_pago']).dt.strftime('%Y-%m')
    monthly_revenue = df_payments.groupby('mes')['monto'].sum().reset_index()
    
    fig = px.line(
        monthly_revenue,
        x='mes',
        y='monto',
        title='Ingresos Mensuales',
        labels={'mes': 'Mes', 'monto': 'Ingresos ($)'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Ingresos ($)",
        showlegend=False
    )
    
    return fig

def export_to_excel(dataframes_dict, filename):
    """Exporta múltiples DataFrames a un archivo Excel"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output.getvalue()

def create_download_link(data, filename, link_text):
    """Crea un enlace de descarga para datos binarios"""
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{link_text}</a>'

def validate_email(email):
    """Valida formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valida formato de teléfono"""
    import re
    pattern = r'^[\d\s\-\+\(\)]+$'
    return re.match(pattern, phone) is not None and len(phone.replace(' ', '').replace('-', '')) >= 7

def validate_dni(dni):
    """Valida formato de DNI"""
    import re
    pattern = r'^\d{8,12}$'  # Entre 8 y 12 dígitos
    return re.match(pattern, dni) is not None

def show_success_message(message):
    """Muestra mensaje de éxito"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Muestra mensaje de error"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Muestra mensaje de advertencia"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Muestra mensaje informativo"""
    st.info(f"ℹ️ {message}")

def format_currency(amount):
    """Formatea cantidad como moneda"""
    return f"${amount:,.2f}"

def format_date(date_str):
    """Formatea una fecha para mostrar"""
    from datetime import datetime
    try:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        return date_str
    except:
        return date_str

def format_datetime(datetime_str):
    """Formatea una fecha y hora para mostrar"""
    from datetime import datetime
    try:
        if isinstance(datetime_str, str):
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            return datetime_obj.strftime('%d/%m/%Y %H:%M')
        return datetime_str
    except:
        return datetime_str

def get_age_from_birthdate(birthdate_str):
    """Calcula la edad a partir de la fecha de nacimiento"""
    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        return age
    except:
        return None

def paginate_dataframe(df, page_size=10):
    """Pagina un DataFrame"""
    if df.empty:
        return df, 0, 0
    
    total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    start_idx = (st.session_state.current_page - 1) * page_size
    end_idx = start_idx + page_size
    
    return df.iloc[start_idx:end_idx], st.session_state.current_page, total_pages

def show_pagination_controls(current_page, total_pages):
    """Muestra controles de paginación"""
    if total_pages <= 1:
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page > 1:
            if st.button("← Anterior"):
                st.session_state.current_page -= 1
                st.rerun()
    
    with col2:
        st.write(f"Página {current_page} de {total_pages}")
    
    with col3:
        if current_page < total_pages:
            if st.button("Siguiente →"):
                st.session_state.current_page += 1
                st.rerun()
