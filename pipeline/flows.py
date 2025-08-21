#!/usr/bin/env python3
"""Pipeline súper simple para refugio de mascotas"""

import pandas as pd
import mysql.connector
import json
from datetime import datetime
import os

def main():
    """Pipeline principal simplificado"""
    print("🐾 Iniciando pipeline simple del refugio...")
    
    # 1. CONEXIÓN A BASE DE DATOS
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'), 
            password=os.getenv('DB_PASSWORD', 'root'),
            database=os.getenv('DB_NAME', 'refugio_mascotas')
        )
        print("✅ Conectado a MySQL")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. EXTRAER DATOS
    try:
        query = "SELECT * FROM mascotas"
        df = pd.read_sql(query, conn)
        print(f"📊 Extraídos {len(df)} registros")
    except Exception as e:
        print(f"❌ Error extrayendo datos: {e}")
        conn.close()
        return
    
    # 3. LIMPIAR DATOS (Validaciones básicas)
    initial_count = len(df)
    
    # Eliminar registros con nombre vacío
    df_clean = df[df['nombre'].notna()].copy()
    df_clean = df_clean[df_clean['nombre'].str.strip() != '']
    
    # Validar edades razonables
    df_clean.loc[df_clean['edad'] < 0, 'edad'] = None
    df_clean.loc[df_clean['edad'] > 25, 'edad'] = None
    
    print(f"🧹 {len(df_clean)} registros válidos de {initial_count}")
    
    # 4. GENERAR BACKUP
    try:
        os.makedirs("backups", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/mascotas_simple_{timestamp}.csv"
        df_clean.to_csv(backup_file, index=False)
        print(f"💾 Backup guardado: {backup_file}")
    except Exception as e:
        print(f"⚠️ Error en backup: {e}")
        backup_file = None
    
    # 5. ACTUALIZAR TABLA DE DATOS LIMPIOS
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mascotas_cleaned")
        
        for _, row in df_clean.iterrows():
            # Calcular score de calidad simple
            score = 1.0
            if pd.isna(row['edad']): score -= 0.2
            if pd.isna(row['descripcion']) or row['descripcion'] == '': score -= 0.1
            
            cursor.execute(
                "INSERT INTO mascotas_cleaned (mascota_id, data_quality_score) VALUES (%s, %s)",
                (int(row['id']), round(score, 2))
            )
        
        conn.commit()
        print(f"💾 Actualizados {len(df_clean)} registros en mascotas_cleaned")
    except Exception as e:
        print(f"⚠️ Error actualizando tabla limpia: {e}")
    
    # 6. GUARDAR LOG SIMPLE
    try:
        os.makedirs("logs", exist_ok=True)
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "registros_originales": initial_count,
            "registros_limpios": len(df_clean),
            "calidad_datos": round((len(df_clean) / initial_count * 100), 1),
            "backup": backup_file
        }
        
        with open("logs/simple_log.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        print(f"📈 Calidad de datos: {metrics['calidad_datos']}%")
        
    except Exception as e:
        print(f"⚠️ Error en log: {e}")
    
    # 7. CERRAR CONEXIÓN
    conn.close()
    print("✅ Pipeline completado exitosamente")
    print(f"📊 Resumen: {len(df_clean)}/{initial_count} registros procesados")

if __name__ == "__main__":
    main()

