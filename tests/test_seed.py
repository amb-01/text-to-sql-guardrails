import pytest
import os
from sqlalchemy import create_engine
from seed import check_data_exists

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ecommerce")

def test_chinook_data_detection():
    """
    Verifies that check_data_exists correctly identifies that the database 
    is already populated with the Chinook tables.
    """
    engine = create_engine(DATABASE_URL)
    
    # Run the check function
    has_data = check_data_exists(engine)
    
    # Assert that it returns True, meaning it successfully detected the tables
    assert has_data is True, "Failed to detect existing Chinook data. Are the tables missing?"