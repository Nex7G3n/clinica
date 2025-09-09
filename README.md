# 🏥 Sistema de Gestión Clínica

Sistema completo de gestión para clínicas médicas desarrollado en Python con Streamlit. Incluye gestión de pacientes, citas médicas, historial clínico, pagos y reportes.

## 📋 Características Principales

### 🔐 Autenticación y Roles
- **Administrador**: Acceso completo al sistema
- **Doctor**: Gestión de pacientes, historiales médicos y citas
- **Recepcionista**: Gestión de citas y registro básico de pacientes
- **Paciente**: Consulta de citas e historial simplificado (opcional)

### 👥 Gestión de Pacientes
- Registro completo de pacientes con datos personales y médicos
- Búsqueda por nombre, DNI o historia clínica
- Gestión de documentos médicos
- Control de alergias y enfermedades crónicas

### 📅 Gestión de Citas
- Agenda médica con calendario interactivo
- Estados: pendiente, atendida, cancelada
- Asignación automática por especialidad
- Vista por médico y por día

### 📋 Historial Médico
- Registro completo de consultas
- Generación de recetas en PDF
- Seguimiento de tratamientos
- Búsqueda por diagnóstico

### 💰 Pagos y Facturación
- Registro de pagos por múltiples métodos
- Generación de facturas automáticas
- Reportes de ingresos
- Control de pagos pendientes

### 📊 Reportes y Estadísticas
- Dashboard con métricas en tiempo real
- Reportes por período
- Estadísticas por médico
- Exportación a PDF y Excel

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si tienes git instalado
   git clone <url-del-repositorio>
   cd clinica_app
   
   # O simplemente descargar y extraer el archivo ZIP
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Activar en Windows
   venv\Scripts\activate
   
   # Activar en Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicializar la base de datos**
   ```bash
   python database/init_db.py
   ```

5. **Ejecutar la aplicación**
   ```bash
   streamlit run main.py
   ```

6. **Acceder a la aplicación**
   - Abrir el navegador en: http://localhost:8501
   - Usuario por defecto: `admin`
   - Contraseña por defecto: `admin123`

## 📁 Estructura del Proyecto

```
clinica_app/
├── main.py                    # Archivo principal de la aplicación
├── requirements.txt           # Dependencias del proyecto
├── database/
│   ├── init_db.py            # Inicialización de la base de datos
│   ├── db_manager.py         # Gestor de base de datos
│   └── clinica.db            # Base de datos SQLite (se crea automáticamente)
├── pages/
│   ├── dashboard.py          # Dashboard principal
│   ├── patients.py           # Gestión de pacientes
│   ├── appointments.py       # Gestión de citas
│   ├── medical_history.py    # Historial médico
│   └── payments.py           # Pagos y facturación
└── utils/
    ├── auth.py               # Sistema de autenticación
    └── helpers.py            # Funciones auxiliares
```

## 🔧 Configuración Inicial

### Primer Acceso
1. Inicia sesión con el usuario administrador por defecto
2. Ve a **Configuración** para establecer los datos de la clínica
3. Crea usuarios adicionales desde **Gestión de Usuarios**
4. Configura especialidades médicas si es necesario

### Creación de Usuarios
1. Ve a **Gestión de Usuarios** (solo administradores)
2. Haz clic en "Nuevo Usuario"
3. Completa la información requerida
4. Asigna el rol apropiado

### Configuración de la Clínica
1. Ve a **Configuración**
2. Completa:
   - Nombre de la clínica
   - Dirección y datos de contacto
   - Horarios de atención
   - Logo (opcional)

## 📖 Guía de Uso

### Para Recepcionistas
1. **Registrar Pacientes**: Usar "Gestión de Pacientes" → "Nuevo Paciente"
2. **Agendar Citas**: Usar "Gestión de Citas" → "Nueva Cita"
3. **Gestionar Pagos**: Usar "Pagos y Facturación"

### Para Médicos
1. **Ver Agenda**: Dashboard muestra citas del día
2. **Atender Pacientes**: Marcar citas como atendidas
3. **Registrar Consultas**: "Historial Médico" → "Nueva Consulta"
4. **Generar Recetas**: "Historial Médico" → "Generar Receta"

### Para Administradores
1. **Gestionar Usuarios**: Crear, editar y desactivar usuarios
2. **Ver Reportes**: Acceso completo a estadísticas
3. **Configurar Sistema**: Ajustar parámetros generales

## 🛠️ Personalización

### Modificar la Base de Datos
- Editar `database/init_db.py` para cambiar el esquema
- Ejecutar nuevamente la inicialización

### Agregar Nuevas Páginas
1. Crear archivo en `pages/`
2. Importar en `main.py`
3. Agregar en el sistema de navegación

### Cambiar Estilos
- Modificar CSS en `main.py` en la sección `st.markdown()`

## 🔒 Seguridad

### Contraseñas
- Las contraseñas se almacenan encriptadas con bcrypt
- Cambiar la contraseña por defecto del administrador

### Base de Datos
- Por defecto usa SQLite (archivo local)
- Para producción, considerar PostgreSQL o MySQL

### Copias de Seguridad
- La base de datos está en `database/clinica.db`
- Hacer copias regulares de este archivo

## 🐛 Solución de Problemas

### Error al Iniciar
```bash
# Verificar que las dependencias estén instaladas
pip install -r requirements.txt

# Verificar la versión de Python
python --version  # Debe ser 3.8+
```

### Error de Base de Datos
```bash
# Reinicializar la base de datos
python database/init_db.py
```

### Error de Permisos
- En Windows: Ejecutar como administrador
- En Linux/Mac: Verificar permisos de escritura

## 📞 Soporte

### Funcionalidades Implementadas ✅
- ✅ Sistema de autenticación completo
- ✅ Gestión de pacientes
- ✅ Gestión de citas
- ✅ Dashboard con estadísticas
- ✅ Historial médico básico
- ✅ Generación de recetas PDF
- ✅ Sistema de pagos
- ✅ Roles y permisos

### Funcionalidades Pendientes 🚧
- 🚧 Gestión de documentos médicos
- 🚧 Reportes avanzados
- 🚧 Notificaciones por email/SMS
- 🚧 Backup automático
- 🚧 API REST
- 🚧 Interfaz para pacientes

## 📄 Licencia

Este proyecto está desarrollado para fines educativos y de demostración. Puedes usarlo y modificarlo según tus necesidades.

## 🤝 Contribuciones

Si deseas contribuir al proyecto:
1. Haz fork del repositorio
2. Crea una rama para tu función
3. Realiza los cambios
4. Envía un pull request

---

**Desarrollado con ❤️ usando Streamlit y Python**
