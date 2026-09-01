"""
SQLAlchemy models for the South Sudan National Registry.

Shared architecture:

    Next.js AI Studio
            |
        Registry API
            |
        Services
            |
        SQLAlchemy
            |
    PostgreSQL / SQLite
            |
        Streamlit AI Studio

The database models are independent of the frontend.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database.database import Base


# ============================================================
# CITIZEN
# ============================================================

class Citizen(Base):

    __tablename__ = "citizens"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    national_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    passport_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    id_document_type: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        index=True,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(50),
        default="Other",
        nullable=False,
    )

    marital_status: Mapped[str] = mapped_column(
        String(50),
        default="Single",
        nullable=False,
    )

    nationality: Mapped[str] = mapped_column(
        String(100),
        default="South Sudanese",
        nullable=False,
    )

    phone_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        index=True,
    )

    email_address: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
    )

    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
    )

    tribe: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
    )

    sub_tribe_or_clan: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    native_language: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
    )

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
        nullable=False,
    )

    county_or_payam: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
        nullable=False,
    )

    sub_county_or_boma: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
    )

    boma: Mapped[Optional[str]] = mapped_column(
        String(150),
        index=True,
    )

    community: Mapped[str] = mapped_column(
        String(255),
        default="",
        index=True,
        nullable=False,
    )

    residential_address: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    duration_of_stay_years: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    household_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "households.id",
            ondelete="SET NULL",
        ),
        index=True,
    )

    household_role: Mapped[str] = mapped_column(
        String(100),
        default="Head of Household",
        nullable=False,
    )

    is_household_head: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    education_level: Mapped[str] = mapped_column(
        String(150),
        default="None / Informal",
        nullable=False,
    )

    is_literate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    employment_status: Mapped[str] = mapped_column(
        String(150),
        default="Unemployed / Seeking Work",
        nullable=False,
    )

    primary_occupation: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    employer_or_business_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    industry_sector: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    monthly_income_range: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    has_special_needs_or_disability: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    disability_type: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    mother_alive: Mapped[Optional[bool]] = mapped_column(
        Boolean,
    )

    father_alive: Mapped[Optional[bool]] = mapped_column(
        Boolean,
    )

    voter_id_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    voter_status: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    constituency: Mapped[Optional[str]] = mapped_column(
        String(150),
        index=True,
    )

    polling_station_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    polling_station_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    has_voted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    voted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
    )

    enumerator_name: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=False,
    )

    enumerator_badge_id: Mapped[str] = mapped_column(
        String(100),
        default="",
        nullable=False,
    )

    enumeration_date: Mapped[Optional[date]] = mapped_column(
        Date,
    )

    verification_status: Mapped[str] = mapped_column(
        String(100),
        default="Pending Review",
        nullable=False,
        index=True,
    )

    verification_notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
    )

    verified_by: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    household: Mapped[Optional["Household"]] = relationship(
        "Household",
        back_populates="members",
        foreign_keys=[household_id],
    )

    civil_events: Mapped[list["CivilEvent"]] = relationship(
        "CivilEvent",
        back_populates="citizen",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="citizen",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    voter_record: Mapped[Optional["VoterRecord"]] = relationship(
        "VoterRecord",
        back_populates="citizen",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "ix_citizens_name_location",
            "full_name",
            "state_or_region",
            "county_or_payam",
        ),
    )


# ============================================================
# HOUSEHOLD
# ============================================================

class Household(Base):

    __tablename__ = "households"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    household_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    head_citizen_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        index=True,
    )

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
        nullable=False,
    )

    county_or_payam: Mapped[Optional[str]] = mapped_column(
        String(150),
        index=True,
    )

    sub_county_or_boma: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    boma: Mapped[Optional[str]] = mapped_column(
        String(150),
        index=True,
    )

    community: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
    )

    residential_address: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    members: Mapped[list["Citizen"]] = relationship(
        "Citizen",
        back_populates="household",
        foreign_keys="Citizen.household_id",
    )


# ============================================================
# CIVIL EVENT
# ============================================================

class CivilEvent(Base):

    __tablename__ = "civil_events"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    reference_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    citizen_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "citizens.id",
            ondelete="SET NULL",
        ),
        index=True,
    )

    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    registration_centre: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
    )

    document_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        default="Pending Review",
        nullable=False,
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    citizen: Mapped[Optional["Citizen"]] = relationship(
        "Citizen",
        back_populates="civil_events",
    )


# ============================================================
# DOCUMENT
# ============================================================

class Document(Base):

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    document_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    citizen_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "citizens.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
    )

    status: Mapped[str] = mapped_column(
        String(100),
        default="Registered",
        nullable=False,
        index=True,
    )

    issued_date: Mapped[Optional[date]] = mapped_column(
        Date,
    )

    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    citizen: Mapped[Optional["Citizen"]] = relationship(
        "Citizen",
        back_populates="documents",
    )


# ============================================================
# VOTER RECORD
# ============================================================

class VoterRecord(Base):

    __tablename__ = "voter_records"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    citizen_id: Mapped[str] = mapped_column(
        ForeignKey(
            "citizens.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    voter_id_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    voter_status: Mapped[str] = mapped_column(
        String(100),
        default="Active",
        nullable=False,
        index=True,
    )

    constituency: Mapped[Optional[str]] = mapped_column(
        String(150),
        index=True,
    )

    polling_station_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    polling_station_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    has_voted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    voted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    citizen: Mapped["Citizen"] = relationship(
        "Citizen",
        back_populates="voter_record",
    )


# ============================================================
# ADMINISTRATIVE UNIT
# ============================================================

class AdministrativeUnit(Base):

    __tablename__ = "administrative_units"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    unit_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    parent_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "administrative_units.id",
            ondelete="SET NULL",
        ),
        index=True,
    )

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
    )

    administrator_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    headquarters: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    target_population: Mapped[Optional[int]] = mapped_column(
        Integer,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    parent: Mapped[Optional["AdministrativeUnit"]] = relationship(
        "AdministrativeUnit",
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[list["AdministrativeUnit"]] = relationship(
        "AdministrativeUnit",
        back_populates="parent",
    )


# ============================================================
# AUDIT LOG
# ============================================================

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(255),
        default="system",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
    )
