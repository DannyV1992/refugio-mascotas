from pydantic import BaseModel, Field

from typing import Optional, List

from datetime import datetime

from enum import Enum

import json

class EspecieEnum(str, Enum):
    perro = "perro"
    gato = "gato"
    otro = "otro"

class EstadoEnum(str, Enum):
    disponible = "disponible"
    adoptado = "adoptado"

class TamañoEnum(str, Enum):
    pequeño = "pequeño"
    mediano = "mediano"
    grande = "grande"

class GeneroEnum(str, Enum):
    macho = "macho"
    hembra = "hembra"

class MascotaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la mascota")
    especie: EspecieEnum = Field(..., description="Especie de la mascota")
    edad: Optional[int] = Field(None, ge=0, le=30, description="Edad en años")
    descripcion: Optional[str] = Field("", max_length=500, description="Descripción de la mascota")
    imagen_url: Optional[str] = Field(None, max_length=500, description="URL de la imagen")
    tamaño: Optional[TamañoEnum] = Field(None, description="Tamaño de la mascota")
    genero: Optional[GeneroEnum] = Field(None, description="Género de la mascota")
    contacto_nombre: Optional[str] = Field(None, max_length=100, description="Nombre de contacto")
    contacto_telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    estado: EstadoEnum = Field(EstadoEnum.disponible, description="Estado de adopción")

class MascotaCreate(MascotaBase):
    pass

class MascotaUpdate(MascotaBase):
    pass

class MascotaResponse(MascotaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MascotaCleanedResponse(BaseModel):
    id: int
    mascota_id: int
    data_quality_score: float
    processed_at: datetime

    class Config:
        from_attributes = True

# Modelos para solicitudes de adopción

class TipoViviendaEnum(str, Enum):
    casa = "casa"
    apartamento = "apartamento"
    casa_jardin = "casa_jardin"

class OtrasMascotasEnum(str, Enum):
    no = "no"
    perros = "perros"
    gatos = "gatos"
    ambos = "ambos"
    otros = "otros"

class ExperienciaEnum(str, Enum):
    primera_vez = "primera_vez"
    poca = "poca"
    moderada = "moderada"
    mucha = "mucha"

class HorasEnum(str, Enum):
    una_tres = "1-3"
    cuatro_seis = "4-6"
    seis_ocho = "6-8"
    ocho_mas = "8+"
    todo_dia = "todo_dia"

class PresupuestoEnum(str, Enum):
    quinientos_mil = "500-1000"
    mil_dos_mil = "1000-2000"
    dos_mil_tres_mil = "2000-3000"
    tres_mil_mas = "3000+"

class EstadoSolicitudEnum(str, Enum):
    pendiente = "pendiente"
    revisando = "revisando"
    aprobada = "aprobada"
    rechazada = "rechazada"

class SolicitudAdopcionBase(BaseModel):
    mascota_id: int
    nombre: str = Field(..., min_length=1, max_length=100)
    telefono: str = Field(..., max_length=20)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    direccion: str = Field(..., min_length=10)
    tipo_vivienda: TipoViviendaEnum
    otras_mascotas: OtrasMascotasEnum
    experiencia: ExperienciaEnum
    motivacion: str = Field(..., min_length=20, max_length=1000)
    horas_disponibles: HorasEnum
    presupuesto: PresupuestoEnum

class SolicitudAdopcionCreate(SolicitudAdopcionBase):
    pass

class SolicitudAdopcionResponse(SolicitudAdopcionBase):
    id: int
    estado: EstadoSolicitudEnum
    notas_admin: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modelos para voluntariado

class DisponibilidadEnum(str, Enum):
    mañanas = "mañanas"
    tardes = "tardes"
    fines_semana = "fines_semana"
    flexible = "flexible"

class EstadoVoluntarioEnum(str, Enum):
    pendiente = "pendiente"
    revisando = "revisando"
    aprobado = "aprobado"
    rechazado = "rechazado"

class SolicitudVoluntariadoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    telefono: str = Field(..., max_length=20)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    areas: List[str] = Field(..., min_items=1) # Lista de áreas seleccionadas
    disponibilidad: DisponibilidadEnum
    experiencia: Optional[str] = Field(None, max_length=1000)

class SolicitudVoluntariadoCreate(SolicitudVoluntariadoBase):
    pass

class SolicitudVoluntariadoResponse(SolicitudVoluntariadoBase):
    id: int
    estado: EstadoVoluntarioEnum
    notas_admin: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modelos para donaciones

class TipoDonacionEnum(str, Enum):
    monetaria = "monetaria"
    especie = "especie"

class EstadoDonacionEnum(str, Enum):
    pendiente = "pendiente"
    confirmada = "confirmada"
    recibida = "recibida"

class DonacionBase(BaseModel):
    tipo_donacion: TipoDonacionEnum
    monto: Optional[float] = Field(None, gt=0)
    descripcion_especie: Optional[str] = Field(None, max_length=1000)
    nombre_donante: str = Field(..., min_length=1, max_length=100)
    telefono_donante: str = Field(..., max_length=20)
    email_donante: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')

class DonacionCreate(DonacionBase):
    pass

class DonacionResponse(DonacionBase):
    id: int
    estado: EstadoDonacionEnum
    fecha_recepcion: Optional[datetime]
    notas_admin: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modelos para apadrinamiento

class EstadoApadrinamientoEnum(str, Enum):
    pendiente = "pendiente"
    activo = "activo"
    pausado = "pausado"
    cancelado = "cancelado"

class ApadrinamientoBase(BaseModel):
    nombre_padrino: str = Field(..., min_length=1, max_length=100)
    telefono_padrino: str = Field(..., max_length=20)
    email_padrino: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    preferencia_especie: Optional[str] = Field(None)
    aportacion_mensual: float = Field(..., gt=0)

class ApadrinamientoCreate(ApadrinamientoBase):
    pass

class ApadrinamientoResponse(ApadrinamientoBase):
    id: int
    mascota_asignada_id: Optional[int]
    estado: EstadoApadrinamientoEnum
    fecha_inicio: Optional[datetime]
    notas_admin: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modelos para difusión

class EstadoDifusionEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

class ColaboradorDifusionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    tipos_difusion: List[str] = Field(..., min_items=1)
    redes_sociales: Optional[str] = Field(None, max_length=500)

class ColaboradorDifusionCreate(ColaboradorDifusionBase):
    pass

class ColaboradorDifusionResponse(ColaboradorDifusionBase):
    id: int
    estado: EstadoDifusionEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Modelos para datos externos

class ExternalDataResponse(BaseModel):
    dog_breeds: list[str]
    cat_fact: str

# Modelos para pipeline

class PipelineStatusResponse(BaseModel):
    status: str
    last_run: Optional[str]
    next_run: Optional[str]
    processed_records: int
