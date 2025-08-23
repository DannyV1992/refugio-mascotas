"""
Pipeline completo para Refugio de Mascotas
- Limpieza de datos de mascotas y solicitudes
- Generación de reportes estadísticos
- Backups automáticos
- Análisis de tendencias de adopción
"""

import pandas as pd
import mysql.connector
import json
from datetime import datetime, timedelta
import os
import warnings
from pathlib import Path
import schedule
import time

# Silenciar warning de pandas
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')

class RefugioDataPipeline:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'refugio_mascotas')
        }
        
        # ✅ CORREGIDO: Crear directorios dentro de pipeline/
        self.base_dir = Path(__file__).parent  # Directorio donde está flows.py
        
        # Crear subdirectorios dentro de pipeline/
        (self.base_dir / "backups").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "logs").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "reports").mkdir(parents=True, exist_ok=True)
        
        self.log_info(f"Pipeline iniciado - Directorios en: {self.base_dir}")

    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            return mysql.connector.connect(**self.db_config)
        except Exception as e:
            self.log_error(f"Error de conexión: {e}")
            raise

    def log_info(self, message):
        """Log de información"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] INFO: {message}")

    def log_error(self, message):
        """Log de errores"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ERROR: {message}")

    def extract_data(self):
        """Extracción de datos de todas las tablas principales"""
        conn = self.get_connection()
        
        data = {}
        tables = [
            'mascotas', 'solicitudes_adopcion', 'solicitudes_voluntariado',
            'donaciones', 'apadrinamientos', 'colaboradores_difusion'
        ]
        
        for table in tables:
            try:
                data[table] = pd.read_sql(f"SELECT * FROM {table}", conn)
                self.log_info(f"Extraídos {len(data[table])} registros de {table}")
            except Exception as e:
                self.log_error(f"Error extrayendo {table}: {e}")
                data[table] = pd.DataFrame()
        
        conn.close()
        return data

    def clean_mascotas_data(self, df):
        """Limpieza específica para datos de mascotas"""
        if df.empty:
            return df, {
                "original": 0,
                "cleaned": 0,
                "issues_fixed": 0,
                "quality_score": 100
            }
        
        initial_count = len(df)
        issues_found = 0
        
        # Hacer una copia para evitar warnings
        df = df.copy()
        
        # Limpiar nombres
        df['nombre'] = df['nombre'].astype(str).str.strip()
        df = df[df['nombre'].str.len() > 0]
        
        # Validar edades (convertir a numeric primero)
        df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
        invalid_ages = (df['edad'] < 0) | (df['edad'] > 25)
        issues_found += invalid_ages.sum()
        df.loc[invalid_ages, 'edad'] = None
        
        # Validar URLs de imágenes
        df['imagen_url'] = df['imagen_url'].fillna('')
        
        # Validar teléfonos si existe la columna
        if 'contacto_telefono' in df.columns:
            phone_pattern = r'^\+?\d{4}-?\d{4}$|^\+?506\s?\d{4}\s?\d{4}$'
            invalid_phones = ~df['contacto_telefono'].fillna('').astype(str).str.match(phone_pattern)
            issues_found += invalid_phones.sum()
        
        cleaned_count = len(df)
        
        return df, {
            "original": initial_count,
            "cleaned": cleaned_count,
            "issues_fixed": int(issues_found),
            "quality_score": round((cleaned_count / initial_count * 100), 2) if initial_count > 0 else 100
        }

    def analyze_adoption_trends(self, mascotas_df, solicitudes_df):
        """Análisis de tendencias de adopción"""
        if mascotas_df.empty or solicitudes_df.empty:
            return {
                "popular_pets": {},
                "species_popularity": {},
                "monthly_trends": {},
                "total_requests": 0,
                "approval_rate": 0
            }
        
        try:
            # Mascotas más solicitadas
            popular_pets = solicitudes_df.groupby('mascota_id').size().sort_values(ascending=False).head(5)
            
            # Especies más populares
            species_requests = mascotas_df[mascotas_df['id'].isin(solicitudes_df['mascota_id'])].groupby('especie').size()
            
            # Solicitudes por mes
            solicitudes_df['created_at'] = pd.to_datetime(solicitudes_df['created_at'])
            monthly_requests = solicitudes_df.groupby(solicitudes_df['created_at'].dt.to_period('M')).size()
            
            # Convertir Period a string para JSON
            monthly_trends = {str(period): int(count) for period, count in monthly_requests.items()}
            
            # Tasa de aprobación
            approval_rate = (solicitudes_df['estado'] == 'aprobada').mean() * 100
            
            return {
                "popular_pets": {int(k): int(v) for k, v in popular_pets.items()},
                "species_popularity": {str(k): int(v) for k, v in species_requests.items()},
                "monthly_trends": monthly_trends,
                "total_requests": len(solicitudes_df),
                "approval_rate": round(approval_rate, 2)
            }
        except Exception as e:
            self.log_error(f"Error en análisis de tendencias: {e}")
            return {
                "popular_pets": {},
                "species_popularity": {},
                "monthly_trends": {},
                "total_requests": len(solicitudes_df) if not solicitudes_df.empty else 0,
                "approval_rate": 0
            }

    def generate_daily_report(self, data, analytics):
        """Generar reporte diario"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.base_dir / "reports" / f"daily_report_{timestamp}.json"  # ✅ CORREGIDO
        
        try:
            # Calcular estadísticas con manejo de errores
            mascotas_disponibles = 0
            if not data['mascotas'].empty and 'estado' in data['mascotas'].columns:
                mascotas_disponibles = int((data['mascotas']['estado'] == 'disponible').sum())
            
            solicitudes_pendientes = 0
            if not data['solicitudes_adopcion'].empty and 'estado' in data['solicitudes_adopcion'].columns:
                solicitudes_pendientes = int((data['solicitudes_adopcion']['estado'] == 'pendiente').sum())
            
            voluntarios_activos = 0
            if not data['solicitudes_voluntariado'].empty and 'estado' in data['solicitudes_voluntariado'].columns:
                voluntarios_activos = int((data['solicitudes_voluntariado']['estado'] == 'aprobado').sum())
            
            donaciones_mes = 0
            if not data['donaciones'].empty and 'created_at' in data['donaciones'].columns and 'monto' in data['donaciones'].columns:
                current_month_donations = data['donaciones'][
                    pd.to_datetime(data['donaciones']['created_at']).dt.month == datetime.now().month
                ]
                donaciones_mes = float(current_month_donations['monto'].fillna(0).sum())
            
            report = {
                "fecha": datetime.now().isoformat(),
                "resumen_datos": {
                    "mascotas_total": len(data['mascotas']),
                    "mascotas_disponibles": mascotas_disponibles,
                    "solicitudes_pendientes": solicitudes_pendientes,
                    "voluntarios_activos": voluntarios_activos,
                    "donaciones_mes": donaciones_mes
                },
                "analytics": analytics,
                "alertas": self.check_alerts(data)
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.log_info(f"Reporte diario generado: {report_path}")
            return report
            
        except Exception as e:
            self.log_error(f"Error generando reporte: {e}")
            return {"fecha": datetime.now().isoformat(), "error": str(e)}

    def check_alerts(self, data):
        """Verificar alertas importantes"""
        alerts = []
        
        try:
            # Solicitudes pendientes por más de 7 días
            if not data['solicitudes_adopcion'].empty and 'created_at' in data['solicitudes_adopcion'].columns:
                old_requests = data['solicitudes_adopcion'][
                    (pd.to_datetime(data['solicitudes_adopcion']['created_at']) < datetime.now() - timedelta(days=7)) &
                    (data['solicitudes_adopcion']['estado'] == 'pendiente')
                ]
                if len(old_requests) > 0:
                    alerts.append(f"ALERTA: {len(old_requests)} solicitudes pendientes por más de 7 días")
            
            # Mascotas sin imagen
            if not data['mascotas'].empty and 'imagen_url' in data['mascotas'].columns:
                no_image = data['mascotas'][
                    (data['mascotas']['imagen_url'].isna()) | 
                    (data['mascotas']['imagen_url'] == '') |
                    (data['mascotas']['imagen_url'] == '/uploads/')
                ]
                if len(no_image) > 0:
                    alerts.append(f"INFO: {len(no_image)} mascotas sin foto")
            
            # Donaciones no confirmadas
            if not data['donaciones'].empty and 'estado' in data['donaciones'].columns:
                unconfirmed = data['donaciones'][data['donaciones']['estado'] == 'pendiente']
                if len(unconfirmed) > 5:
                    alerts.append(f"ALERTA: {len(unconfirmed)} donaciones por confirmar")
        
        except Exception as e:
            self.log_error(f"Error verificando alertas: {e}")
            alerts.append(f"Error verificando alertas: {str(e)}")
        
        return alerts

    def create_backups(self, data):
        """Crear backups de todas las tablas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / f"backup_{timestamp}"  # ✅ CORREGIDO
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for table_name, df in data.items():
            if not df.empty:
                backup_file = backup_dir / f"{table_name}_{timestamp}.csv"
                df.to_csv(backup_file, index=False, encoding='utf-8')
                self.log_info(f"Backup creado: {backup_file}")

    def update_quality_scores(self, cleaned_mascotas):
        """Actualizar tabla de calidad"""
        if cleaned_mascotas.empty:
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Limpiar tabla anterior
            cursor.execute("DELETE FROM mascotas_cleaned")
            
            # Insertar datos limpios con scores
            for _, row in cleaned_mascotas.iterrows():
                score = 1.0
                if pd.isna(row.get('edad')): score -= 0.2
                if pd.isna(row.get('descripcion')) or str(row.get('descripcion', '')) == '': score -= 0.1
                if pd.isna(row.get('imagen_url')) or str(row.get('imagen_url', '')) == '': score -= 0.2
                if pd.isna(row.get('contacto_telefono')) or str(row.get('contacto_telefono', '')) == '': score -= 0.1
                
                cursor.execute(
                    "INSERT INTO mascotas_cleaned (mascota_id, data_quality_score) VALUES (%s, %s)",
                    (int(row['id']), round(max(score, 0.1), 2))
                )
            
            conn.commit()
            self.log_info(f"Actualizados {len(cleaned_mascotas)} registros en mascotas_cleaned")
            
        except Exception as e:
            self.log_error(f"Error actualizando calidad: {e}")
        finally:
            cursor.close()
            conn.close()

    def run_full_pipeline(self):
        """Ejecutar pipeline completo"""
        self.log_info("🐾 Iniciando pipeline completo del refugio...")
        
        try:
            # 1. Extraer datos
            data = self.extract_data()
            
            # 2. Limpiar datos principales
            cleaned_mascotas, quality_stats = self.clean_mascotas_data(data['mascotas'])
            
            # 3. Análisis de tendencias
            analytics = self.analyze_adoption_trends(cleaned_mascotas, data['solicitudes_adopcion'])
            
            # 4. Generar reporte
            report = self.generate_daily_report(data, analytics)
            
            # 5. Crear backups
            self.create_backups(data)
            
            # 6. Actualizar tabla de calidad
            self.update_quality_scores(cleaned_mascotas)
            
            # 7. Log final
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "status": "SUCCESS",
                "quality_stats": quality_stats,
                "total_records_processed": sum(len(df) for df in data.values()),
                "alerts_generated": len(report.get('alertas', []))
            }
            
            log_file = self.base_dir / "logs" / f"pipeline_log_{datetime.now().strftime('%Y%m%d')}.json"  # ✅ CORREGIDO
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
            
            self.log_info(f"✅ Pipeline completado exitosamente")
            self.log_info(f"📊 Calidad de datos: {quality_stats.get('quality_score', 100)}%")
            self.log_info(f"🔍 Alertas generadas: {len(report.get('alertas', []))}")
            
            if report.get('alertas'):
                self.log_info("⚠️ Alertas:")
                for alerta in report['alertas']:
                    self.log_info(f"   - {alerta}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Pipeline falló: {e}")
            return False

# Función para ejecutar manualmente
def run_pipeline():
    pipeline = RefugioDataPipeline()
    return pipeline.run_full_pipeline()

# Programación automática (opcional)
def schedule_pipeline():
    """Programar ejecución automática"""
    schedule.every().day.at("02:00").do(run_pipeline)  # 2 AM diario
    schedule.every().sunday.at("01:00").do(run_pipeline)  # Domingo 1 AM
    
    print("🕐 Pipeline programado - presiona Ctrl+C para detener")
    print("📅 Ejecuciones:")
    print("   - Diario: 2:00 AM")
    print("   - Semanal: Domingos 1:00 AM")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline detenido")

if __name__ == "__main__":
    import sys
    
    print("🐾 REFUGIO DE MASCOTAS - PIPELINE DE DATOS")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_pipeline()
    else:
        success = run_pipeline()
        if success:
            print("\n🎉 Pipeline ejecutado exitosamente!")
        else:
            print("\n❌ Pipeline falló. Revisa los logs.")
