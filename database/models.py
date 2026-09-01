"""
SQLAlchemy models for the South Sudan National Registry.

The models are deliberately database-oriented and shared by:

    Next.js AI Studio
            |
        Registry API
            |
        SQLAlchemy
            |
      PostgreSQL / SQLite
            |
        Streamlit AI Studio
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


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
    )

    id_document_type: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    date_of_birth: Mapped[Optional[Date]] = mapped_column(
        Date,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    gender: Mapped[str] = mapped_column(
        String(50),
        default="Other",
    )

    marital_status: Mapped[str] = mapped_column(
        String(50),
        default="Single",
    )

    nationality: Mapped[str] = mapped_column(
        String(100),
        default="South Sudanese",
    )

    # --------------------------------------------------------
    # Contact
    # --------------------------------------------------------

    phone_number: Mapped[Optional[str]] = mapped_column(
        String(50),
    )

    email_address: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
    )

    # --------------------------------------------------------
    # Demographics
    # --------------------------------------------------------

    tribe: Mapped[str] = mapped_column(
        String(150),
        default="",
    )

    sub_tribe_or_clan: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    native_language: Mapped[str] = mapped_column(
        String(150),
        default="",
    )

    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
    )

    county_or_payam: Mapped[str] = mapped_column(
        String(150),
        default="",
    )

    sub_county_or_boma: Mapped[str] = mapped_column(
        String(150),
        default="",
    )

    boma: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    community: Mapped[str] = mapped_column(
        String(255),
        default="",
    )

    residential_address: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    duration_of_stay_years: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    # --------------------------------------------------------
    # Household
    # --------------------------------------------------------

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
    )

    is_household_head: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    household: Mapped[Optional["Household"]] = relationship(
        "Household",
        back_populates="members",
        foreign_keys=[household_id],
    )

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education_level: Mapped[str] = mapped_column(
        String(150),
        default="None / Informal",
    )

    is_literate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    employment_status: Mapped[str] = mapped_column(
        String(150),
        default="Unemployed / Seeking Work",
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

    # --------------------------------------------------------
    # Special Needs
    # --------------------------------------------------------

    has_special_needs_or_disability: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    # --------------------------------------------------------
    # Voter
    # --------------------------------------------------------

    voter_id_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
    )

    voter_status: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    constituency: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    polling_station_id: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    polling_station_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    has_voted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    voted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
    )

    # --------------------------------------------------------
    # Enumeration
    # --------------------------------------------------------

    enumerator_name: Mapped[str] = mapped_column(
        String(255),
        default="",
    )

    enumerator_badge_id: Mapped[str] = mapped_column(
        String(100),
        default="",
    )

    enumeration_date: Mapped[Optional[Date]] = mapped_column(
        Date,
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verification_status: Mapped[str] = mapped_column(
        String(100),
        default="Pending Review",
        index=True,
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    civil_events: Mapped[list["CivilEvent"]] = relationship(
        "CivilEvent",
        back_populates="citizen",
        cascade="all, delete-orphan",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="citizen",
        cascade="all, delete-orphan",
    )

    voter_record: Mapped[Optional["VoterRecord"]] = relationship(
        "VoterRecord",
        back_populates="citizen",
        uselist=False,
        cascade="all, delete-orphan",
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
    )

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
        index=True,
    )

    county_or_payam: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    sub_county_or_boma: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    boma: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    community: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    residential_address: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
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
    )

    citizen_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "citizens.id",
            ondelete="SET NULL",
        ),
        index=True,
    )

    event_date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
    )

    registration_centre: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    document_number: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    status: Mapped[str] = mapped_column(
        String(100),
        default="Pending Review",
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    citizen: Mapped[Optional[Citizen]] = relationship(
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

    status: Mapped[str] = mapped_column(
        String(100),
        default="Registered",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    citizen: Mapped[Optional[Citizen]] = relationship(
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
    )

    voter_id_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
    )

    voter_status: Mapped[str] = mapped_column(
        String(100),
        default="Active",
    )

    constituency: Mapped[Optional[str]] = mapped_column(
        String(150),
    )

    polling_station_id: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    polling_station_name: Mapped[Optional[str]] = mapped_column(
        String(255),
    )

    has_voted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    voted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    citizen: Mapped[Citizen] = relationship(
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
    )

    parent_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey(
            "administrative_units.id",
            ondelete="SET NULL",
        ),
    )

    state_or_region: Mapped[str] = mapped_column(
        String(150),
        default="",
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
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
    )

    username: Mapped[str] = mapped_column(
        String(255),
        default="system",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    details: Mapped[Optional[str]] = mapped_column(
        Text,
  )
