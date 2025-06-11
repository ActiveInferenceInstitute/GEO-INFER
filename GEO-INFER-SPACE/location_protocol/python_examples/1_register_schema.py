from web3 import Web3
from config import PRIVATE_KEY, SEPOLIA_CHAIN_ID
from eas_contracts import get_w3_instance, get_schema_registry_contract
from location_protocol_utils import get_schema_uid

def register_schema():
    """
    Connects to the Sepolia testnet, registers a new schema for the Location Protocol,
    and prints the transaction hash and resulting schema UID.
    """
    # 1. Setup
    w3 = get_w3_instance()
    account = w3.eth.account.from_key(PRIVATE_KEY)
    schema_registry = get_schema_registry_contract(w3)

    # 2. Define Schema
    # This is the base schema for the Location Protocol.
    schema_string = "string srs, string locationType, string location, uint8 specVersion"
    resolver_address = "0x0000000000000000000000000000000000000000"  # Zero address for no resolver
    revocable = True

    print("Registering schema...")
    print(f"  Schema: \"{schema_string}\"")
    print(f"  Revocable: {revocable}")
    print(f"  Resolver: {resolver_address}")

    # 3. Build and Send Transaction
    try:
        tx_params = {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
        }
        
        # Estimate gas
        gas_estimate = schema_registry.functions.register(
            schema_string, resolver_address, revocable
        ).estimate_gas(tx_params)
        tx_params['gas'] = gas_estimate

        # Build transaction
        transaction = schema_registry.functions.register(
            schema_string, resolver_address, revocable
        ).build_transaction(tx_params)

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print(f"Transaction sent. Hash: {tx_hash.hex()}")

        # 4. Wait for receipt and get Schema UID
        print("Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if tx_receipt.status == 1:
            # Calculate schema UID locally to verify
            schema_uid = get_schema_uid(schema_string, resolver_address, revocable)
            print("\nSchema registered successfully!")
            print(f"  Schema UID: {schema_uid}")
            print(f"  Transaction hash: {tx_receipt.transactionHash.hex()}")
            print(f"  Block number: {tx_receipt.blockNumber}")
            print(f"  Etherscan link: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
        else:
            print("Transaction failed.")
            print(f"  Transaction hash: {tx_receipt.transactionHash.hex()}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    register_schema() 