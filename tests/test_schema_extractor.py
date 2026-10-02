import pytest
from schema_extractor import SchemaExtractor

@pytest.fixture(scope="module")
def extractor():
    return SchemaExtractor()

def test_extract_schema_contains_chinook_tables(extractor):
    """Test that schema extraction correctly identifies core Chinook tables."""
    schema = extractor.extract_schema()
    
    # Convert all extracted table names to lowercase for case-insensitive checking
    tables_lower = [t.lower() for t in schema.keys()]
    
    assert "album" in tables_lower
    assert "artist" in tables_lower
    assert "track" in tables_lower
    assert "invoice" in tables_lower

def test_extract_schema_foreign_keys(extractor):
    """Test that foreign key relationships are correctly mapped."""
    schema = extractor.extract_schema()
    
    # Locate the exact table name as stored in the database ('album' or 'Album')
    album_key = next(k for k in schema.keys() if k.lower() == 'album')
    
    # Map all column names to lowercase to bypass Python's strict case sensitivity
    album_cols = {col["name"].lower(): col for col in schema[album_key]}
    
    # Support both 'artistid' and 'artist_id' depending on the Chinook port
    artist_col_key = "artistid" if "artistid" in album_cols else "artist_id"
    
    fk_target = album_cols[artist_col_key]["foreign_key"]
    
    # Verify a foreign key exists and points to the artist table
    assert fk_target is not None
    assert "artist" in fk_target.lower()

def test_categorical_sample_extraction(extractor):
    """Test that sample values are extracted from text columns."""
    schema = extractor.extract_schema()
    
    genre_key = next(k for k in schema.keys() if k.lower() == 'genre')
    genre_cols = {col["name"].lower(): col for col in schema[genre_key]}
    
    samples = genre_cols["name"]["sample_values"]
    
    # Verify the query successfully pulled a list of string samples, ignoring exact genre names
    assert isinstance(samples, list)
    assert len(samples) > 0
    assert isinstance(samples[0], str)