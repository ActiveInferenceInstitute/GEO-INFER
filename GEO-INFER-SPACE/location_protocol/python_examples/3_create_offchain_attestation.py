import time
from web3 import Web3
from eth_account.messages import encode_typed_data
from config import PRIVATE_KEY, SEPOLIA_CHAIN_ID, EAS_CONTRACT_ADDRESS
from eas_contracts import get_w3_instance
from location_protocol_utils import encode_payload

# The UID of the schema we registered.
SCHEMA_UID = "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a" # Fallback to the one from the docs
SCHEMA_STRING = "string srs, string locationType, string location, uint8 specVersion"

def create_offchain_attestation():
    """
    Creates and signs an off-chain attestation according to EIP-712.
    """
    # 1. Setup
    w3 = get_w3_instance()
    account = w3.eth.account.from_key(PRIVATE_KEY)

    # 2. Prepare Location Payload
    location_payload = [
        {"name": "srs", "value": "EPSG:4326", "type": "string"},
        {"name": "locationType", "value": "coordinate-decimal+lon-lat", "type": "string"},
        {"name": "location", "value": "-103.771556, 44.967243", "type": "string"},
        {"name": "specVersion", "value": 1, "type": "uint8"}
    ]
    encoded_data = w3.to_bytes(hexstr=encode_payload(SCHEMA_STRING, location_payload))

    # 3. Define EIP-712 Typed Data
    # Based on the EAS EIP712Proxy contract
    domain = {
        "name": "EAS Attestation",
        "version": "1",
        "chainId": SEPOLIA_CHAIN_ID,
        "verifyingContract": EAS_CONTRACT_ADDRESS,
    }

    primary_type = "Attest"
    
    types = {
        "Attest": [
            {"name": "schema", "type": "bytes32"},
            {"name": "recipient", "type": "address"},
            {"name": "expirationTime", "type": "uint64"},
            {"name": "revocable", "type": "bool"},
            {"name": "refUID", "type": "bytes32"},
            {"name": "data", "type": "bytes"},
            {"name": "time", "type": "uint64"},
        ]
    }

    # 4. Prepare message
    message = {
        "schema": w3.to_bytes(hexstr=SCHEMA_UID),
        "recipient": "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165",
        "expirationTime": 0,
        "revocable": True,
        "refUID": w3.to_bytes(hexstr="0x0000000000000000000000000000000000000000000000000000000000000000"),
        "data": encoded_data,
        "time": int(time.time()),
    }

    # 5. Sign the Typed Data
    try:
        signable_message = encode_typed_data(full_message={'domain': domain, 'types': types, 'primaryType': primary_type, 'message': message})
        signed_message = w3.eth.account.sign_message(signable_message, private_key=PRIVATE_KEY)
        
        signature = {
            "r": signed_message.r,
            "s": signed_message.s,
            "v": signed_message.v,
        }

        print("Off-chain attestation created and signed successfully!")
        print("\n Attestation Message:")
        print(message)
        print("\n Signature (r, s, v):")
        print(signature)

        # 6. Verify the signature (optional, for demonstration)
        recovered_address = w3.eth.account.recover_message(signable_message, signature=signed_message.signature)
        print(f"\nSigner address:    {account.address}")
        print(f"Recovered address: {recovered_address}")

        if recovered_address.lower() == account.address.lower():
            print("\nSignature verified successfully!")
        else:
            print("\nSignature verification failed.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_offchain_attestation() 