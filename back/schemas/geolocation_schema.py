from typing import Optional

from ninja import Schema


class LocationSchema(Schema):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str = ""
    city: str = ""

class LocationUpdateSchema(Schema):
    address: str

class NearbyWorkersResponse(Schema):
    worker_id: int
    username: str
    specialization: str
    rating: float
    experience: int
    is_verified: bool
    distance_km: float
    address: str
    score: float

class PartsShopSchema(Schema):
    name: str
    address: str
    latitude: float
    longitude: float
    contacts: list
    distance: Optional[float] = None

class GeocodeResponse(Schema):
    success: bool
    coordinates: Optional[dict] = None
    address: str

class LocationResponse(Schema):
    exists: bool
    location: Optional[LocationSchema] = None