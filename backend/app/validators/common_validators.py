"""
Common validation utilities used across the application.
"""
import re
from typing import Tuple, Optional
from fastapi import HTTPException, status


def validate_license_plate(license_plate: str) -> str:
    """
    Validate and normalize license plate format.
    
    Args:
        license_plate: License plate to validate
        
    Returns:
        Normalized license plate
        
    Raises:
        HTTPException: If license plate is invalid
    """
    if not license_plate or not license_plate.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License plate cannot be empty"
        )
    
    # Normalize: remove spaces, convert to uppercase
    normalized = license_plate.strip().upper().replace(' ', '').replace('-', '')
    
    # Argentina license plate patterns
    patterns = [
        r'^[A-Z]{3}\d{3}$',      # Old format: ABC123
        r'^[A-Z]{2}\d{3}[A-Z]{2}$',  # New format: AB123CD
        r'^\d{3}[A-Z]{3}$',      # Alternative old format: 123ABC
    ]
    
    for pattern in patterns:
        if re.match(pattern, normalized):
            return normalized
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid license plate format. Expected formats: ABC123, AB123CD, or 123ABC"
    )


def validate_coordinates(longitude: float, latitude: float) -> Tuple[float, float]:
    """
    Validate geographic coordinates.
    
    Args:
        longitude: Longitude coordinate
        latitude: Latitude coordinate
        
    Returns:
        Tuple of validated (longitude, latitude)
        
    Raises:
        HTTPException: If coordinates are invalid
    """
    # Basic range validation
    if not (-180 <= longitude <= 180):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude must be between -180 and 180 degrees"
        )
    
    if not (-90 <= latitude <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude must be between -90 and 90 degrees"
        )
    
    # Argentina bounds validation (approximate)
    argentina_bounds = {
        'min_longitude': -73.5,
        'max_longitude': -53.6,
        'min_latitude': -55.1,
        'max_latitude': -21.8
    }
    
    if not (argentina_bounds['min_longitude'] <= longitude <= argentina_bounds['max_longitude']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Longitude appears to be outside Argentina bounds"
        )
    
    if not (argentina_bounds['min_latitude'] <= latitude <= argentina_bounds['max_latitude']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude appears to be outside Argentina bounds"
        )
    
    return longitude, latitude


def validate_email_format(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Normalized email address
        
    Raises:
        HTTPException: If email format is invalid
    """
    if not email or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be empty"
        )
    
    email = email.strip().lower()
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    return email


def validate_phone_number(phone: str) -> str:
    """
    Validate and normalize phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Normalized phone number
        
    Raises:
        HTTPException: If phone number is invalid
    """
    if not phone or not phone.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number cannot be empty"
        )
    
    # Remove all non-digit characters except +
    normalized = re.sub(r'[^\d+]', '', phone.strip())
    
    # Argentina phone number patterns
    patterns = [
        r'^\+54\d{10}$',     # International format: +54xxxxxxxxxx
        r'^54\d{10}$',       # Without + : 54xxxxxxxxxx
        r'^\d{10}$',         # Local format: xxxxxxxxxx
        r'^\d{8}$',          # Local landline: xxxxxxxx
    ]
    
    for pattern in patterns:
        if re.match(pattern, normalized):
            return normalized
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid phone number format for Argentina"
    )


def validate_tax_id(tax_id: str) -> str:
    """
    Validate Argentina tax ID (CUIT/CUIL).
    
    Args:
        tax_id: Tax ID to validate
        
    Returns:
        Normalized tax ID
        
    Raises:
        HTTPException: If tax ID is invalid
    """
    if not tax_id or not tax_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax ID cannot be empty"
        )
    
    # Remove all non-digit characters
    normalized = re.sub(r'\D', '', tax_id.strip())
    
    # CUIT/CUIL format: 11 digits
    if len(normalized) != 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax ID (CUIT/CUIL) must be 11 digits"
        )
    
    # Basic CUIT/CUIL validation algorithm
    if not _validate_cuit_algorithm(normalized):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CUIT/CUIL format"
        )
    
    # Format as XX-XXXXXXXX-X
    return f"{normalized[:2]}-{normalized[2:10]}-{normalized[10]}"


def _validate_cuit_algorithm(cuit: str) -> bool:
    """
    Validate CUIT using the official algorithm.
    
    Args:
        cuit: 11-digit CUIT string
        
    Returns:
        True if valid, False otherwise
    """
    if len(cuit) != 11:
        return False
    
    # CUIT validation multipliers
    multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    # Calculate check digit
    total = sum(int(cuit[i]) * multipliers[i] for i in range(10))
    remainder = total % 11
    
    if remainder < 2:
        check_digit = remainder
    else:
        check_digit = 11 - remainder
    
    return int(cuit[10]) == check_digit