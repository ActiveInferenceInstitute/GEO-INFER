import time
from web3 import Web3
from config import PRIVATE_KEY
from eas_contracts import get_w3_instance, get_eas_contract
from location_protocol_utils import encode_payload

# The UID of the schema we registered in the previous step.
# Replace this with the actual schema UID you received.
# You can also calculate it using get_schema_uid from the utils.
SCHEMA_UID = "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a" # Fallback to the one from the docs
SCHEMA_STRING = "string srs, string locationType, string location, uint8 specVersion"

def create_onchain_attestation():
    """
    Creates an on-chain attestation using the Location Protocol schema.
    """
    # 1. Setup
    w3 = get_w3_instance()
    account = w3.eth.account.from_key(PRIVATE_KEY)
    eas = get_eas_contract(w3)

    # 2. Prepare Location Payload
    # This payload corresponds to the example in the Location Protocol documentation.
    location_payload = [
        {"name": "srs", "value": "EPSG:4326", "type": "string"},
        {"name": "locationType", "value": "coordinate-decimal+lon-lat", "type": "string"},
        {"name": "location", "value": "-103.771556, 44.967243", "type": "string"},
        {"name": "specVersion", "value": 1, "type": "uint8"}
    ]
    
    encoded_data = encode_payload(SCHEMA_STRING, location_payload)

    # 3. Prepare Attestation Object
    attestation = {
        "schema": SCHEMA_UID,
        "data": {
            "recipient": "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165", # Example recipient
            "expirationTime": 0,  # No expiration
            "revocable": True,
            "refUID": "0x" + "0" * 64, # No reference
            "data": w3.to_bytes(hexstr=encoded_data),
            "value": 0 # No ETH value attached
        }
    }

    print("Creating on-chain attestation...")
    
    # 4. Build and Send Transaction
    try:
        tx_params = {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
            "value": attestation['data']['value']
        }

        gas_estimate = eas.functions.attest(attestation).estimate_gas(tx_params)
        tx_params['gas'] = gas_estimate

        transaction = eas.functions.attest(attestation).build_transaction(tx_params)

        signed_tx = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"Transaction sent. Hash: {tx_hash.hex()}")

        # 5. Wait for receipt and get new attestation UID
        print("Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # The Attested event contains the new UID
            attested_event = eas.events.Attested().process_receipt(tx_receipt)[0]
            new_uid = attested_event['args']['uid'].hex()
            
            print("\nAttestation created successfully!")
            print(f"  New Attestation UID: 0x{new_uid}")
            print(f"  Etherscan Link: https://sepolia.easscan.org/attestation/view/0x{new_uid}")
        else:
            print("Transaction failed.")
            print(f"  Transaction hash: {tx_receipt.transactionHash.hex()}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_onchain_attestation() 