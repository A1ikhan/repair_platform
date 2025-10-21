from ninja import Schema
from typing import Optional, List
from datetime import date, datetime
from .users_schema import UserSchema

class ProblemPhotoSchema(Schema):
    id: int
    image_url: str
    description: str
    uploaded_at: datetime

    @staticmethod
    def resolve_image_url(obj):
        return obj.image.url

class ProblemPhotoUploadSchema(Schema):
    description: Optional[str] = None

class PricePredictionSchema(Schema):
    predicted_price: Optional[float] = None
    confidence: float = 0.0
    price_range: Optional[dict] = None
    message: str = ""


class RepairRequestSchemaIn(Schema):
    title: str
    description: str
    device_type: str
    address: str
    desired_completion_date: Optional[date] = None

class FileSchemaOut(Schema):
    id: int
    file_url: str
    description: str
    uploaded_by: UserSchema
    uploaded_at: datetime

    @staticmethod
    def resolve_file_url(obj):
        return obj.file.url

    @staticmethod
    def resolve_uploaded_by(obj):
        return UserSchema.from_orm(obj.uploaded_by)

class RepairRequestSchemaOut(Schema):
    id: int
    title: str
    description: str
    device_type: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    desired_completion_date: Optional[date] = None
    status: str
    created_by: UserSchema
    created_at: datetime
    updated_at: datetime
    files: List[FileSchemaOut] = []

    predicted_price: Optional[float] = None
    price_confidence: float = 0.0
    final_price: Optional[float] = None
    problem_photos: List[ProblemPhotoSchema] = []

    @staticmethod
    def resolve_created_by(obj):
        return UserSchema.from_orm(obj.created_by)

    @staticmethod
    def resolve_problem_photos(obj):
        return [ProblemPhotoSchema.from_orm(photo) for photo in obj.problem_photos.all()]

    @staticmethod
    def resolve_files(obj):
        return obj.files.all()

class FinalPriceUpdateSchema(Schema):
    final_price: float

class AIAnalysisDataSchema(Schema):
    problems_detected: List[str] = []
    severity_score: float = 0.0
    estimated_repair_time_hours: float = 0.0
    keywords: List[str] = []