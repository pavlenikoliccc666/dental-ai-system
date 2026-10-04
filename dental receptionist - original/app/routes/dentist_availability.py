from fastapi import APIRouter  # pyright: ignore[reportMissingImports]

from app.schemas import DentistAvailabilityCreate
from app.services.dentist_availability import (
    list_availability_for_clinics,
    create_availability_for_clinics,
)


router = APIRouter(
    prefix="/clinics/{clinic_id}/dentists/{dentist_id}/availability",
    tags=["dentist availability"],
)


@router.get("")
def list_availability(
    clinic_id: int,
    dentist_id: int,
):
    return list_availability_for_clinics(
        clinic_id,
        dentist_id,
    )


@router.post("", status_code=201)
def create_availability(
    clinic_id: int,
    dentist_id: int,
    availability: DentistAvailabilityCreate,
):
    return create_availability_for_clinics(
        clinic_id,
        dentist_id,
        availability,
    )