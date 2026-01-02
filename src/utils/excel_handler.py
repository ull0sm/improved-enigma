"""
Excel Handler
Import and export Excel files for bulk athlete operations
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from io import BytesIO
from datetime import datetime
from src.utils.validators import (
    validate_excel_row, normalize_athlete_data,
    BELT_RANKS, GENDERS, COMPETITION_DAYS
)


# Expected column mappings (Excel column name -> internal field name)
COLUMN_MAPPINGS = {
    'name': 'full_name',
    'full name': 'full_name',
    'athlete name': 'full_name',
    'full_name': 'full_name',
    
    'dob': 'date_of_birth',
    'date of birth': 'date_of_birth',
    'birthdate': 'date_of_birth',
    'birth date': 'date_of_birth',
    'date_of_birth': 'date_of_birth',
    
    'gender': 'gender',
    'sex': 'gender',
    
    'belt': 'belt_rank',
    'belt rank': 'belt_rank',
    'belt_rank': 'belt_rank',
    'rank': 'belt_rank',
    
    'weight': 'weight_kg',
    'weight kg': 'weight_kg',
    'weight_kg': 'weight_kg',
    'weight (kg)': 'weight_kg',
    
    'day': 'competition_day',
    'competition day': 'competition_day',
    'competition_day': 'competition_day',
    'comp day': 'competition_day',
    
    'kata': 'kata_event',
    'kata event': 'kata_event',
    'kata_event': 'kata_event',
    
    'kumite': 'kumite_event',
    'kumite event': 'kumite_event',
    'kumite_event': 'kumite_event'
}


def parse_excel_file(uploaded_file) -> Tuple[bool, List[Dict[str, Any]], List[str]]:
    """
    Parse an uploaded Excel file and validate its contents.
    
    Returns:
        Tuple of (success, list_of_athletes, list_of_errors)
    """
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        if df.empty:
            return False, [], ["The Excel file is empty"]
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Map columns to internal field names
        column_map = {}
        for col in df.columns:
            if col in COLUMN_MAPPINGS:
                column_map[col] = COLUMN_MAPPINGS[col]
        
        if not column_map:
            return False, [], [
                "Could not find required columns. Expected columns: Name, Date of Birth, Gender, Belt Rank, Competition Day"
            ]
        
        # Rename columns
        df = df.rename(columns=column_map)
        
        # Check required columns
        required = ['full_name', 'date_of_birth', 'gender', 'belt_rank', 'competition_day']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return False, [], [f"Missing required columns: {', '.join(missing)}"]
        
        # Process each row
        athletes = []
        all_errors = []
        
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel rows are 1-indexed, plus header row
            
            # Build athlete data
            athlete_data = {
                'full_name': str(row.get('full_name', '')).strip() if pd.notna(row.get('full_name')) else '',
                'date_of_birth': parse_date(row.get('date_of_birth')),
                'gender': normalize_gender(row.get('gender', '')),
                'belt_rank': normalize_belt(row.get('belt_rank', '')),
                'weight_kg': parse_weight(row.get('weight_kg')),
                'competition_day': normalize_day(row.get('competition_day', '')),
                'kata_event': parse_boolean(row.get('kata_event', True)),
                'kumite_event': parse_boolean(row.get('kumite_event', True))
            }
            
            # Validate
            is_valid, errors = validate_excel_row(athlete_data, row_num)
            
            if is_valid:
                athletes.append(normalize_athlete_data(athlete_data))
            else:
                all_errors.extend(errors)
        
        if not athletes and all_errors:
            return False, [], all_errors
        
        return True, athletes, all_errors
        
    except Exception as e:
        return False, [], [f"Error reading Excel file: {str(e)}"]


def parse_date(value) -> Optional[str]:
    """Parse date from various formats."""
    if pd.isna(value):
        return None
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    
    if isinstance(value, str):
        # Try common formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']
        for fmt in formats:
            try:
                return datetime.strptime(value.strip(), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
    
    return str(value)


def parse_weight(value) -> Optional[float]:
    """Parse weight value."""
    if pd.isna(value):
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_boolean(value) -> bool:
    """Parse boolean value from various formats."""
    if pd.isna(value):
        return True  # Default to True for events
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        return value.lower().strip() in ['yes', 'true', '1', 'y', 'x', '✓', '✔']
    
    return False


def normalize_gender(value) -> str:
    """Normalize gender value."""
    if pd.isna(value):
        return ''
    
    value = str(value).strip().lower()
    
    if value in ['male', 'm', 'boy', 'man']:
        return 'Male'
    elif value in ['female', 'f', 'girl', 'woman']:
        return 'Female'
    
    return str(value).title()


def normalize_belt(value) -> str:
    """Normalize belt rank value."""
    if pd.isna(value):
        return ''
    
    value = str(value).strip().lower()
    
    # Direct match
    for belt in BELT_RANKS:
        if belt.lower() == value:
            return belt
    
    # Partial match
    for belt in BELT_RANKS:
        if value in belt.lower() or belt.lower() in value:
            return belt
    
    return str(value).title()


def normalize_day(value) -> str:
    """Normalize competition day value."""
    if pd.isna(value):
        return ''
    
    value = str(value).strip().lower()
    
    if '1' in value:
        return 'Day 1'
    elif '2' in value:
        return 'Day 2'
    elif 'both' in value or 'all' in value:
        return 'Both'
    
    return str(value).title()


def generate_excel_template() -> bytes:
    """
    Generate a blank Excel template for athlete registration.
    """
    # Create sample data
    data = {
        'Name': ['John Doe', 'Jane Smith'],
        'Date of Birth': ['2010-05-15', '2012-08-22'],
        'Gender': ['Male', 'Female'],
        'Belt Rank': ['Blue', 'Green'],
        'Weight (kg)': [35.5, 28.0],
        'Competition Day': ['Day 1', 'Day 2'],
        'Kata': ['Yes', 'Yes'],
        'Kumite': ['Yes', 'No']
    }
    
    df = pd.DataFrame(data)
    
    # Write to bytes buffer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Athletes')
        
        # Get workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Athletes']
        
        # Adjust column widths
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    return output.getvalue()


def export_athletes_to_excel(athletes: List[Dict[str, Any]], filename: str = "athletes") -> bytes:
    """
    Export a list of athletes to Excel format.
    """
    if not athletes:
        # Return empty template
        return generate_excel_template()
    
    # Prepare data for export
    export_data = []
    for athlete in athletes:
        export_data.append({
            'Name': athlete.get('full_name', ''),
            'Date of Birth': athlete.get('date_of_birth', ''),
            'Gender': athlete.get('gender', ''),
            'Belt Rank': athlete.get('belt_rank', ''),
            'Weight (kg)': athlete.get('weight_kg', ''),
            'Competition Day': athlete.get('competition_day', ''),
            'Kata': 'Yes' if athlete.get('kata_event') else 'No',
            'Kumite': 'Yes' if athlete.get('kumite_event') else 'No',
            'Dojo': athlete.get('dojos', {}).get('name', '') if isinstance(athlete.get('dojos'), dict) else '',
            'Registered By': athlete.get('coaches', {}).get('full_name', '') if isinstance(athlete.get('coaches'), dict) else '',
            'Registration Date': athlete.get('created_at', '')[:10] if athlete.get('created_at') else ''
        })
    
    df = pd.DataFrame(export_data)
    
    # Write to bytes buffer
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Athletes')
        
        # Adjust column widths
        workbook = writer.book
        worksheet = writer.sheets['Athletes']
        
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            ) + 2
            col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
            worksheet.column_dimensions[col_letter].width = min(max_length, 30)
    
    return output.getvalue()
