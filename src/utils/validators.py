"""
Data Validators
Validation functions for athlete data and form inputs
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, date
import re


# Valid options
BELT_RANKS = [
    'White', 'Yellow', 'Orange', 'Green', 'Blue', 'Purple', 'Brown', 
    'Black 1st Dan', 'Black 2nd Dan', 'Black 3rd Dan', 'Black 4th Dan', 'Black 5th Dan'
]

GENDERS = ['Male', 'Female']

COMPETITION_DAYS = ['Day 1', 'Day 2', 'Both']


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    if not email or not email.strip():
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format"
    
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format."""
    if not phone or not phone.strip():
        return True, ""  # Phone is optional
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid number (allows + for country code)
    if not re.match(r'^\+?[0-9]{7,15}$', cleaned):
        return False, "Invalid phone number format"
    
    return True, ""


def validate_athlete_name(name: str) -> Tuple[bool, str]:
    """Validate athlete name."""
    if not name or not name.strip():
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name.strip()) > 100:
        return False, "Name must be less than 100 characters"
    
    return True, ""


def validate_date_of_birth(dob: Any) -> Tuple[bool, str]:
    """Validate date of birth."""
    if not dob:
        return False, "Date of birth is required"
    
    # Convert to date if string
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            return False, "Invalid date format (use YYYY-MM-DD)"
    
    # Check if date is in the past
    today = date.today()
    if dob >= today:
        return False, "Date of birth must be in the past"
    
    # Check reasonable age range (3 to 100 years)
    age = (today - dob).days / 365.25
    if age < 3:
        return False, "Athlete must be at least 3 years old"
    if age > 100:
        return False, "Invalid date of birth"
    
    return True, ""


def validate_weight(weight: Any) -> Tuple[bool, str]:
    """Validate weight."""
    if weight is None or weight == '':
        return True, ""  # Weight is optional
    
    try:
        weight = float(weight)
    except (ValueError, TypeError):
        return False, "Weight must be a number"
    
    if weight < 10 or weight > 200:
        return False, "Weight must be between 10 and 200 kg"
    
    return True, ""


def validate_gender(gender: str) -> Tuple[bool, str]:
    """Validate gender selection."""
    if not gender:
        return False, "Gender is required"
    
    if gender not in GENDERS:
        return False, f"Gender must be one of: {', '.join(GENDERS)}"
    
    return True, ""


def validate_belt_rank(belt: str) -> Tuple[bool, str]:
    """Validate belt rank selection."""
    if not belt:
        return False, "Belt rank is required"
    
    if belt not in BELT_RANKS:
        return False, f"Invalid belt rank"
    
    return True, ""


def validate_competition_day(day: str) -> Tuple[bool, str]:
    """Validate competition day selection."""
    if not day:
        return False, "Competition day is required"
    
    if day not in COMPETITION_DAYS:
        return False, f"Competition day must be one of: {', '.join(COMPETITION_DAYS)}"
    
    return True, ""


def validate_events(kata: bool, kumite: bool) -> Tuple[bool, str]:
    """Validate that at least one event is selected."""
    if not kata and not kumite:
        return False, "At least one event (Kata or Kumite) must be selected"
    
    return True, ""


def validate_athlete_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete athlete data.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    
    # Validate each field
    validations = [
        validate_athlete_name(data.get('full_name', '')),
        validate_date_of_birth(data.get('date_of_birth')),
        validate_gender(data.get('gender', '')),
        validate_belt_rank(data.get('belt_rank', '')),
        validate_weight(data.get('weight_kg')),
        validate_competition_day(data.get('competition_day', '')),
        validate_events(data.get('kata_event', False), data.get('kumite_event', False))
    ]
    
    for is_valid, error in validations:
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors


def validate_excel_row(row: Dict[str, Any], row_number: int) -> Tuple[bool, List[str]]:
    """
    Validate a row from Excel import.
    Returns (is_valid, list_of_errors_with_row_number).
    """
    is_valid, errors = validate_athlete_data(row)
    
    # Add row number to errors
    prefixed_errors = [f"Row {row_number}: {error}" for error in errors]
    
    return is_valid, prefixed_errors


def normalize_athlete_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and clean athlete data before insertion.
    """
    normalized = {}
    
    # Clean string fields
    if 'full_name' in data:
        normalized['full_name'] = data['full_name'].strip().title()
    
    # Normalize date
    if 'date_of_birth' in data:
        dob = data['date_of_birth']
        if isinstance(dob, datetime):
            normalized['date_of_birth'] = dob.strftime('%Y-%m-%d')
        elif isinstance(dob, date):
            normalized['date_of_birth'] = dob.strftime('%Y-%m-%d')
        else:
            normalized['date_of_birth'] = str(dob)
    
    # Copy other fields
    for field in ['gender', 'belt_rank', 'competition_day', 'kata_event', 'kumite_event']:
        if field in data:
            normalized[field] = data[field]
    
    # Handle weight
    if 'weight_kg' in data and data['weight_kg']:
        try:
            normalized['weight_kg'] = float(data['weight_kg'])
        except:
            normalized['weight_kg'] = None
    
    return normalized
