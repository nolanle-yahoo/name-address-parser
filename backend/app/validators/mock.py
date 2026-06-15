"""Offline validator used when no external provider credentials are configured.

It performs lightweight structural checks (state code, ZIP format, required
fields) so the app is fully runnable out of the box. It does NOT confirm true
mailing deliverability — configure USPS or Smarty for that.
"""
import re

from ..models import AddressValidationRequest, ValidatedAddress
from .base import AddressValidator

_US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
    "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
    "WI", "WY", "DC", "PR", "VI", "GU", "AS", "MP",
}
_ZIP_RE = re.compile(r"^\d{5}(-\d{4})?$")


class MockValidator(AddressValidator):
    name = "mock"

    async def validate(self, req: AddressValidationRequest) -> ValidatedAddress:
        messages: list[str] = []
        valid = True

        if not req.street or not req.street.strip():
            messages.append("Street is required.")
            valid = False

        state = (req.state or "").strip().upper()
        if state and state not in _US_STATES:
            messages.append(f"'{state}' is not a recognized US state/territory code.")
            valid = False

        zip_code = (req.zip_code or "").strip()
        if zip_code and not _ZIP_RE.match(zip_code):
            messages.append("ZIP must be 5 digits or ZIP+4 (#####-####).")
            valid = False

        if not (req.city or req.zip_code):
            messages.append("Provide at least a city or a ZIP code.")
            valid = False

        if valid:
            messages.append("Passed offline structural checks (mock provider — not USPS-verified).")

        zip5, zip4 = (zip_code.split("-") + [None])[:2] if "-" in zip_code else (zip_code or None, None)

        return ValidatedAddress(
            is_valid=valid,
            provider=self.name,
            deliverable=None,  # unknown without a real provider
            standardized_street=req.street,
            standardized_secondary=req.secondary,
            standardized_city=req.city,
            standardized_state=state or None,
            standardized_zip=zip5,
            standardized_zip4=zip4,
            messages=messages,
        )
