from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import httpx
import shutil
import uuid
import json
from pathlib import Path

from database import db
from models import (
    MascotaCreate, MascotaUpdate, MascotaResponse,
    SolicitudAdopcionCreate, SolicitudAdopcionResponse,
    SolicitudVoluntariadoCreate, SolicitudVoluntariadoResponse,
    DonacionCreate, DonacionResponse,
    ApadrinamientoCreate, ApadrinamientoResponse,
    ColaboradorDifusionCreate, ColaboradorDifusionResponse,
    ExternalDataResponse, PipelineStatusResponse
)

app = FastAPI(title="Refugio de Mascotas API")

# CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio para imágenes
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Montar directorio de archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuración de BD
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'refugio_mascotas'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {e}")

# ===============================
# ENDPOINTS PARA MASCOTAS
# ===============================

@app.get("/mascotas", response_model=List[MascotaResponse])
async def listar_mascotas():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM mascotas ORDER BY created_at DESC")
        mascotas = cursor.fetchall()
        return mascotas
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.post("/mascotas", response_model=dict)
async def crear_mascota(mascota: MascotaCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO mascotas
        (nombre, especie, edad, descripcion, imagen_url, tamaño, genero, contacto_nombre, contacto_telefono, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            mascota.nombre, mascota.especie, mascota.edad,
            mascota.descripcion, mascota.imagen_url, mascota.tamaño,
            mascota.genero, mascota.contacto_nombre, mascota.contacto_telefono,
            mascota.estado
        ))
        connection.commit()
        return {"message": "Mascota creada exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.put("/mascotas/{mascota_id}")
async def actualizar_mascota(mascota_id: int, mascota: MascotaUpdate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        UPDATE mascotas SET 
        nombre=%s, especie=%s, edad=%s, descripcion=%s, imagen_url=%s, 
        tamaño=%s, genero=%s, contacto_nombre=%s, contacto_telefono=%s, estado=%s
        WHERE id=%s
        """
        cursor.execute(query, (
            mascota.nombre, mascota.especie, mascota.edad,
            mascota.descripcion, mascota.imagen_url, mascota.tamaño,
            mascota.genero, mascota.contacto_nombre, mascota.contacto_telefono,
            mascota.estado, mascota_id
        ))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
        return {"message": "Mascota actualizada exitosamente"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.delete("/mascotas/{mascota_id}")
async def eliminar_mascota(mascota_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM mascotas WHERE id=%s", (mascota_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
        return {"message": "Mascota eliminada exitosamente"}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINT PARA SUBIR IMÁGENES
# ===============================
'''
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Validar tamaño (5MB máximo)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="La imagen no debe superar los 5MB")
    
    # Generar nombre único para el archivo
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Retornar URL de acceso
    return {"url": f"/uploads/{filename}"}
'''

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    print("Recibiendo petición para subir imagen:", file.filename)
    content = await file.read()
    print("Tamaño recibido:", len(content))
    
    # Validar tamaño (5MB máximo)
    file_size = len(content)
    if file_size > 5 * 1024 * 1024: # 5MB
        raise HTTPException(status_code=400, detail="La imagen no debe superar los 5MB")
    # Generar nombre único para el archivo
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    print("Guardado archivo en:", file_path)
    
    # Retornar URL de acceso
    return {"url": f"/uploads/{filename}"}


# ===============================
# ENDPOINTS PARA ADOPCIONES
# ===============================

@app.post("/solicitudes-adopcion", response_model=dict)
async def crear_solicitud_adopcion(solicitud: SolicitudAdopcionCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO solicitudes_adopcion 
        (mascota_id, nombre, telefono, email, direccion, tipo_vivienda, 
         otras_mascotas, experiencia, motivacion, horas_disponibles, presupuesto)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            solicitud.mascota_id, solicitud.nombre, solicitud.telefono,
            solicitud.email, solicitud.direccion, solicitud.tipo_vivienda,
            solicitud.otras_mascotas, solicitud.experiencia, solicitud.motivacion,
            solicitud.horas_disponibles, solicitud.presupuesto
        ))
        connection.commit()
        return {"message": "Solicitud de adopción enviada exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/solicitudes-adopcion", response_model=List[SolicitudAdopcionResponse])
async def listar_solicitudes_adopcion():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM solicitudes_adopcion ORDER BY created_at DESC")
        solicitudes = cursor.fetchall()
        return solicitudes
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINTS PARA VOLUNTARIADO
# ===============================

@app.post("/solicitudes-voluntariado", response_model=dict)
async def crear_solicitud_voluntariado(solicitud: SolicitudVoluntariadoCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        areas_json = json.dumps(solicitud.areas)
        query = """
        INSERT INTO solicitudes_voluntariado 
        (nombre, telefono, email, areas, disponibilidad, experiencia)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            solicitud.nombre, solicitud.telefono, solicitud.email,
            areas_json, solicitud.disponibilidad, solicitud.experiencia
        ))
        connection.commit()
        return {"message": "Solicitud de voluntariado enviada exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/solicitudes-voluntariado", response_model=List[dict])
