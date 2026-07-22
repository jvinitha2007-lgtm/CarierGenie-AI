from pydantic import BaseModel, ConfigDict, EmailStr, Field

class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    role: str = Field(min_length=2, max_length=160)
    skills: list[str] = Field(default_factory=list, max_length=30)

class ApplicationUpdate(BaseModel):
    opportunity_id: int
    status: str = Field(pattern='^(Saved|Applied|Interview|Offers)$')

class ProfileResponse(ProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    role_name: str