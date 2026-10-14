from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator, field_validator


class StudentFields(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    date_of_birth: date
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    course: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=300)
    enrollment_date: date | None = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_must_not_be_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class StudentCreate(StudentFields):
    @model_validator(mode="after")
    def require_contact_method(self):
        if not self.email and not self.phone:
            raise ValueError("Provide at least an email address or phone number")
        return self


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    date_of_birth: date | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    course: str | None = Field(default=None, max_length=120)
    address: str | None = Field(default=None, max_length=300)
    enrollment_date: date | None = None

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    @field_validator("name", "date_of_birth", mode="before")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_must_not_be_future(cls, value):
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class StudentRead(StudentFields):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
