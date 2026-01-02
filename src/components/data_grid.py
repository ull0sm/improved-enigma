"""
Data Grid Component
Virtualized data table with search and filter capabilities
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Callable


def render_data_grid(
    data: List[Dict[str, Any]],
    columns: List[Dict[str, Any]],
    key: str = "data_grid",
    height: int = 400,
    searchable: bool = True,
    show_actions: bool = True,
    on_edit: Optional[Callable] = None,
    on_delete: Optional[Callable] = None
):
    """
    Render a data grid with search and optional actions.
    
    Args:
        data: List of dictionaries containing the data
        columns: List of column configs [{'field': 'name', 'header': 'Name', 'width': 200}]
        key: Unique key for the component
        height: Height of the grid in pixels
        searchable: Whether to show search box
        show_actions: Whether to show edit/delete actions
        on_edit: Callback when edit is clicked
        on_delete: Callback when delete is clicked
    """
    if not data:
        st.info("📋 No data to display")
        return
    
    # Search functionality
    if searchable:
        search_query = st.text_input(
            "🔍 Search",
            placeholder="Search by name...",
            key=f"{key}_search"
        )
        
        if search_query:
            search_lower = search_query.lower()
            data = [
                row for row in data
                if any(
                    search_lower in str(row.get(col['field'], '')).lower()
                    for col in columns
                )
            ]
    
    # Create DataFrame for display
    df_data = []
    for row in data:
        row_data = {}
        for col in columns:
            field = col['field']
            value = row.get(field, '')
            
            # Handle nested fields (e.g., 'dojos.name')
            if '.' in field:
                parts = field.split('.')
                value = row
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, '')
                    else:
                        value = ''
                        break
            
            row_data[col['header']] = value
        
        # Add ID for actions
        row_data['_id'] = row.get('id', '')
        df_data.append(row_data)
    
    df = pd.DataFrame(df_data)
    
    # Display count
    st.markdown(f"<p style='color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem;'>Showing {len(df)} records</p>", unsafe_allow_html=True)
    
    if show_actions and (on_edit or on_delete):
        # Display with action buttons
        for idx, row in df.iterrows():
            with st.container():
                cols = st.columns([*[col.get('width', 1) for col in columns], 1])
                
                for i, col in enumerate(columns):
                    with cols[i]:
                        value = row[col['header']]
                        st.markdown(f"<p style='margin: 0.5rem 0; font-size: 0.9rem;'>{value}</p>", unsafe_allow_html=True)
                
                with cols[-1]:
                    btn_cols = st.columns(2)
                    if on_edit:
                        with btn_cols[0]:
                            if st.button("✏️", key=f"{key}_edit_{row['_id']}", help="Edit"):
                                on_edit(row['_id'])
                    if on_delete:
                        with btn_cols[1]:
                            if st.button("🗑️", key=f"{key}_del_{row['_id']}", help="Delete"):
                                on_delete(row['_id'])
                
                st.markdown("<hr style='margin: 0.5rem 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    else:
        # Display as standard dataframe
        display_cols = [col['header'] for col in columns]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            height=height,
            hide_index=True
        )


def render_athletes_table(
    athletes: List[Dict[str, Any]],
    show_dojo: bool = False,
    show_coach: bool = False,
    editable: bool = True,
    key: str = "athletes_table"
):
    """
    Specialized athletes table with common column configuration.
    """
    columns = [
        {'field': 'full_name', 'header': 'Name', 'width': 2},
        {'field': 'date_of_birth', 'header': 'DOB', 'width': 1},
        {'field': 'gender', 'header': 'Gender', 'width': 1},
        {'field': 'belt_rank', 'header': 'Belt', 'width': 1},
        {'field': 'competition_day', 'header': 'Day', 'width': 1},
    ]
    
    if show_dojo:
        columns.append({'field': 'dojos.name', 'header': 'Dojo', 'width': 1})
    
    if show_coach:
        columns.append({'field': 'coaches.full_name', 'header': 'Coach', 'width': 1})
    
    # Prepare data with formatted values
    formatted_data = []
    for athlete in athletes:
        formatted = athlete.copy()
        
        # Format events as icons
        events = []
        if athlete.get('kata_event'):
            events.append('🥋')
        if athlete.get('kumite_event'):
            events.append('👊')
        formatted['events_display'] = ' '.join(events) or '-'
        
        formatted_data.append(formatted)
    
    # Create DataFrame
    df = pd.DataFrame(formatted_data)
    
    if df.empty:
        st.info("📋 No athletes registered yet")
        return None
    
    # Build display columns
    display_data = []
    for athlete in formatted_data:
        row = {
            'Name': athlete.get('full_name', ''),
            'DOB': str(athlete.get('date_of_birth', ''))[:10],
            'Gender': athlete.get('gender', ''),
            'Belt': athlete.get('belt_rank', ''),
            'Day': athlete.get('competition_day', ''),
            'Events': athlete.get('events_display', '')
        }
        
        if show_dojo:
            dojo = athlete.get('dojos', {})
            row['Dojo'] = dojo.get('name', '') if isinstance(dojo, dict) else ''
        
        if show_coach:
            coach = athlete.get('coaches', {})
            row['Coach'] = coach.get('full_name', '') if isinstance(coach, dict) else ''
        
        display_data.append(row)
    
    display_df = pd.DataFrame(display_data)
    
    # Use Streamlit's dataframe with selection if editable
    if editable:
        event = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key=key
        )
        
        # Return selected row
        if event and event.selection and event.selection.rows:
            selected_idx = event.selection.rows[0]
            return athletes[selected_idx]
    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            key=key
        )
    
    return None
