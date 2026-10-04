from app.database import engine
from app.schemas import ClinicServiceCreate
from sqlalchemy import text
from fastapi import HTTPException  # type: ignore[import-not-found]




def list_services_for_clinic(clinic_id : int) -> list[dict]:
    with engine.connect() as connection:
        result = connection.execute(
            text("""
             SELECT
             id,
             clinic_id,
             name,
             price,
             active,
             duration_minutes,
             created_at
             FROM clinic_services
             WHERE clinic_id = :clinic_id
             AND active = TRUE
             ORDER BY id

               """),
               {"clinic_id":clinic_id}
        )

        return [
            dict(row._mapping)
            for row in result
        ]




def create_service_for_clinic(clinic_id: int,service : ClinicServiceCreate) -> dict:
    with engine.begin() as connection:
        clinic_exist = connection.execute(
            text("""SELECT 1
            FROM clinics
            WHERE id = :clinic_id"""),
            {"clinic_id":clinic_id}
            
        ).one_or_none()

        if clinic_exist is None:
            raise HTTPException(
                status_code=404,
                detail="Clinic not found."
            )


        result = connection.execute(text("""
        INSERT INTO clinic_services
        (
        clinic_id,
        name,
        price,
        duration_minutes)
        
        VALUES(
        :clinic_id,
        :name,
        :price,
        :duration_minutes
        )
        RETURNING id,clinic_id,name,price,active,duration_minutes,created_at"""),
        {"clinic_id":clinic_id,
          **service.model_dump()})

        row = result.one()

        return dict(row._mapping)