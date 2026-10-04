from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine
from app.schemas import PatientCreate


router = APIRouter(
    prefix = "/clinics/{clinic_id}/patients",
    tags = ["patients"]
)


@router.get("")
def list_patients_for_clinic(clinic_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT id, clinic_id, full_name, phone, email, created_at
                FROM patients
                WHERE clinic_id = :clinic_id
                ORDER BY id
                """
            ),
            {"clinic_id": clinic_id},
        )

        return [
            dict(row._mapping)
            for row in result
        ]


@router.post("", status_code=201)
def create_patient_for_clinic(
    clinic_id: int,
    patient: PatientCreate,
):
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """
                INSERT INTO patients (
                    clinic_id,
                    full_name,
                    phone,
                    email
                )
                VALUES (
                    :clinic_id,
                    :full_name,
                    :phone,
                    :email
                )
                RETURNING id, clinic_id, full_name, phone, email, created_at
                """
            ),
            {
                "clinic_id": clinic_id,
                "full_name": patient.full_name,
                "phone": patient.phone,
                "email": patient.email,
            },
        )

        row = result.one()

    return dict(row._mapping)
