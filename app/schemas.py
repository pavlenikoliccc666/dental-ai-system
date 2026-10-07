from pydantic import BaseModel,Field,model_validator
from datetime import datetime
from decimal import Decimal
from datetime import time


class ClinicCreate(BaseModel):
    name : str

    city : str

    timezone : str

class PatientCreate(BaseModel):
    full_name : str

    phone : str

    email : str 



class AppointmentCreate(BaseModel):
    patient_id: int

    dentist_id: int

    starts_at: datetime

    ends_at: datetime


class AppointmentReschedule(BaseModel):
    starts_at: datetime

    ends_at: datetime



class DentistCreate(BaseModel):
    full_name: str

    specialization: str


class ClinicServiceCreate(BaseModel):
    name: str

    duration_minutes: int

    price : Decimal | None = None


class DentistAvailabilityCreate(BaseModel):
    day_of_the_week: int = Field(
        ge=0,
        le=6,
        description="0 = ponedjeljak, 6 = nedjelja",
    )

    starts_at: time
    ends_at: time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.ends_at <= self.starts_at:
            raise ValueError(
                "ends_at must be after starts_at"
            )

        return self