async def listar_solicitudes_voluntariado():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM solicitudes_voluntariado ORDER BY created_at DESC")
        solicitudes = cursor.fetchall()
        # Convertir areas de JSON string a lista
        for solicitud in solicitudes:
            if solicitud['areas']:
                solicitud['areas'] = json.loads(solicitud['areas'])
        return solicitudes
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINTS PARA DONACIONES
# ===============================

@app.post("/donaciones", response_model=dict)
async def crear_donacion(donacion: DonacionCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO donaciones 
        (tipo_donacion, monto, descripcion_especie, nombre_donante, telefono_donante, email_donante)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            donacion.tipo_donacion, donacion.monto, donacion.descripcion_especie,
            donacion.nombre_donante, donacion.telefono_donante, donacion.email_donante
        ))
        connection.commit()
        return {"message": "Donación registrada exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/donaciones", response_model=List[DonacionResponse])
async def listar_donaciones():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM donaciones ORDER BY created_at DESC")
        donaciones = cursor.fetchall()
        return donaciones
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINTS PARA APADRINAMIENTO
# ===============================

@app.post("/apadrinamientos", response_model=dict)
async def crear_apadrinamiento(apadrinamiento: ApadrinamientoCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """
        INSERT INTO apadrinamientos 
        (nombre_padrino, telefono_padrino, email_padrino, preferencia_especie, aportacion_mensual)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            apadrinamiento.nombre_padrino, apadrinamiento.telefono_padrino,
            apadrinamiento.email_padrino, apadrinamiento.preferencia_especie,
            apadrinamiento.aportacion_mensual
        ))
        connection.commit()
        return {"message": "Solicitud de apadrinamiento enviada exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/apadrinamientos", response_model=List[ApadrinamientoResponse])
async def listar_apadrinamientos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM apadrinamientos ORDER BY created_at DESC")
        apadrinamientos = cursor.fetchall()
        return apadrinamientos
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINTS PARA DIFUSIÓN
# ===============================

@app.post("/colaboradores-difusion", response_model=dict)
async def crear_colaborador_difusion(colaborador: ColaboradorDifusionCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        tipos_json = json.dumps(colaborador.tipos_difusion)
        query = """
        INSERT INTO colaboradores_difusion 
        (nombre, email, tipos_difusion, redes_sociales)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            colaborador.nombre, colaborador.email,
            tipos_json, colaborador.redes_sociales
        ))
        connection.commit()
        return {"message": "Colaborador de difusión registrado exitosamente", "id": cursor.lastrowid}
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/colaboradores-difusion", response_model=List[dict])
async def listar_colaboradores_difusion():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM colaboradores_difusion ORDER BY created_at DESC")
        colaboradores = cursor.fetchall()
        # Convertir tipos_difusion de JSON string a lista
        for colaborador in colaboradores:
            if colaborador['tipos_difusion']:
                colaborador['tipos_difusion'] = json.loads(colaborador['tipos_difusion'])
        return colaboradores
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# ENDPOINTS DE ESTADÍSTICAS
# ===============================

@app.get("/estadisticas-colaboracion")
async def obtener_estadisticas_colaboracion():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        stats = {}
        
        # Voluntarios activos
        cursor.execute("SELECT COUNT(*) as count FROM solicitudes_voluntariado WHERE estado = 'aprobado'")
        stats['voluntarios_activos'] = cursor.fetchone()['count']
        
        # Total donaciones del mes
        cursor.execute("""
            SELECT SUM(monto) as total FROM donaciones 
            WHERE tipo_donacion = 'monetaria' 
            AND MONTH(created_at) = MONTH(CURRENT_DATE())
            AND YEAR(created_at) = YEAR(CURRENT_DATE())
        """)
        result = cursor.fetchone()
        stats['donaciones_mes'] = float(result['total']) if result['total'] else 0
        
        # Apadrinamientos activos
        cursor.execute("SELECT COUNT(*) as count FROM apadrinamientos WHERE estado = 'activo'")
        stats['apadrinamientos_activos'] = cursor.fetchone()['count']
        
        # Colaboradores de difusión activos
        cursor.execute("SELECT COUNT(*) as count FROM colaboradores_difusion WHERE estado = 'activo'")
        stats['colaboradores_difusion'] = cursor.fetchone()['count']
        
        return stats
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

# ===============================
# APIs EXTERNAS
# ===============================

@app.get("/api/external-pet-data")
async def obtener_datos_externos():
    async with httpx.AsyncClient() as client:
        try:
            # Dog breeds
            dog_response = await client.get("https://dog.ceo/api/breeds/list/all")
            dog_breeds = dog_response.json()

            # Cat fact
            cat_response = await client.get("https://catfact.ninja/fact")
            cat_fact = cat_response.json()

            return {
                "dog_breeds": list(dog_breeds["message"].keys())[:10],
                "cat_fact": cat_fact["fact"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo datos externos: {e}")

@app.get("/api/pipeline/status")
async def estado_pipeline():
    return {
        "status": "running",
        "last_run": datetime.now().isoformat(),
        "next_run": "2024-01-01T00:00:00",
        "processed_records": 0
    }

# ===============================
# ENDPOINT DE SALUD
# ===============================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
