"""Parse a US address into individual mailing components using ``usaddress``.

usaddress is a probabilistic parser trained on US address data and produces
fine-grained tags (street number, directionals, suffix, unit, etc.).
"""
from __future__ import annotations

from ..models import ParsedAddress

try:
    import usaddress

    _HAS_USADDRESS = True
except Exception:  # pragma: no cover
    _HAS_USADDRESS = False


# usaddress tag -> our field
_MAP = {
    "AddressNumber": "street_number",
    "AddressNumberPrefix": "street_number",
    "AddressNumberSuffix": "street_number",
    "StreetNamePreDirectional": "pre_directional",
    "StreetNamePreType": "street_name",          # e.g. "Avenue of the Americas"
    "StreetName": "street_name",
    "StreetNamePostType": "street_suffix",
    "StreetNamePostDirectional": "post_directional",
    "OccupancyType": "unit_type",
    "OccupancyIdentifier": "unit_number",
    "SubaddressType": "unit_type",
    "SubaddressIdentifier": "unit_number",
    "USPSBoxType": "po_box",
    "USPSBoxID": "po_box",
    "USPSBoxGroupType": "po_box",
    "USPSBoxGroupID": "po_box",
    "PlaceName": "city",
    "StateName": "state",
    "ZipCode": "zip_code",
}


def _join(existing, value):
    return f"{existing} {value}".strip() if existing else value


def parse_address(raw: str) -> ParsedAddress:
    raw = (raw or "").strip()
    if not raw:
        return ParsedAddress(raw=raw, address_type="Unknown")

    if not _HAS_USADDRESS:
        return ParsedAddress(raw=raw, address_type="Unparsed (usaddress unavailable)")

    try:
        tagged, addr_type = usaddress.tag(raw)
    except usaddress.RepeatedLabelError as e:
        # Fall back to the raw token list when the parser sees ambiguity
        tagged = {}
        for value, label in e.parsed_string:
            field = _MAP.get(label)
            if field:
                tagged[label] = _join(tagged.get(label), value)
        addr_type = "Ambiguous"

    fields: dict[str, str] = {}
    components = dict(tagged)
    for label, value in tagged.items():
        field = _MAP.get(label)
        if field:
            fields[field] = _join(fields.get(field), value)

    zip_code = fields.get("zip_code")
    zip_plus4 = None
    if zip_code and "-" in zip_code:
        zip_code, zip_plus4 = zip_code.split("-", 1)

    po_box = fields.get("po_box")
    address_type = "PO Box" if po_box else (addr_type or "Street Address")

    return ParsedAddress(
        street_number=fields.get("street_number"),
        pre_directional=fields.get("pre_directional"),
        street_name=fields.get("street_name"),
        street_suffix=fields.get("street_suffix"),
        post_directional=fields.get("post_directional"),
        unit_type=fields.get("unit_type"),
        unit_number=fields.get("unit_number"),
        po_box=po_box,
        city=fields.get("city"),
        state=fields.get("state"),
        zip_code=zip_code,
        zip_plus4=zip_plus4,
        raw=raw,
        address_type=address_type,
        components=components,
    )
