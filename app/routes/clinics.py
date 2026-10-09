from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine
from app.schemas import ClinicCreate
from fastapi import HTTPException


router = APIRouter(
    prefix="/clinics",
    tags=["clinics"],
)


@router.get("")
def list_clinics():
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT id, name, city, timezone
                FROM clinics
                ORDER BY id
                """
            )
        )

        return [
            dict(row._mapping)
            for row in result
        ]






@router.post("",status_code=201)
def create_clinic(clinic:ClinicCreate):
    with engine.begin() as connection:
        result = connection.execute(
            text("""INSERT INTO clinics(name,city,timezone)
            VALUES(:name,:city,:timezone)
            RETURNING id, name, city, timezone, created_at"""),
            clinic.model_dump()
        )

        row=result.one()

        return dict(row._mapping)





@router.get("/{clinics}")
def get_clinic(clinic_id: int):
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT id, name, city, timezone
                FROM clinics
                WHERE id = :clinic_id
                """
            ),
            {"clinic_id": clinic_id},
        )

        row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Clinic not found",
        )

    return dict(row._mapping)