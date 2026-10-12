# pyright: reportMissingImports=false
from fastapi import FastAPI
from app.agent import lifespan
app = FastAPI(title="AI Dental Receptionist",lifespan=lifespan)
from app.routes.patients import router as patient_router
from app.routes.clinics import router as clinics_router
from app.routes.appointments import router as appointment_router,cancel_router,find_appointments_patient_router
from app.routes.dentists import router as dentists_router
from app.routes.clinic_services import router as clinic_services_router
from app.routes.dentist_availability import router as dentist_availability_router
from app.routes.chat import router as chat_router
app.include_router(clinics_router)
app.include_router(patient_router)
app.include_router(appointment_router)
app.include_router(dentists_router)
app.include_router(cancel_router)
app.include_router(clinic_services_router)
app.include_router(dentist_availability_router)
app.include_router(find_appointments_patient_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return{
        "status":"Ok"
    }