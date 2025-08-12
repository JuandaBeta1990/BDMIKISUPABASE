# archivo: schemas.py (Versión Completa y Final - 04 de Agosto, 2025)

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- Schemas Base ---
# Un schema base que otros pueden heredar para no repetir la Config
class BaseSchema(BaseModel):
    # Configuración para Pydantic V2: permite mapear desde objetos de base de datos
    model_config = ConfigDict(from_attributes=True)

# --- Zone Schemas ---
class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None

class ZoneCreate(ZoneBase):
    pass

class Zone(ZoneBase, BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    slug: Optional[str] = None
    zone: Optional[UUID] = None
    sub_zone: Optional[str] = None
    developer: Optional[str] = None
    maps_url: Optional[str] = None
    concept: Optional[str] = None
    total_units: Optional[int] = 0
    delivery_summary: Optional[str] = None
    brochure_slug: Optional[str] = None
    render_slug: Optional[str] = None
    tour_url: Optional[str] = None
    admin_type: Optional[str] = None
    accepts_crypto: Optional[bool] = False
    turn_key: Optional[bool] = False
    has_ocean_view: Optional[bool] = False
    condo_regime: Optional[bool] = False # Corregido a booleano

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel): # Modelo específico para actualización con todos los campos opcionales
    name: Optional[str] = None
    slug: Optional[str] = None
    zone: Optional[UUID] = None
    sub_zone: Optional[str] = None
    developer: Optional[str] = None
    maps_url: Optional[str] = None
    concept: Optional[str] = None
    total_units: Optional[int] = None
    delivery_summary: Optional[str] = None
    brochure_slug: Optional[str] = None
    render_slug: Optional[str] = None
    tour_url: Optional[str] = None
    admin_type: Optional[str] = None
    accepts_crypto: Optional[bool] = None
    turn_key: Optional[bool] = None
    has_ocean_view: Optional[bool] = None
    condo_regime: Optional[bool] = None

class Project(ProjectBase, BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

class ProjectWithZone(Project):
    zone_name: Optional[str] = None

# --- Unit Schemas ---
class UnitBase(BaseModel):
    project_id: UUID
    unit_identifier: str
    typology: Optional[str] = None
    level: Optional[str] = None
    total_area_sqm: Optional[float] = None
    status: Optional[str] = 'Disponible'
    delivery_date: Optional[str] = None
    price_list_url: Optional[str] = None

class UnitCreate(UnitBase):
    pass

class Unit(UnitBase, BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime

# NUEVA CLASE para la actualización
class UnitUpdate(BaseModel):
    unit_identifier: Optional[str] = None
    typology: Optional[str] = None
    level: Optional[str] = None
    total_area_sqm: Optional[float] = None
    status: Optional[str] = None
    delivery_date: Optional[str] = None
    price_list_url: Optional[str] = None

# --- Payment Option Schemas ---
class PaymentOptionBase(BaseModel):
    unit_id: UUID
    scheme_name: str
    price: Optional[float] = None
    currency: Optional[str] = None

class PaymentOptionCreate(PaymentOptionBase):
    pass

class PaymentOption(PaymentOptionBase, BaseSchema):
    id: UUID
    created_at: datetime

# --- Project Amenity Schemas ---
class AmenityBase(BaseModel):
    project_id: UUID
    amenity_description: str

class AmenityCreate(AmenityBase):
    pass

class Amenity(AmenityBase, BaseSchema):
    id: UUID
    created_at: datetime

# --- Project Detail Schemas ---
class DetailBase(BaseModel):
    project_id: UUID
    category: str
    detail_key: str
    detail_value: Optional[str] = None

class DetailCreate(DetailBase):
    pass

class Detail(DetailBase, BaseSchema):
    id: UUID
    created_at: datetime

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase,
           BaseSchema):
    id: UUID

# --- Strategic Context Schemas ---
class StrategicContextBase(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    gmaps_url: Optional[str] = None
    zone_id: Optional[UUID] = None

class StrategicContextCreate(StrategicContextBase):
    pass

class StrategicContext(StrategicContextBase, BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime