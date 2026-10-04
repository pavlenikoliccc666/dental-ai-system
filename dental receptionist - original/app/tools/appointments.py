from app.services.clinic_services import (
    list_services_for_clinic,
)
from app.services.dentist_availability import (
    list_availability_for_clinics,
)

from app.services.appointments import(
   create_appointment as create_appointment_service,
   cancel_appointment as cancel_appointment_service,
   reschedule_appointment as reschedule_appointment_service,
   get_patient_appointments as get_patient_appointments_service
)

from app.schemas import AppointmentCreate,AppointmentReschedule

from app.services.appointments import(find_available_slots)
from datetime import date

from langchain_core.tools import tool

@tool
def get_clinic_services_tool(
    clinic_id: int,
) -> list[dict]:
    """This tool return services for clinic.It containts price,name,duration,status...
    """
    return list_services_for_clinic(clinic_id)


@tool
def get_dentist_availability_tool(
    clinic_id: int,
    dentist_id: int,
) -> list[dict]:
    """This tool return work time of dentist for each day.It can have 1 or more work times during the day."""
    return list_availability_for_clinics(
        clinic_id,
        dentist_id,
    )

@tool
def find_available_slots_tool(
        clinic_id: int,
        dentist_id: int,
        service_id: int,
        requested_date: date
) -> list[dict]:
 """This tool return the available slots for specific day,time,service,dentist and clinic."""
    
 return find_available_slots(
    clinic_id,
    dentist_id,
    service_id,
    requested_date
 )

@tool
def book_appointment_tool(
    clinic_id: int,
    appointment: AppointmentCreate,
) -> dict:
    """This tool book appointments for specific clinics."""
    return create_appointment_service(
        clinic_id,
        appointment,
    )

@tool
def cancel_appointment_tool(
    appointment_id: int,
) -> dict:
    """This tool cancel the appointment of patient in clinic where he is registred."""
    return cancel_appointment_service(
        appointment_id,
    )

@tool
def reschedule_appointment_tool(
    appointment_id: int,
    new_time: AppointmentReschedule,
) -> dict:
    """This tool reschedule the appointment of patient for clinic where he is registred."""
    return reschedule_appointment_service(
        appointment_id,
        new_time,
    )

@tool
def get_patient_appointments_tool(
        clinic_id:int,
        patient_id:int
) -> list[dict]:
    """This tool return appointments of only one patient from clinic where he is registred."""
    return get_patient_appointments_service(
        clinic_id,
        patient_id
    )