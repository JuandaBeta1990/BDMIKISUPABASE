# archivo: schemas.py (Versión Completa y Final - Corregida)

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

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Zone(ZoneBase, BaseSchema):
    id: int
    project_count: Optional[int] = 0


# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    zone_id: Optional[int] = None
    general_field_id: Optional[str] = None
    prices_field_id: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    zone_id: Optional[int] = None
    general_field_id: Optional[str] = None
    prices_field_id: Optional[str] = None

class Project(ProjectBase, BaseSchema):
    id: int

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

class UnitUpdate(BaseModel):
    unit_identifier: Optional[str] = None
    typology: Optional[str] = None
    level: Optional[str] = None
    total_area_sqm: Optional[float] = None
    status: Optional[str] = None
    delivery_date: Optional[str] = None
    price_list_url: Optional[str] = None

class Unit(UnitBase, BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime


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
    role: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

class User(UserBase, BaseSchema):
    id: int  # Tu BD usa INTEGER, NO UUID


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