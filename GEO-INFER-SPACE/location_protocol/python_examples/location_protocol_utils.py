import re
from eth_abi import encode as encode_abi, decode as decode_abi
from web3 import Web3


def parse_schema_string(schema_string: str) -> tuple[list[str], list[str]]:
    """
    Parses an EAS schema string into a list of types and a list of names.
    e.g., "string srs, string locationType" -> (['string', 'string'], ['srs', 'locationType'])
    """
    parts = [part.strip() for part in schema_string.split(',')]
    types = []
    names = []
    for part in parts:
        match = re.match(r'(\S+)\s+(\S+)', part)
        if match:
            type, name = match.groups()
            types.append(type)
            names.append(name)
    return types, names


def encode_payload(schema_string: str, payload: list[dict]) -> str:
    """
    Encodes a location payload according to the given schema string.

    :param schema_string: The EAS schema string.
    :param payload: A list of dictionaries, where each dict has "name", "value".
    :return: The ABI-encoded payload as a hex string.
    """
    schema_types, schema_names = parse_schema_string(schema_string)

    # Create a dictionary for quick lookup of values by name
    payload_dict = {item['name']: item['value'] for item in payload}

    # Order the values according to the schema definition
    ordered_values = [payload_dict[name] for name in schema_names]

    encoded_data = encode_abi(schema_types, ordered_values)

    return '0x' + encoded_data.hex()


def decode_payload(schema_string: str, encoded_payload: bytes) -> list[dict]:
    """
    Decodes an ABI-encoded payload according to the given schema string.

    :param schema_string: The EAS schema string.
    :param encoded_payload: The ABI-encoded payload as bytes.
    :return: A list of dictionaries representing the decoded payload.
    """
    schema_types, schema_names = parse_schema_string(schema_string)
    decoded_values = decode_abi(schema_types, encoded_payload)

    return [
        {"name": name, "value": value, "type": type}
        for name, value, type in zip(schema_names, decoded_values, schema_types)
    ]


def get_schema_uid(schema_string: str, resolver_address: str, revocable: bool) -> str:
    """
    Calculates the schema UID.
    The UID is `keccak256(abi.encodePacked(schema, resolver, revocable))`.
    """
    return Web3.solidity_keccak(
        ['string', 'address', 'bool'],
        [schema_string, resolver_address, revocable]
    ).hex() 