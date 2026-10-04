from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.schemas import DentistCreate


router = APIRouter(
    prefix="/clinics/{clinic_id}/dentists",
    tags=["dentists"],
)


@router.get("")
def list_dentists_for_clinic(clinic_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT id, clinic_id, full_name, specialization, created_at
                FROM dentists
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
def create_dentist_for_clinic(
    clinic_id: int,
    dentist: DentistCreate,
):
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """
                INSERT INTO dentists (
                    clinic_id,
                    full_name,
                    specialization
                )
                VALUES (
                    :clinic_id,
                    :full_name,
                    :specialization
                )
                RETURNING id, clinic_id, full_name, specialization, created_at
                """
            ),
            {
                "clinic_id": clinic_id,
                **dentist.model_dump(),
            },
        )

        row = result.one()

        return dict(row._mapping)