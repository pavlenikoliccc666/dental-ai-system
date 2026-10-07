from sqlalchemy import text
from fastapi import HTTPException
from app.database import engine
from app.schemas import AppointmentCreate
from app.schemas import AppointmentReschedule

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import text
from fastapi import HTTPException

def get_appointments_for_clinic(clinic_id: int) -> list[dict]:
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT
                    id,
                    clinic_id,
                    patient_id,
                    dentist_id,
                    starts_at,
                    ends_at,
                    status,
                    created_at
                FROM appointments
                WHERE clinic_id = :clinic_id
                ORDER BY starts_at
                """
            ),
            {"clinic_id": clinic_id},
        )

        return [
            dict(row._mapping)
            for row in result
        ]




def create_appointment(
    clinic_id: int,
    appointment: AppointmentCreate,
):
    if appointment.ends_at <= appointment.starts_at:
        raise HTTPException(
            status_code=400,
            detail="Appointment must end after it starts.",
        )

    params = {
        "clinic_id": clinic_id,
        **appointment.model_dump(),
    }

    with engine.begin() as connection:
        clinic_exist = connection.execute(
            text(
                """SELECT 1
                FROM clinics
                WHERE id = :clinic_id"""
            ),
            {"clinic_id":clinic_id},
            
        ).one_or_none()

        if clinic_exist is None:
            raise HTTPException(
                status_code=404,
                detail = "Clinic not found."
            )

        patient_belongs_to_clinic = connection.execute(
            text("""SELECT 1
            FROM patients
            WHERE id = :patient_id
                AND clinic_id = :clinic_id"""),
                {"clinic_id":clinic_id,
                 "patient_id":appointment.patient_id}
        ).one_or_none

        if patient_belongs_to_clinic is None:
            raise HTTPException(
                status_code=404,
                detail = "Patient not found in this clinic."
            )

        dentist_belong_to_clinic = connection.execute(
            text("""SELECT 1
            FROM dentists
            WHERE id = :dentist_id
            AND clinic_id = :clinic_id
            """),
            {"dentist_id":appointment.dentist_id,
             "clinic_id":clinic_id}
        )

        if dentist_belong_to_clinic is None:
            raise HTTPException(
                status_code=404,
                detail="Dentist not found"
            )
        
        
        existing_appointment = connection.execute(
            text(
                """
                SELECT 1
                FROM appointments
                WHERE dentist_id = :dentist_id
                  AND status = 'booked'
                  AND starts_at < :ends_at
                  AND ends_at > :starts_at
                LIMIT 1
                """
            ),
            {
                "dentist_id": appointment.dentist_id,
                "starts_at": appointment.starts_at,
                "ends_at": appointment.ends_at,
            },
        ).one_or_none()

        if existing_appointment is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Dentist already has an appointment "
                    "in this time range."
                ),
            )
        result = connection.execute(
            text(
                """
                INSERT INTO appointments (
                    clinic_id,
                    patient_id,
                    dentist_id,
                    starts_at,
                    ends_at
                )
                VALUES (
                    :clinic_id,
                    :patient_id,
                    :dentist_id,
                    :starts_at,
                    :ends_at
                )
                RETURNING
                    id,
                    clinic_id,
                    patient_id,
                    dentist_id,
                    starts_at,
                    ends_at,
                    status,
                    created_at
                """
            ),
            params,
        )

        row = result.one()

    return dict(row._mapping)




def cancel_appointment(appointment_id: int):
    with engine.begin() as connection:
        result = connection.execute(
            text(
                """
                UPDATE appointments
                SET status = 'cancelled'
                WHERE id = :appointment_id
                  AND status = 'booked'
                RETURNING
                    id,
                    clinic_id,
                    patient_id,
                    dentist_id,
                    starts_at,
                    ends_at,
                    status,
                    created_at
                """
            ),
            {"appointment_id": appointment_id},
        )

        row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Booked appointment not found.",
        )

    return dict(row._mapping)





def reschedule_appointment(
    appointment_id: int,
    new_time: AppointmentReschedule
) -> dict:
    if new_time.ends_at <= new_time.starts_at:
        raise HTTPException(
            status_code=400,
            detail="Appointment must end after it starts.",
        )

    with engine.begin() as connection:
        existing_appointment = connection.execute(
            text(
                """
                SELECT 1
                FROM appointments AS existing
                WHERE existing.dentist_id = (
                    SELECT dentist_id
                    FROM appointments
                    WHERE id = :appointment_id
                )
                  AND existing.id <> :appointment_id
                  AND existing.status = 'booked'
                  AND existing.starts_at < :ends_at
                  AND existing.ends_at > :starts_at
                LIMIT 1
                """
            ),
            {
                "appointment_id": appointment_id,
                "starts_at": new_time.starts_at,
                "ends_at": new_time.ends_at,
            },
        ).one_or_none()

        if existing_appointment is not None:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Dentist already has another appointment "
                    "in this time range."
                ),
            )
        
        result = connection.execute(
            text(
                """
                UPDATE appointments
                SET
                    starts_at = :starts_at,
                    ends_at = :ends_at
                WHERE id = :appointment_id
                  AND status = 'booked'
                RETURNING
                    id,
                    clinic_id,
                    patient_id,
                    dentist_id,
                    starts_at,
                    ends_at,
                    status,
                    created_at
                """
            ),
            {
                "appointment_id": appointment_id,
                "starts_at": new_time.starts_at,
                "ends_at": new_time.ends_at,
            },
        )

        row = result.one_or_none()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Booked appointment not found.",
            )

    return dict(row._mapping)





def find_available_slots(
    clinic_id: int,
    dentist_id: int,
    service_id: int,
    requested_date: date,
) -> list[dict]:
    with engine.connect() as connection:
        clinic = connection.execute(
            text(
                """
                SELECT timezone
                FROM clinics
                WHERE id = :clinic_id
                """
            ),
            {"clinic_id": clinic_id},
        ).one_or_none()

        if clinic is None:
            raise HTTPException(
                status_code=404,
                detail="Clinic not found.",
            )

        dentist = connection.execute(
            text(
                """
                SELECT 1
                FROM dentists
                WHERE id = :dentist_id
                  AND clinic_id = :clinic_id
                """
            ),
            {
                "dentist_id": dentist_id,
                "clinic_id": clinic_id,
            },
        ).one_or_none()

        if dentist is None:
            raise HTTPException(
                status_code=404,
                detail="Dentist not found in this clinic.",
            )

        service = connection.execute(
            text(
                """
                SELECT name, duration_minutes
                FROM clinic_services
                WHERE id = :service_id
                  AND clinic_id = :clinic_id
                  AND active = TRUE
                """
            ),
            {
                "service_id": service_id,
                "clinic_id": clinic_id,
            },
        ).one_or_none()

        if service is None:
            raise HTTPException(
                status_code=404,
                detail="Service not found in this clinic.",
            )

        day_of_week = requested_date.weekday()

        availability = connection.execute(
            text(
                """
                SELECT starts_at, ends_at
                FROM dentist_availability
                WHERE dentist_id = :dentist_id
                  AND clinic_id = :clinic_id
                  AND day_of_the_week = :day_of_week
                ORDER BY starts_at
                """
            ),
            {
                "dentist_id": dentist_id,
                "clinic_id": clinic_id,
                "day_of_week": day_of_week,
            },
        ).all()

        if not availability:
            return []

        timezone = ZoneInfo(clinic.timezone)

        day_start = datetime.combine(
            requested_date,
            datetime.min.time(),
        ).replace(tzinfo=timezone)

        day_end = day_start + timedelta(days=1)

        booked = connection.execute(
            text(
                """
                SELECT starts_at, ends_at
                FROM appointments
                WHERE clinic_id = :clinic_id
                  AND dentist_id = :dentist_id
                  AND status = 'booked'
                  AND starts_at < :day_end
                  AND ends_at > :day_start
                """
            ),
            {
                "clinic_id": clinic_id,
                "dentist_id": dentist_id,
                "day_start": day_start,
                "day_end": day_end,
            },
        ).all()

        slots = []
        duration = timedelta(
            minutes=service.duration_minutes
        )

        for window in availability:
            current_start = datetime.combine(
                requested_date,
                window.starts_at,
            ).replace(tzinfo=timezone)

            window_end = datetime.combine(
                requested_date,
                window.ends_at,
            ).replace(tzinfo=timezone)

            while current_start + duration <= window_end:
                current_end = current_start + duration

                overlaps = any(
                    current_start < booked_slot.ends_at
                    and current_end > booked_slot.starts_at
                    for booked_slot in booked
                )

                if not overlaps:
                    slots.append(
                        {
                            "service_id": service_id,
                            "dentist_id": dentist_id,
                            "date": requested_date.isoformat(),
                            "starts_at": current_start.isoformat(),
                            "ends_at": current_end.isoformat(),
                        }
                    )

                current_start += timedelta(minutes=30)

        return slots


def get_patient_appointments(clinic_id: int,patient_id: int) -> list[dict]:
    with engine.connect() as connection:
        clinic_exist = connection.execute(
            text(
                """SELECT 1
                FROM clinics
                WHERE id = :clinic_id"""
            ),
            {"clinic_id": clinic_id},
        ).scalar_one_or_none()

        if clinic_exist is None:
            raise HTTPException(
                status_code=404,
                detail="Clinic not found."
            )
            

        patient_belongs_to_clinic = connection.execute(
            text(
                """SELECT 1
                FROM patients
                WHERE id = :patient_id
                AND clinic_id = :clinic_id"""
            ),
            {
                "patient_id": patient_id,
                "clinic_id": clinic_id,
            },
        ).scalar_one_or_none()

        if patient_belongs_to_clinic is None:
            raise HTTPException(
             status_code=404,
             detail = "Patient doesnt belong to clinic or it doesnt exsit."
            )


        result = connection.execute(text(
            """
            SELECT
            id,
            clinic_id,
            patient_id,
            dentist_id,
            starts_at,
            ends_at,
            status,
            created_at
            FROM appointments
            WHERE patient_id = :patient_id
            AND clinic_id = :clinic_id
            AND status = 'booked'
            ORDER BY starts_at"""
        ),
        {
            "patient_id":patient_id,
            "clinic_id":clinic_id
        }).all()

        return[
            dict(row._mapping)
            for row in result
        ]


