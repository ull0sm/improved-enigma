"""
Supabase Client Configuration
Handles connection to Supabase with proper error handling
"""

import streamlit as st
from supabase import create_client, Client
from functools import lru_cache


def get_supabase_config():
    """Get Supabase configuration from Streamlit secrets"""
    try:
        return {
            "url": st.secrets["supabase"]["url"],
            "key": st.secrets["supabase"]["key"]
        }
    except KeyError as e:
        st.error(f"Missing Supabase configuration: {e}")
        st.info("Please configure your Supabase credentials in .streamlit/secrets.toml")
        st.stop()


@st.cache_resource
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.
    Uses Streamlit's cache_resource to maintain connection across reruns.
    """
    config = get_supabase_config()
    return create_client(config["url"], config["key"])


def get_authenticated_client(access_token: str) -> Client:
    """
    Get a Supabase client with user's access token for RLS.
    This ensures queries respect Row Level Security policies.
    """
    config = get_supabase_config()
    client = create_client(config["url"], config["key"])
    client.auth.set_session(access_token, "")
    return client
