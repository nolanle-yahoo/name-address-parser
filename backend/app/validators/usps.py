"""USPS Web Tools Address Validation (Address Standardization API).

Docs: https://www.usps.com/business/web-tools-apis/address-information-api.htm
Requires a free USERID from USPS Web Tools registration.

The API confirms whether an address is a valid, mailable US address and returns
the standardized/corrected form.
"""
import xml.etree.ElementTree as ET
from urllib.parse import quote

import httpx

from ..models import AddressValidationRequest, ValidatedAddress
from .base import AddressValidator

_ENDPOINT = "https://secure.shippingapis.com/ShippingAPI.dll"


class USPSValidator(AddressValidator):
    name = "usps"

    def __init__(self, user_id: str):
        if not user_id:
            raise ValueError("USPS_USER_ID is required for the USPS validator.")
        self.user_id = user_id

    def _build_xml(self, req: AddressValidationRequest) -> str:
        def esc(v: str | None) -> str:
            return (v or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # USPS: Address1 = secondary (apt/suite), Address2 = street
        return (
            f'<AddressValidateRequest USERID="{esc(self.user_id)}">'
            f"<Revision>1</Revision>"
            f'<Address ID="0">'
            f"<Address1>{esc(req.secondary)}</Address1>"
            f"<Address2>{esc(req.street)}</Address2>"
            f"<City>{esc(req.city)}</City>"
            f"<State>{esc(req.state)}</State>"
            f"<Zip5>{esc((req.zip_code or '')[:5])}</Zip5>"
            f"<Zip4></Zip4>"
            f"</Address>"
            f"</AddressValidateRequest>"
        )

    async def validate(self, req: AddressValidationRequest) -> ValidatedAddress:
        xml = self._build_xml(req)
        url = f"{_ENDPOINT}?API=Verify&XML={quote(xml)}"

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)

        # Top-level error
        err = root.find("Description")
        if root.tag == "Error" and err is not None:
            return ValidatedAddress(
                is_valid=False, provider=self.name, deliverable=False,
                messages=[err.text or "USPS error"], raw_response={"xml": resp.text},
            )

        addr = root.find("Address")
        if addr is None:
            return ValidatedAddress(
                is_valid=False, provider=self.name, deliverable=False,
                messages=["No address returned by USPS."], raw_response={"xml": resp.text},
            )

        def get(tag):
            el = addr.find(tag)
            return el.text if el is not None else None

        addr_err = addr.find("Error")
        if addr_err is not None:
            desc = addr_err.find("Description")
            return ValidatedAddress(
                is_valid=False, provider=self.name, deliverable=False,
                messages=[(desc.text if desc is not None else "Address not found in USPS database.")],
                raw_response={"xml": resp.text},
            )

        messages = []
        return_text = get("ReturnText")
        if return_text:
            messages.append(return_text)
        messages.append("Address confirmed deliverable by USPS.")

        return ValidatedAddress(
            is_valid=True,
            provider=self.name,
            deliverable=True,
            standardized_street=get("Address2"),
            standardized_secondary=get("Address1"),
            standardized_city=get("City"),
            standardized_state=get("State"),
            standardized_zip=get("Zip5"),
            standardized_zip4=get("Zip4"),
            messages=messages,
            raw_response={"xml": resp.text},
        )
