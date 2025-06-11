import os
from dotenv import load_dotenv

load_dotenv()

# Your private key from a wallet like MetaMask.
# IMPORTANT: This is a secret. Do not commit it to version control.
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY not found in .env file. Please set it.")

# An RPC endpoint URL for the Sepolia testnet.
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL")
if not SEPOLIA_RPC_URL:
    raise ValueError("SEPOLIA_RPC_URL not found in .env file. Please set it.")

# EAS Contract Addresses on Sepolia
EAS_CONTRACT_ADDRESS = "0xC2679fBD37d740A1671aE758aA9374042a45A584"
SCHEMA_REGISTRY_ADDRESS = "0x0a7E2Ff54e76B8E6659aedc9103FB21c038050D0"

# Sepolia Chain ID
SEPOLIA_CHAIN_ID = 11155111 