import streamlit as st
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Gestión Clínica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos después de configurar la página
from database.init_db import init_database, insert_initial_data
from utils.auth import check_authentication, sidebar_navigation, login_page
from pages.dashboard import show_dashboard
from pages.patients import show_patient_management
from pages.appointments import show_appointment_management

# Importar otras páginas
import importlib

def load_medical_history():
    """Carga la página de historial médico"""
    try:
        from pages.medical_history import show_medical_history
        return show_medical_history
    except ImportError:
        return None

def load_payments():
    """Carga la página de pagos"""
    try:
        from pages.payments import show_payments
        return show_payments
    except ImportError:
        return None

def load_reports():
    """Carga la página de reportes"""
    try:
        from pages.reports import show_reports
        return show_reports
    except ImportError:
        return None

def load_admin():
    """Carga la página de administración"""
    try:
        from pages.admin import show_admin
        return show_admin
    except ImportError:
        return None

def load_users():
    """Carga la página de gestión de usuarios"""
    try:
        from pages.users import show_user_management
        return show_user_management
    except ImportError:
        return None

def load_config():
    """Carga la página de configuración"""
    try:
        from pages.config import show_configuration
        return show_configuration
    except ImportError:
        return None

def main():
    """Función principal de la aplicación"""
    
    # Inicializar base de datos si no existe
    try:
        init_database()
        insert_initial_data()
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
        st.stop()
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid #e6e6e6;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-pending {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-completed {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-cancelled {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8fafc;
    }
    
    .stButton > button {
        width: 100%;
    }
    
    .success-message {
        padding: 0.75rem;
        background-color: #d1fae5;
        border: 1px solid #a7f3d0;
        border-radius: 0.375rem;
        color: #065f46;
    }
    
    .error-message {
        padding: 0.75rem;
        background-color: #fee2e2;
        border: 1px solid #fecaca;
        border-radius: 0.375rem;
        color: #991b1b;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Verificar autenticación
    if not check_authentication():
        login_page()
        return
    
    # Navegación lateral
    selected_page = sidebar_navigation()
    
    # Enrutamiento de páginas
    try:
        if selected_page == "📊 Dashboard":
            show_dashboard()
            
        elif selected_page == "👥 Gestión de Pacientes":
            show_patient_management()
            
        elif selected_page == "📅 Gestión de Citas":
            show_appointment_management()
            
        elif selected_page == "📋 Historial Médico":
            medical_history_func = load_medical_history()
            if medical_history_func:
                medical_history_func()
            else:
                st.error("Página de historial médico no disponible")
                create_placeholder_page("Historial Médico", "📋")
                
        elif selected_page == "💰 Pagos y Facturación":
            payments_func = load_payments()
            if payments_func:
                payments_func()
            else:
                create_placeholder_page("Pagos y Facturación", "💰")
                
        elif selected_page == "📈 Reportes":
            reports_func = load_reports()
            if reports_func:
                reports_func()
            else:
                create_placeholder_page("Reportes", "📈")
                
        elif selected_page == "⚙️ Administración":
            admin_func = load_admin()
            if admin_func:
                admin_func()
            else:
                create_placeholder_page("Administración", "⚙️")
                
        elif selected_page == "👥 Gestión de Usuarios":
            users_func = load_users()
            if users_func:
                users_func()
            else:
                create_placeholder_page("Gestión de Usuarios", "👥")
                
        elif selected_page == "🔧 Configuración":
            config_func = load_config()
            if config_func:
                config_func()
            else:
                create_placeholder_page("Configuración", "🔧")
                
    except Exception as e:
        st.error(f"Error al cargar la página: {e}")
        st.error("Por favor, contacte al administrador del sistema")

def create_placeholder_page(page_name, icon):
    """Crea una página placeholder para funcionalidades en desarrollo"""
    st.title(f"{icon} {page_name}")
    
    st.info(f"La página de {page_name} está en desarrollo.")
    st.write("Esta funcionalidad se agregará en futuras versiones de la aplicación.")
    
    # Mostrar información de lo que incluiría esta página
    if page_name == "Historial Médico":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Consulta de historial médico completo por paciente")
        st.write("- Registro de nuevas consultas médicas")
        st.write("- Generación de recetas médicas en PDF")
        st.write("- Seguimiento de tratamientos")
        st.write("- Búsqueda de historiales por diagnóstico")
        
    elif page_name == "Pagos y Facturación":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Registro de pagos por consulta")
        st.write("- Generación de facturas")
        st.write("- Control de métodos de pago")
        st.write("- Reportes de ingresos")
        st.write("- Seguimiento de pagos pendientes")
        
    elif page_name == "Reportes":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Reporte de pacientes atendidos por período")
        st.write("- Estadísticas de consultas por médico")
        st.write("- Diagnósticos más frecuentes")
        st.write("- Análisis de ingresos")
        st.write("- Exportación de reportes en PDF y Excel")
        
    elif page_name == "Administración":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Gestión de especialidades médicas")
        st.write("- Configuración de horarios de atención")
        st.write("- Backup y restauración de datos")
        st.write("- Logs del sistema")
        st.write("- Mantenimiento de la base de datos")
        
    elif page_name == "Gestión de Usuarios":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Creación y edición de usuarios")
        st.write("- Asignación de roles y permisos")
        st.write("- Reseteo de contraseñas")
        st.write("- Activación/desactivación de usuarios")
        st.write("- Auditoría de accesos")
        
    elif page_name == "Configuración":
        st.subheader("Funcionalidades planeadas:")
        st.write("- Información de la clínica")
        st.write("- Configuración de horarios")
        st.write("- Personalización de la interfaz")
        st.write("- Configuración de notificaciones")
        st.write("- Parámetros del sistema")

if __name__ == "__main__":
    main()
