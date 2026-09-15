"""
File Name: network_validation.py
Created Date: 2026-09-15
Author: Alex
Description:
    Provides reusable validation functions for DICOM network
    settings, Study Date values, and DICOM UIDs.
"""

import ipaddress
import warnings
from datetime import datetime

from pydicom.uid import UID


class ValidationError(ValueError):
    """Represent a validation error with a UI-friendly title."""

    def __init__(self, title, message):
        super().__init__(message)
        self.title = title
        self.message = message


def validate_ae_title(value, name):
    """Validate and normalize a DICOM AE Title."""
    value = value.strip()

    if not value:
        raise ValidationError(
            f"Missing {name}",
            f"{name} is required.",
        )

    if len(value) > 16:
        raise ValidationError(
            f"Invalid {name}",
            f"{name} must be 16 characters or fewer.",
        )

    return value


def validate_port(value, name):
    """Validate a TCP port number."""
    if not 1 <= value <= 65535:
        raise ValidationError(
            f"Invalid {name}",
            f"{name} must be between 1 and 65535.",
        )

    return value


def validate_ip_address(value):
    """Validate and normalize an IPv4 or IPv6 address."""
    value = value.strip()

    try:
        ipaddress.ip_address(value)
    except ValueError as error:
        raise ValidationError(
            "Invalid Network Settings",
            "Remote IP must be a valid IPv4 or IPv6 address.",
        ) from error

    return value


def validate_network_connection(
    local_ae_title,
    remote_ae_title,
    remote_ip,
    remote_port,
):
    """Validate PACS connection settings."""
    errors = []

    try:
        local_ae_title = validate_ae_title(
            local_ae_title,
            "Local AE Title",
        )
    except ValidationError as error:
        errors.append(error.message)

    try:
        remote_ae_title = validate_ae_title(
            remote_ae_title,
            "Remote AE Title",
        )
    except ValidationError as error:
        errors.append(error.message)

    try:
        remote_ip = validate_ip_address(remote_ip)
    except ValidationError as error:
        errors.append(error.message)

    try:
        remote_port = validate_port(
            remote_port,
            "Remote Port",
        )
    except ValidationError as error:
        errors.append(error.message)

    if errors:
        raise ValidationError(
            "Invalid Network Settings",
            "\n".join(errors),
        )

    return {
        "local_ae_title": local_ae_title,
        "remote_ae_title": remote_ae_title,
        "remote_ip": remote_ip,
        "remote_port": remote_port,
    }


def validate_storage_scp(local_ae_title, local_port):
    """Validate local Storage SCP settings."""
    errors = []

    try:
        local_ae_title = validate_ae_title(
            local_ae_title,
            "Local AE Title",
        )
    except ValidationError as error:
        errors.append(error.message)

    try:
        local_port = validate_port(
            local_port,
            "Storage SCP Port",
        )
    except ValidationError as error:
        errors.append(error.message)

    if errors:
        raise ValidationError(
            "Invalid Storage SCP Settings",
            "\n".join(errors),
        )

    return {
        "local_ae_title": local_ae_title,
        "local_port": local_port,
    }


def validate_study_date_value(value):
    """Validate an optional DICOM Study Date."""
    value = value.strip()

    if not value:
        return ""

    if len(value) != 8 or not value.isdigit():
        raise ValidationError(
            "Invalid Study Date",
            "Study Date must use the YYYYMMDD format.",
        )

    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as error:
        raise ValidationError(
            "Invalid Study Date",
            "Study Date is not a valid calendar date.",
        ) from error

    return value


def validate_dicom_uid(value, name):
    """Validate and normalize a required DICOM UID."""
    value = value.strip()

    if not value:
        raise ValidationError(
            f"Missing {name}",
            f"{name} is required.",
        )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        is_valid = UID(value).is_valid

    if not is_valid:
        raise ValidationError(
            f"Invalid {name}",
            f"{name} is not a valid DICOM UID.",
        )

    return value
