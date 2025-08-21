import mysql.connector
from mysql.connector import Error
import os
from typing import Optional

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'refugio_mascotas'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root')
        }
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error de conexión a la base de datos: {e}")
            raise e
    
    def create_database_if_not_exists(self):
        """Crear la base de datos si no existe"""
        try:
            # Conexión sin especificar base de datos
            temp_config = self.config.copy()
            temp_config.pop('database')
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            # Crear base de datos
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            print(f"✅ Base de datos '{self.config['database']}' creada/verificada")
            
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"❌ Error creando base de datos: {e}")
            return False
    
    def initialize_tables(self):
        """Ejecutar el script init.sql automáticamente"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Leer y ejecutar init.sql
            with open('sql/init.sql', 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # Dividir en statements individuales y ejecutar
            statements = sql_script.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            connection.commit()
            print("✅ Tablas inicializadas correctamente")
            
            cursor.close()
            connection.close()
            return True
        except Error as e:
            print(f"❌ Error inicializando tablas: {e}")
            return False
    
    def setup_database(self):
        """Setup completo de la base de datos"""
        print("🗄️ Configurando base de datos...")
        
        if self.create_database_if_not_exists():
            if self.initialize_tables():
                print("✅ Base de datos configurada exitosamente")
                return True
        
        print("❌ Error en la configuración de la base de datos")
        return False
    
    def test_connection(self):
        try:
            connection = self.get_connection()
            if connection.is_connected():
                print("✅ Conexión a MySQL exitosa")
                connection.close()
                return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return False

# Instancia global
db = Database()

