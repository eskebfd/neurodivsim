from pydantic import BaseModel, ConfigDict, Field


class UserProfileBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UserProfileAttribute(UserProfileBaseModel):
    attribute_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Stable technical ID of the reference configuration attribute.",
    )
    name: str = Field(..., min_length=1, description="Readable attribute name.")
    value: float = Field(
        ...,
        ge=0,
        le=100,
        description="Fixed configuration assumption on a scale from 0 to 100.",
    )
    description: str | None = Field(
        None,
        description="Optional explanation of the conceptual meaning.",
    )


class UserProfileDefinition(UserProfileBaseModel):
    profile_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_]*$",
        description="Stable technical ID of the reference configuration.",
    )
    label: str = Field(..., min_length=1, description="Readable name of the reference configuration.")
    is_baseline: bool = Field(
        False,
        description="Marks the generic comparison profile.",
    )
    attributes: dict[str, UserProfileAttribute] = Field(
        ...,
        min_length=1,
        description="Fixed, consistently structured configuration attributes.",
    )
