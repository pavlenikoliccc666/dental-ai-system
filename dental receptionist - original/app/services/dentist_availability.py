from sqlalchemy import text
from fastapi import HTTPException
from app.database import engine
from app.schemas import DentistAvailabilityCreate


def list_availability_for_clinics(clinic_id: int,dentist_id: int) -> list[dict]:
    with engine.connect() as connection:
        
        result = connection.execute(text(
            """SELECT
            id,
            clinic_id,
            dentist_id,
            day_of_the_week,
            starts_at,
            ends_at
            FROM dentist_availability
            WHERE dentist_id = :dentist_id
            AND clinic_id = :clinic_id

            """
        ),
        {
            "dentist_id":dentist_id,
            "clinic_id":clinic_id
        })

        return [
            dict(row._mapping)
            for row in result
        ]



def create_availability_for_clinics(dentist_id:int,clinic_id:int,availability: DentistAvailabilityCreate):
    with engine.begin() as connection:
        dentist_check = connection.execute(text(
            """SELECT 1
        FROM dentists
        WHERE id = :dentist_id
        AND clinic_id = :clinic_id"""
        ),{
            "dentist_id":dentist_id,
            "clinic_id":clinic_id
        }).one_or_none()

        if dentist_check is None:
            raise HTTPException(
                status_code=404,
                detail="Dentist not found"
            )


        result = connection.execute(text("""
            INSERT INTO dentist_availability
            (dentist_id,
            clinic_id,
            day_of_the_week,
            starts_at,
            ends_at)
            VALUES
            (
            :dentist_id,
            :clinic_id,
            :day_of_the_week,
            :starts_at,
            :ends_at)
            RETURNING dentist_id,clinic_id,day_of_the_week,starts_at,ends_at
            """

        ),{
            "dentist_id":dentist_id,
            "clinic_id":clinic_id,
            **availability.model_dump()
        })

        row = result.one()

        return dict(row._mapping)