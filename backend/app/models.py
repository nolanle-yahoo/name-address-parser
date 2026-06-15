from typing import Literal, Optional

from pydantic import BaseModel, Field


# ----------------------------- Name -----------------------------
class NameParseRequest(BaseModel):
    name: str = Field(..., examples=["Dr. John A. Smith Jr.", "Acme Plumbing & Supply LLC"])


class ParsedName(BaseModel):
    entity_type: Literal["person", "business", "household", "unknown"]
    is_business: bool
    # Person components
    prefix: Optional[str] = None          # Dr., Mr., Mrs.
    first: Optional[str] = None
    middle: Optional[str] = None
    last: Optional[str] = None
    suffix: Optional[str] = None          # Jr., Sr., III
    nickname: Optional[str] = None
    # Business component
    business_name: Optional[str] = None
    # Diagnostics
    raw: str
    confidence: float = 0.0
    components: dict = Field(default_factory=dict)


# ----------------------------- Address -----------------------------
class AddressParseRequest(BaseModel):
    address: str = Field(
        ..., examples=["1600 Pennsylvania Ave NW Suite 200, Washington, DC 20500"]
    )


class ParsedAddress(BaseModel):
    street_number: Optional[str] = None
    pre_directional: Optional[str] = None      # N, S, E, W (before street name)
    street_name: Optional[str] = None
    street_suffix: Optional[str] = None        # St, Ave, Blvd
    post_directional: Optional[str] = None     # NW, SE (after street name)
    unit_type: Optional[str] = None            # Suite, Apt, Unit
    unit_number: Optional[str] = None
    po_box: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    zip_plus4: Optional[str] = None
    raw: str
    address_type: str = "Street Address"
    components: dict = Field(default_factory=dict)


# ----------------------------- Validation -----------------------------
class AddressValidationRequest(BaseModel):
    street: str = Field(..., examples=["1600 Pennsylvania Ave NW"])
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    secondary: Optional[str] = Field(None, description="Apt/Suite line", examples=["Suite 200"])


class ValidatedAddress(BaseModel):
    is_valid: bool
    provider: str
    deliverable: Optional[bool] = None
    # Standardized / corrected address as returned by the provider
    standardized_street: Optional[str] = None
    standardized_secondary: Optional[str] = None
    standardized_city: Optional[str] = None
    standardized_state: Optional[str] = None
    standardized_zip: Optional[str] = None
    standardized_zip4: Optional[str] = None
    messages: list[str] = Field(default_factory=list)
    raw_response: dict = Field(default_factory=dict)


# ----------------------------- Combined -----------------------------
class FullParseRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    validate_address: bool = True


class FullParseResponse(BaseModel):
    name: Optional[ParsedName] = None
    address: Optional[ParsedAddress] = None
    validation: Optional[ValidatedAddress] = None
