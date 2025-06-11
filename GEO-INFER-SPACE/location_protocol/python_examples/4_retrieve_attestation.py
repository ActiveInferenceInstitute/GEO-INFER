import sys
from eas_contracts import get_w3_instance, get_eas_contract
from location_protocol_utils import decode_payload

# The schema string for the location protocol.
SCHEMA_STRING = "string srs, string locationType, string location, uint8 specVersion"

def retrieve_attestation(attestation_uid: str):
    """
    Retrieves an on-chain attestation by its UID and decodes its payload.
    """
    if not attestation_uid or len(attestation_uid) != 66:
        print("Error: Please provide a valid 32-byte attestation UID as a hex string (e.g., 0x...).")
        sys.exit(1)

    # 1. Setup
    w3 = get_w3_instance()
    eas = get_eas_contract(w3)

    print(f"Retrieving attestation with UID: {attestation_uid}")

    # 2. Call the contract
    try:
        attestation = eas.functions.getAttestation(attestation_uid).call()
        
        # The attestation struct returned by the contract:
        # (uid, schema, time, expirationTime, revocationTime, refUID, recipient, attester, revocable, data)
        
        uid, schema, time, expirationTime, revocationTime, refUID, recipient, attester, revocable, data = attestation

        print("\nAttestation found!")
        print("-" * 20)
        print(f"  UID: {uid.hex()}")
        print(f"  Schema: {schema.hex()}")
        print(f"  Attester: {attester}")
        print(f"  Recipient: {recipient}")
        print(f"  Created at: {time}")
        print(f"  Expires at: {expirationTime}")
        print(f"  Revocable: {revocable}")
        print(f"  Data (raw): {data.hex()}")
        print("-" * 20)

        # 3. Decode the payload
        print("\nDecoding Location Protocol payload...")
        try:
            decoded_data = decode_payload(SCHEMA_STRING, data)
            print("Payload decoded successfully:")
            for item in decoded_data:
                print(f"  - {item['name']} ({item['type']}): {item['value']}")
        except Exception as e:
            print(f"Failed to decode payload: {e}")
            print("Please ensure the attestation was created with the correct schema:")
            print(f"  Schema: {SCHEMA_STRING}")

    except Exception as e:
        # This might be a "BadFunctionCallOutput" error if the UID is not found
        print(f"\nAn error occurred: {e}")
        print("This could mean the attestation UID was not found on the Sepolia testnet.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 4_retrieve_attestation.py <attestation_uid>")
        # Example UID from the documentation, may not exist on Sepolia.
        # It's better to use one created from script #2.
        example_uid = "0x628f06c011351ef39b419718f29f20f0bc62ff3342d1e9c284531bf12bd20f31"
        print(f"Running with example UID: {example_uid}")
        retrieve_attestation(example_uid)
    else:
        retrieve_attestation(sys.argv[1]) 