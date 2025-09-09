import sqlite3
import bcrypt
from datetime import datetime, date, time
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path="database/clinica.db"):
        self.db_path = db_path
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    # MÉTODOS DE AUTENTICACIÓN
    def authenticate_user(self, username, password):
        """Autentica un usuario y devuelve sus datos si es válido"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, password_hash, rol, nombre_completo, especialidad, estado
            FROM usuarios WHERE username = ?
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and user[7] == 'activo':  # Verificar que el usuario esté activo
            stored_hash = user[3].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'rol': user[4],
                    'nombre_completo': user[5],
                    'especialidad': user[6],
                    'estado': user[7]
                }
        return None
    
    def create_user(self, username, email, password, rol, nombre_completo, especialidad=None):
        """Crea un nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO usuarios (username, email, password_hash, rol, nombre_completo, especialidad)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, rol, nombre_completo, especialidad))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise e
    
    def get_users(self, rol=None):
        """Obtiene lista de usuarios, opcionalmente filtrada por rol"""
        conn = self.get_connection()
        
        if rol:
            query = "SELECT * FROM usuarios WHERE rol = ? AND estado = 'activo'"
            df = pd.read_sql_query(query, conn, params=[rol])
        else:
            query = "SELECT * FROM usuarios WHERE estado = 'activo'"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    # MÉTODOS DE PACIENTES
    def create_patient(self, dni, nombre_completo, fecha_nacimiento, sexo, telefono=None, 
                      direccion=None, email=None, grupo_sanguineo=None, alergias=None, 
                      enfermedades_cronicas=None, usuario_id=None):
        """Crea un nuevo paciente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pacientes 
                (dni, nombre_completo, fecha_nacimiento, sexo, telefono, direccion, 
                email, grupo_sanguineo, alergias, enfermedades_cronicas, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (dni, nombre_completo, fecha_nacimiento, sexo, telefono, direccion,
                  email, grupo_sanguineo, alergias, enfermedades_cronicas, usuario_id))
            
            patient_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return patient_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise e
    
    def get_patients(self, search_term=None):
        """Obtiene lista de pacientes con búsqueda opcional"""
        conn = self.get_connection()
        
        if search_term:
            query = '''
                SELECT * FROM pacientes 
                WHERE (nombre_completo LIKE ? OR dni LIKE ?) AND estado = 'activo'
                ORDER BY nombre_completo
            '''
            search_pattern = f"%{search_term}%"
            df = pd.read_sql_query(query, conn, params=[search_pattern, search_pattern])
        else:
            query = "SELECT * FROM pacientes WHERE estado = 'activo' ORDER BY nombre_completo"
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def get_patient_by_id(self, patient_id):
        """Obtiene un paciente por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        
        if patient:
            columns = ['id', 'dni', 'nombre_completo', 'fecha_nacimiento', 'sexo', 
                      'telefono', 'direccion', 'email', 'grupo_sanguineo', 'alergias', 
                      'enfermedades_cronicas', 'estado', 'fecha_registro', 'usuario_id']
            return dict(zip(columns, patient))
        return None
    
    def update_patient(self, patient_id, **kwargs):
        """Actualiza un paciente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        fields = []
        values = []
        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(patient_id)
            query = f"UPDATE pacientes SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    # MÉTODOS DE CITAS
    def create_appointment(self, paciente_id, medico_id, fecha, hora, motivo=None, observaciones=None):
        """Crea una nueva cita"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO citas (paciente_id, medico_id, fecha, hora, motivo, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (paciente_id, medico_id, fecha, hora, motivo, observaciones))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id
    
    def get_appointments(self, date_filter=None, medico_id=None, estado=None):
        """Obtiene lista de citas con filtros opcionales"""
        conn = self.get_connection()
        
        query = '''
            SELECT c.*, p.nombre_completo as paciente_nombre, p.dni,
                   u.nombre_completo as medico_nombre
            FROM citas c
            JOIN pacientes p ON c.paciente_id = p.id
            JOIN usuarios u ON c.medico_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if date_filter:
            query += " AND c.fecha = ?"
            params.append(date_filter)
        
        if medico_id:
            query += " AND c.medico_id = ?"
            params.append(medico_id)
            
        if estado:
            query += " AND c.estado = ?"
            params.append(estado)
        
        query += " ORDER BY c.fecha, c.hora"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def update_appointment_status(self, appointment_id, estado, observaciones=None):
        """Actualiza el estado de una cita"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if observaciones:
            cursor.execute('''
                UPDATE citas SET estado = ?, observaciones = ? WHERE id = ?
            ''', (estado, observaciones, appointment_id))
        else:
            cursor.execute('''
                UPDATE citas SET estado = ? WHERE id = ?
            ''', (estado, appointment_id))
        
        conn.commit()
        conn.close()
    
    # MÉTODOS DE HISTORIAL MÉDICO
    def create_medical_record(self, paciente_id, medico_id, motivo_consulta, diagnostico=None, 
                            receta=None, examenes_solicitados=None, observaciones=None, cita_id=None):
        """Crea un nuevo registro médico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO historial_medico 
            (paciente_id, cita_id, medico_id, motivo_consulta, diagnostico, 
             receta, examenes_solicitados, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (paciente_id, cita_id, medico_id, motivo_consulta, diagnostico, 
              receta, examenes_solicitados, observaciones))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id
    
    def get_patient_medical_history(self, paciente_id):
        """Obtiene el historial médico de un paciente"""
        conn = self.get_connection()
        
        query = '''
            SELECT h.*, u.nombre_completo as medico_nombre
            FROM historial_medico h
            JOIN usuarios u ON h.medico_id = u.id
            WHERE h.paciente_id = ?
            ORDER BY h.fecha DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[paciente_id])
        conn.close()
        return df
    
    # MÉTODOS DE PAGOS
    def create_payment(self, cita_id, monto, metodo_pago, observaciones=None):
        """Registra un pago"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pagos (cita_id, monto, metodo_pago, estado, observaciones)
            VALUES (?, ?, ?, 'pagado', ?)
        ''', (cita_id, monto, metodo_pago, observaciones))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def get_payments(self, start_date=None, end_date=None):
        """Obtiene lista de pagos con filtros opcionales"""
        conn = self.get_connection()
        
        query = '''
            SELECT p.*, c.fecha as fecha_cita, pac.nombre_completo as paciente_nombre,
                   u.nombre_completo as medico_nombre
            FROM pagos p
            JOIN citas c ON p.cita_id = c.id
            JOIN pacientes pac ON c.paciente_id = pac.id
            JOIN usuarios u ON c.medico_id = u.id
            WHERE p.estado = 'pagado'
        '''
        params = []
        
        if start_date and end_date:
            query += " AND DATE(p.fecha_pago) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " ORDER BY p.fecha_pago DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    # MÉTODOS DE CONFIGURACIÓN
    def get_clinic_config(self):
        """Obtiene la configuración de la clínica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM configuracion LIMIT 1")
        config = cursor.fetchone()
        conn.close()
        
        if config:
            columns = ['id', 'nombre_clinica', 'direccion', 'telefono', 'email', 
                      'logo_path', 'horario_inicio', 'horario_fin', 'duracion_cita']
            return dict(zip(columns, config))
        return None
    
    def update_clinic_config(self, **kwargs):
        """Actualiza la configuración de la clínica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si existe configuración
        cursor.execute("SELECT COUNT(*) FROM configuracion")
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            fields = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if fields:
                query = f"UPDATE configuracion SET {', '.join(fields)}"
                cursor.execute(query, values)
        else:
            # Crear configuración inicial
            fields = list(kwargs.keys())
            placeholders = ', '.join(['?' for _ in fields])
            values = list(kwargs.values())
            
            query = f"INSERT INTO configuracion ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    # MÉTODOS DE ESPECIALIDADES
    def get_specialties(self):
        """Obtiene lista de especialidades activas"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM especialidades WHERE estado = 'activo'", conn)
        conn.close()
        return df
    
    # MÉTODOS DE REPORTES
    def get_stats_dashboard(self, start_date=None, end_date=None):
        """Obtiene estadísticas para el dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de pacientes activos
        cursor.execute("SELECT COUNT(*) FROM pacientes WHERE estado = 'activo'")
        stats['total_pacientes'] = cursor.fetchone()[0]
        
        # Total de citas del día actual
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM citas WHERE fecha = ?", (today,))
        stats['citas_hoy'] = cursor.fetchone()[0]
        
        # Total de médicos activos
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'doctor' AND estado = 'activo'")
        stats['total_medicos'] = cursor.fetchone()[0]
        
        # Ingresos del mes actual
        cursor.execute('''
            SELECT COALESCE(SUM(monto), 0) FROM pagos 
            WHERE strftime('%Y-%m', fecha_pago) = strftime('%Y-%m', 'now')
            AND estado = 'pagado'
        ''')
        stats['ingresos_mes'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
