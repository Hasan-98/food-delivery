# Dispatch Service uses shared models for schemas
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from shared.models import (
    Driver as DriverSchema,
    DriverCreate,
    DriverCreateRequest,
    DriverStatus
)

__all__ = ["DriverSchema", "DriverCreate", "DriverCreateRequest", "DriverStatus"]

