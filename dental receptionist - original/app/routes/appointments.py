from fastapi import APIRouter
from app.schemas import AppointmentCreate
from app.schemas import AppointmentReschedule


from app.services.appointments import (
    get_appointments_for_clinic,
    create_appointment as create_appointment_service,
    cancel_appointment as cancel_appointment_service,
    reschedule_appointment as reschedule_appointment_service,
    get_patient_appointments
    

)

router = APIRouter(
    prefix="/clinics/{clinic_id}/appointments",
    tags = ["appointment"]
)




cancel_router = APIRouter(
    prefix="/appointments",
    tags=["appointment"],
)


find_appointments_patient_router = APIRouter(
    prefix="/clinics/{clinic_id}/patients/{patient_id}/appointments",
    tags=["appointment"],
)
@router.get("")
def get_appointment_for_clinic(clinic_id: int):
    return get_appointments_for_clinic(clinic_id)






@router.post("", status_code=201)
def create_appointment_endpoint(clinic_id: int,appointment: AppointmentCreate):
    return create_appointment_service(clinic_id,appointment)





@cancel_router.post("/{appointment_id}/cancel")
def cancel_appointment_endpoint(appointment_id: int):
    return cancel_appointment_service(appointment_id)







@cancel_router.patch("/{appointment_id}/reschedule")
def reschedule_appointment_endpoint(appointment_id: int,appointment: AppointmentReschedule):
    return reschedule_appointment_service(appointment_id,appointment)


@find_appointments_patient_router.get("")
def get_appointment_patient_endpoint(clinic_id : int,patient_id : int):
    return get_patient_appointments(clinic_id,patient_id)