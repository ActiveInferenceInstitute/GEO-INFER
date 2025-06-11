import pytest
from web3 import Web3
from location_protocol_utils import (
    parse_schema_string,
    encode_payload,
    decode_payload,
    get_schema_uid
)

def test_parse_schema_string():
    """Tests the parsing of an EAS schema string."""
    schema_string = "string srs, string locationType, string location, uint8 specVersion"
    types, names = parse_schema_string(schema_string)
    assert types == ["string", "string", "string", "uint8"]
    assert names == ["srs", "locationType", "location", "specVersion"]

    schema_string_complex = "bytes32 mediaData, string mediaType, uint64 eventTimestamp"
    types, names = parse_schema_string(schema_string_complex)
    assert types == ["bytes32", "string", "uint64"]
    assert names == ["mediaData", "mediaType", "eventTimestamp"]

def test_get_schema_uid():
    """Tests the schema UID calculation."""
    schema_string = "string srs, string locationType, string location, uint8 specVersion"
    resolver = "0x0000000000000000000000000000000000000000"
    revocable = True
    
    # This is the known UID for the above schema on EAS.
    expected_uid = "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a"
    
    calculated_uid = get_schema_uid(schema_string, resolver, revocable)
    assert calculated_uid == expected_uid

def test_payload_encoding_decoding():
    """Tests that payload encoding and decoding are symmetric."""
    schema_string = "string srs, string locationType, string location, uint8 specVersion"
    payload = [
        {"name": "srs", "value": "EPSG:4326"},
        {"name": "locationType", "value": "coordinate-decimal+lon-lat"},
        {"name": "location", "value": "-103.771556, 44.967243"},
        {"name": "specVersion", "value": 1}
    ]

    # Encode the payload
    encoded_data_hex = encode_payload(schema_string, payload)
    encoded_data_bytes = Web3.to_bytes(hexstr=encoded_data_hex)

    # Decode the payload
    decoded_payload = decode_payload(schema_string, encoded_data_bytes)

    # Reconstruct the original payload for comparison
    original_payload_dict = {item['name']: item['value'] for item in payload}
    decoded_payload_dict = {item['name']: item['value'] for item in decoded_payload}

    assert original_payload_dict == decoded_payload_dict

def test_payload_encoding_with_different_order():
    """Tests that payload encoding works even if payload order differs from schema."""
    schema_string = "string srs, string locationType, string location, uint8 specVersion"
    
    # Payload in a different order than schema
    payload = [
        {"name": "location", "value": "-103.771556, 44.967243"},
        {"name": "specVersion", "value": 1},
        {"name": "srs", "value": "EPSG:4326"},
        {"name": "locationType", "value": "coordinate-decimal+lon-lat"},
    ]

    # The encoder should order the values correctly based on the schema string.
    encoded_data_hex = encode_payload(schema_string, payload)
    encoded_data_bytes = Web3.to_bytes(hexstr=encoded_data_hex)
    
    decoded_payload = decode_payload(schema_string, encoded_data_bytes)

    original_payload_dict = {item['name']: item['value'] for item in payload}
    decoded_payload_dict = {item['name']: item['value'] for item in decoded_payload}

    assert original_payload_dict == decoded_payload_dict 