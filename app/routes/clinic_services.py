from fastapi import APIRouter
from app.services.clinic_services import(list_services_for_clinic,create_service_for_clinic)
from app.schemas import ClinicServiceCreate


router = APIRouter(
    prefix="/clinics/{clinic_id}/services",
    tags = ["clinic services"]
)


@router.get("")
def list_services(clinic_id:int):
    return list_services_for_clinic(clinic_id)



@router.post("",status_code=201)
def create_services(clinic_id:int,service: ClinicServiceCreate):
    return create_service_for_clinic(clinic_id,service)