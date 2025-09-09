import sqlite3
import os
from datetime import datetime

def init_database():
    """Inicializa la base de datos con todas las tablas necesarias"""
    db_path = "database/clinica.db"
    
    # Crear directorio de base de datos si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de usuarios (administrador, doctor, recepcionista, paciente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('administrador', 'doctor', 'recepcionista', 'paciente')),
            nombre_completo TEXT NOT NULL,
            especialidad TEXT,
            telefono TEXT,
            estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo', 'inactivo')),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de pacientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            fecha_nacimiento DATE NOT NULL,
            sexo TEXT NOT NULL CHECK(sexo IN ('M', 'F', 'Otro')),
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            grupo_sanguineo TEXT,
            alergias TEXT,
            enfermedades_cronicas TEXT,
            estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo', 'inactivo')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabla de citas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            medico_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'atendida', 'cancelada')),
            motivo TEXT,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (medico_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabla de historial médico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_medico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            cita_id INTEGER,
            medico_id INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            motivo_consulta TEXT NOT NULL,
            diagnostico TEXT,
            receta TEXT,
            examenes_solicitados TEXT,
            observaciones TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (cita_id) REFERENCES citas (id),
            FOREIGN KEY (medico_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Tabla de pagos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cita_id INTEGER NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('efectivo', 'tarjeta', 'transferencia')),
            estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'pagado', 'cancelado')),
            fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observaciones TEXT,
            FOREIGN KEY (cita_id) REFERENCES citas (id)
        )
    ''')
    
    # Tabla de configuración
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_clinica TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            logo_path TEXT,
            horario_inicio TIME DEFAULT '08:00',
            horario_fin TIME DEFAULT '18:00',
            duracion_cita INTEGER DEFAULT 30
        )
    ''')
    
    # Tabla de especialidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS especialidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo', 'inactivo'))
        )
    ''')
    
    # Tabla de documentos médicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos_medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            nombre_archivo TEXT NOT NULL,
            tipo_documento TEXT,
            ruta_archivo TEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subido_por INTEGER,
            FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
            FOREIGN KEY (subido_por) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_initial_data():
    """Inserta datos iniciales en la base de datos"""
    import bcrypt
    
    conn = sqlite3.connect("database/clinica.db")
    cursor = conn.cursor()
    
    # Usuario administrador por defecto
    admin_password = "admin123"
    admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios 
        (username, email, password_hash, rol, nombre_completo, especialidad)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@clinica.com', admin_hash, 'administrador', 'Administrador Principal', 'Administración'))
    
    # Especialidades por defecto
    especialidades_default = [
        'Medicina General',
        'Cardiología',
        'Dermatología',
        'Pediatría',
        'Ginecología',
        'Neurología',
        'Oftalmología',
        'Traumatología'
    ]
    
    for esp in especialidades_default:
        cursor.execute('INSERT OR IGNORE INTO especialidades (nombre) VALUES (?)', (esp,))
    
    # Configuración por defecto
    cursor.execute('''
        INSERT OR IGNORE INTO configuracion 
        (nombre_clinica, direccion, telefono, email)
        VALUES (?, ?, ?, ?)
    ''', ('Clínica Médica', 'Dirección de la Clínica', '123-456-7890', 'contacto@clinica.com'))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    insert_initial_data()
    print("Base de datos inicializada correctamente")
