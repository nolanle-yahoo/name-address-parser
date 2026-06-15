from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import (
    AddressParseRequest,
    AddressValidationRequest,
    FullParseRequest,
    FullParseResponse,
    NameParseRequest,
    ParsedAddress,
    ParsedName,
    ValidatedAddress,
)
from .parsers.address_parser import parse_address
from .parsers.name_parser import parse_name
from .validators.factory import get_validator

settings = get_settings()

app = FastAPI(
    title="Name / Address Parser & Validator",
    description=(
        "Parses US consumer and business names and US mailing addresses into "
        "components, and validates addresses against an external provider "
        "(USPS / Smarty), with an offline mock fallback."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"http://localhost:\d+|http://127\.0\.0\.1:\d+|exp://.*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "validator": get_validator().name}


@app.post("/api/parse/name", response_model=ParsedName)
async def api_parse_name(req: NameParseRequest):
    return parse_name(req.name)


@app.post("/api/parse/address", response_model=ParsedAddress)
async def api_parse_address(req: AddressParseRequest):
    return parse_address(req.address)


@app.post("/api/validate/address", response_model=ValidatedAddress)
async def api_validate_address(req: AddressValidationRequest):
    validator = get_validator()
    return await validator.validate(req)


@app.post("/api/parse", response_model=FullParseResponse)
async def api_parse_full(req: FullParseRequest):
    """Parse a name and/or address in one call, optionally validating the address."""
    parsed_name = parse_name(req.name) if req.name else None
    parsed_address = parse_address(req.address) if req.address else None

    validation = None
    if parsed_address and req.validate_address:
        v_req = AddressValidationRequest(
            street=" ".join(
                p for p in [
                    parsed_address.street_number,
                    parsed_address.pre_directional,
                    parsed_address.street_name,
                    parsed_address.street_suffix,
                    parsed_address.post_directional,
                ] if p
            ) or (parsed_address.po_box or parsed_address.raw),
            secondary=" ".join(
                p for p in [parsed_address.unit_type, parsed_address.unit_number] if p
            ) or None,
            city=parsed_address.city,
            state=parsed_address.state,
            zip_code=(
                f"{parsed_address.zip_code}-{parsed_address.zip_plus4}"
                if parsed_address.zip_code and parsed_address.zip_plus4
                else parsed_address.zip_code
            ),
        )
        validation = await get_validator().validate(v_req)

    return FullParseResponse(
        name=parsed_name, address=parsed_address, validation=validation
    )
