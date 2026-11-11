import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VisitorRegistrationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    consent: bool

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Name must contain at least one non-whitespace character")
        return normalized

    @field_validator("consent")
    @classmethod
    def require_consent(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Consent is required to register")
        return value


class VisitorVerificationRequest(BaseModel):
    access_code: str = Field(min_length=16, max_length=19)

    @field_validator("access_code")
    @classmethod
    def normalize_access_code(cls, value: str) -> str:
        normalized = re.sub(r"[\s-]", "", value).upper()
        if not re.fullmatch(r"[A-HJ-NP-Z2-9]{16}", normalized):
            raise ValueError("Enter a valid access code")
        return normalized


class VisitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class VisitorRegistrationResponse(VisitorResponse):
    access_code: str
