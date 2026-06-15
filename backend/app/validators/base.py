from abc import ABC, abstractmethod

from ..models import AddressValidationRequest, ValidatedAddress


class AddressValidator(ABC):
    """Interface every external validation provider implements."""

    name: str = "base"

    @abstractmethod
    async def validate(self, req: AddressValidationRequest) -> ValidatedAddress:
        ...
