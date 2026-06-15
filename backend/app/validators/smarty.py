"""Smarty (SmartyStreets) US Street Address API validator.

Docs: https://www.smarty.com/docs/cloud/us-street-api
Requires an auth-id / auth-token key pair.

Returns DPV (Delivery Point Validation) info indicating true mailing
deliverability plus the USPS-standardized address.
"""
import httpx

from ..models import AddressValidationRequest, ValidatedAddress
from .base import AddressValidator

_ENDPOINT = "https://us-street.api.smarty.com/street-address"


class SmartyValidator(AddressValidator):
    name = "smarty"

    def __init__(self, auth_id: str, auth_token: str, license_: str = ""):
        if not auth_id or not auth_token:
            raise ValueError("SMARTY_AUTH_ID and SMARTY_AUTH_TOKEN are required for Smarty.")
        self.auth_id = auth_id
        self.auth_token = auth_token
        self.license = license_

    async def validate(self, req: AddressValidationRequest) -> ValidatedAddress:
        params = {
            "auth-id": self.auth_id,
            "auth-token": self.auth_token,
            "street": req.street or "",
            "secondary": req.secondary or "",
            "city": req.city or "",
            "state": req.state or "",
            "zipcode": req.zip_code or "",
            "candidates": "1",
            "match": "enhanced",
        }
        if self.license:
            params["license"] = self.license

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(_ENDPOINT, params=params)
            resp.raise_for_status()
            data = resp.json()

        if not data:
            return ValidatedAddress(
                is_valid=False, provider=self.name, deliverable=False,
                messages=["Address could not be verified — no USPS match found."],
                raw_response={"candidates": []},
            )

        c = data[0]
        comp = c.get("components", {})
        meta = c.get("metadata", {})
        analysis = c.get("analysis", {})

        dpv = analysis.get("dpv_match_code", "")
        # Y = confirmed, S = confirmed w/ secondary dropped, D = confirmed w/o secondary
        deliverable = dpv in {"Y", "S", "D"}

        messages = []
        if deliverable:
            messages.append("Address verified as deliverable (USPS DPV confirmed).")
        else:
            messages.append("Address not confirmed deliverable by USPS DPV.")
        if dpv:
            messages.append(f"DPV match code: {dpv}")
        if analysis.get("dpv_vacant") == "Y":
            messages.append("Note: USPS reports this address as vacant.")

        zip_code = comp.get("zipcode")
        plus4 = comp.get("plus4_code")

        return ValidatedAddress(
            is_valid=deliverable,
            provider=self.name,
            deliverable=deliverable,
            standardized_street=c.get("delivery_line_1"),
            standardized_secondary=c.get("delivery_line_2"),
            standardized_city=comp.get("city_name"),
            standardized_state=comp.get("state_abbreviation"),
            standardized_zip=zip_code,
            standardized_zip4=plus4,
            messages=messages,
            raw_response=c,
        )
