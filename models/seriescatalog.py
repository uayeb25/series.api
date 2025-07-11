from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SeriesCatalog(BaseModel):
    id: Optional[int] = Field(
        default=None,
        ge=1,
        description="Auto-generated ID, optional for input"
    )

    name: Optional['str'] = Field(
        default=None
    )

    original_name: Optional['str'] = Field(
        default=None
    )

    overview: Optional['str'] = Field(
        default=None
    )

    status: Optional['str'] = Field(
        default=None
    )

    original_language: Optional['str'] = Field(
        default=None
    )

