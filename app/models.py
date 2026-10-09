from datetime import datetime
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey
from decimal import Decimal
from sqlalchemy import Boolean, Numeric, Integer
from sqlalchemy import func
from datetime import time
from sqlalchemy import Time

from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass






class Clinic(Base):
    __tablename__ = "clinics"
    id : Mapped[int] = mapped_column(primary_key = True)

    name:Mapped[str] = mapped_column(String(200),nullable=False)

    city: Mapped[str] = mapped_column(String(100), nullable=False)

    timezone: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True),nullable=False)

    address: Mapped[str | None] = mapped_column(
    String(200),
    nullable=True)
                 





class Patient(Base):
    __tablename__ = "patients"

    id : Mapped[int] = mapped_column(primary_key=True)

    clinic_id : Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable = False)

    full_name : Mapped[str] = mapped_column(String(200),nullable=False)

    phone : Mapped[str] = mapped_column(String(200),nullable=False)

    email : Mapped[str] = mapped_column(String(200),nullable=True)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone= True),nullable=False)



class Dentist(Base):
    __tablename__ = "dentists"

    id: Mapped[int] = mapped_column(primary_key=True)

    clinic_id : Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable=False)

    full_name : Mapped[str] = mapped_column(String(200),nullable=False)

    specialization : Mapped[str] = mapped_column(String(100),nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)

    clinic_id : Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable=False)

    patient_id : Mapped[int] = mapped_column(ForeignKey("patients.id"),nullable=False)

    dentist_id : Mapped[int] = mapped_column(ForeignKey("dentists.id"),nullable=False)

    starts_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

    ends_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

    status : Mapped[str] = mapped_column(String(20),server_default="booked",nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)



class ClinicService(Base):
    __tablename__ = "clinic_services"

    id: Mapped[int] = mapped_column(primary_key=True)

    clinic_id : Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable=False)

    name : Mapped[str] = mapped_column(String(200),nullable=False)

    price : Mapped[Decimal | None] = mapped_column(Numeric(10,2),nullable=True)

    active : Mapped[bool] = mapped_column(Boolean,server_default="true",nullable=False)

    duration_minutes: Mapped[int] = mapped_column(
    Integer,
    nullable=False)

    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)



class DentistAvailability(Base):
    __tablename__ = "dentist_availability"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable=False)

    dentist_id: Mapped[int] = mapped_column(ForeignKey("dentists.id"),nullable=False)

    day_of_the_week: Mapped[int] = mapped_column(Integer,nullable=False)

    starts_at: Mapped[time] = mapped_column(Time,nullable=False)

    ends_at: Mapped[time] = mapped_column(Time,nullable=False)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"),nullable=False)

    content: Mapped[str] = mapped_column(String(2000),nullable=False)

    source: Mapped[str] = mapped_column(String(200),nullable=True)

    embedding: Mapped[list[float]] = mapped_column(Vector(1536),nullable=False)