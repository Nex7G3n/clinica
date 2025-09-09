import streamlit as st
from database.db_manager import DatabaseManager
import bcrypt

def check_authentication():
    """Verifica si el usuario está autenticado"""
    return 'user' in st.session_state and st.session_state.user is not None

def check_permission(required_roles):
    """Verifica si el usuario tiene el rol necesario"""
    if not check_authentication():
        return False
    
    user_role = st.session_state.user['rol']
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    return user_role in required_roles

def login_page():
    """Página de login"""
    st.title("🏥 Sistema de Gestión Clínica")
    st.subheader("Iniciar Sesión")
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        login_button = st.form_submit_button("Iniciar Sesión")
        
        if login_button:
            if username and password:
                db = DatabaseManager()
                user = db.authenticate_user(username, password)
                
                if user:
                    st.session_state.user = user
                    st.success(f"¡Bienvenido, {user['nombre_completo']}!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
            else:
                st.error("Por favor ingrese usuario y contraseña")
    
    # Información de usuarios por defecto
    with st.expander("ℹ️ Información de acceso"):
        st.info("""
        **Usuario por defecto:**
        - Usuario: admin
        - Contraseña: admin123
        - Rol: Administrador
        
        Después de iniciar sesión, puede crear más usuarios desde el panel de administración.
        """)

def logout():
    """Cerrar sesión"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.rerun()

def require_auth(required_roles=None):
    """Decorator para requerir autenticación"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_authentication():
                login_page()
                return
            
            if required_roles and not check_permission(required_roles):
                st.error("❌ No tiene permisos para acceder a esta sección")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    if check_authentication():
        return st.session_state.user
    return None

def is_admin():
    """Verifica si el usuario actual es administrador"""
    return check_permission('administrador')

def is_doctor():
    """Verifica si el usuario actual es doctor"""
    return check_permission('doctor')

def is_receptionist():
    """Verifica si el usuario actual es recepcionista"""
    return check_permission('recepcionista')

def can_manage_patients():
    """Verifica si el usuario puede gestionar pacientes"""
    return check_permission(['administrador', 'doctor', 'recepcionista'])

def can_manage_appointments():
    """Verifica si el usuario puede gestionar citas"""
    return check_permission(['administrador', 'doctor', 'recepcionista'])

def can_access_medical_records():
    """Verifica si el usuario puede acceder a historiales médicos"""
    return check_permission(['administrador', 'doctor'])

def can_generate_reports():
    """Verifica si el usuario puede generar reportes"""
    return check_permission(['administrador'])

def sidebar_navigation():
    """Barra lateral de navegación"""
    if not check_authentication():
        return
    
    user = get_current_user()
    
    with st.sidebar:
        st.title("🏥 Clínica")
        st.write(f"👤 {user['nombre_completo']}")
        st.write(f"🏷️ {user['rol'].title()}")
        st.divider()
        
        # Navegación según rol
        pages = []
        
        # Dashboard para todos
        pages.append("📊 Dashboard")
        
        # Gestión de pacientes
        if can_manage_patients():
            pages.append("👥 Gestión de Pacientes")
        
        # Gestión de citas
        if can_manage_appointments():
            pages.append("📅 Gestión de Citas")
        
        # Historial médico
        if can_access_medical_records():
            pages.append("📋 Historial Médico")
        
        # Pagos y facturación
        if check_permission(['administrador', 'recepcionista']):
            pages.append("💰 Pagos y Facturación")
        
        # Reportes
        if can_generate_reports():
            pages.append("📈 Reportes")
        
        # Administración
        if is_admin():
            pages.append("⚙️ Administración")
            pages.append("👥 Gestión de Usuarios")
        
        # Configuración
        if is_admin():
            pages.append("🔧 Configuración")
        
        # Seleccionar página
        selected_page = st.radio("Navegación", pages, key="navigation")
        
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
        
        return selected_page

def show_role_badge(rol):
    """Muestra una insignia del rol del usuario"""
    role_colors = {
        'administrador': '🔴',
        'doctor': '🟢',
        'recepcionista': '🟡',
        'paciente': '🔵'
    }
    
    return f"{role_colors.get(rol, '⚪')} {rol.title()}"
