"""Nominatim / OpenStreetMap address validator (free, no API key).

Geocodes the address against OpenStreetMap data via the Nominatim API. A match
means the address resolves to a known real-world location in OSM.

IMPORTANT: This is NOT a USPS deliverability check. It confirms the address
*exists / can be located*, not that USPS will deliver mail to it (it cannot
detect vacant units, non-mailable addresses, or do USPS DPV/CASS). Use USPS or
Smarty for true mailing verification.

Usage policy (public server, https://operations.osmfoundation.org/policies/nominatim/):
  - Max ~1 request/second.
  - A valid, descriptive User-Agent / Referer is REQUIRED (requests without one
    are blocked). Set NOMINATIM_USER_AGENT in .env.
  - For heavy use, self-host and point NOMINATIM_URL at your instance.
"""
from __future__ import annotations

import httpx

from ..models import AddressValidationRequest, ValidatedAddress
from .base import AddressValidator

# OSM place types that indicate a precise, mailable-ish match (house/building level)
_PRECISE_TYPES = {"house", "building", "residential", "address"}


class NominatimValidator(AddressValidator):
    name = "nominatim"

    def __init__(self, base_url: str, user_agent: str):
        if not user_agent:
            raise ValueError(
                "NOMINATIM_USER_AGENT is required (Nominatim blocks requests "
                "without a descriptive User-Agent)."
            )
        self.base_url = (base_url or "https://nominatim.openstreetmap.org").rstrip("/")
        self.user_agent = user_agent

    async def validate(self, req: AddressValidationRequest) -> ValidatedAddress:
        # Structured query gives Nominatim the best shot at a precise match.
        street = " ".join(p for p in [req.secondary, req.street] if p) if req.secondary else req.street
        params = {
            "street": street or "",
            "city": req.city or "",
            "state": req.state or "",
            "postalcode": req.zip_code or "",
            "country": "USA",
            "format": "jsonv2",
            "addressdetails": "1",
            "limit": "1",
        }
        # Drop empty params so Nominatim doesn't over-constrain
        params = {k: v for k, v in params.items() if v}
        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}/search", params=params, headers=headers)
            resp.raise_for_status()
            results = resp.json()

        if not results:
            return ValidatedAddress(
                is_valid=False,
                provider=self.name,
                deliverable=None,
                messages=[
                    "Address could not be located in OpenStreetMap (no geocoding match).",
                    "Note: this is an OSM geocoding check, not USPS deliverability.",
                ],
                raw_response={"results": []},
            )

        r = results[0]
        addr = r.get("address", {})
        osm_type = r.get("type") or r.get("addresstype") or ""

        house_number = addr.get("house_number")
        road = addr.get("road")
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("hamlet")
        state = addr.get("ISO3166-2-lvl4", "").replace("US-", "") or _state_abbr(addr.get("state"))
        postcode = addr.get("postcode")
        zip5, zip4 = (postcode.split("-") + [None])[:2] if postcode and "-" in postcode else (postcode, None)

        # Precise if OSM returned a house number (rooftop-ish) match.
        precise = bool(house_number) or osm_type in _PRECISE_TYPES
        std_street = " ".join(p for p in [house_number, road] if p) or None

        messages = []
        if precise:
            messages.append("Address located in OpenStreetMap at building/house level.")
        else:
            messages.append(
                "Approximate match only — OSM located the street/area but not an exact building."
            )
        messages.append("Note: OSM geocoding match, not USPS-verified deliverability.")
        if r.get("display_name"):
            messages.append(f"OSM: {r['display_name']}")

        return ValidatedAddress(
            is_valid=precise,
            provider=self.name,
            deliverable=None,  # OSM cannot determine USPS deliverability
            standardized_street=std_street,
            standardized_secondary=req.secondary,
            standardized_city=city,
            standardized_state=state or None,
            standardized_zip=zip5,
            standardized_zip4=zip4,
            messages=messages,
            raw_response=r,
        )


_STATE_NAME_TO_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "district of columbia": "DC", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "puerto rico": "PR",
}


def _state_abbr(name):
    if not name:
        return None
    return _STATE_NAME_TO_ABBR.get(name.strip().lower(), name)
