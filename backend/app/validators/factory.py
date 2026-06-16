from ..config import get_settings
from .base import AddressValidator
from .mock import MockValidator
from .nominatim import NominatimValidator
from .smarty import SmartyValidator
from .usps import USPSValidator


def get_validator() -> AddressValidator:
    """Select the active validator based on configuration.

    Falls back to the offline mock validator if the requested provider is
    missing required credentials, so the app always runs.
    """
    s = get_settings()
    choice = (s.address_validator or "mock").lower()

    try:
        if choice == "usps":
            return USPSValidator(user_id=s.usps_user_id)
        if choice == "smarty":
            return SmartyValidator(
                auth_id=s.smarty_auth_id,
                auth_token=s.smarty_auth_token,
                license_=s.smarty_license,
            )
        if choice == "nominatim":
            return NominatimValidator(
                base_url=s.nominatim_url,
                user_agent=s.nominatim_user_agent,
            )
    except ValueError:
        # Misconfigured provider -> degrade gracefully to mock
        return MockValidator()

    return MockValidator()
