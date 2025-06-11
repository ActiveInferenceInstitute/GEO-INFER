# Python Examples for the Location Protocol

This directory contains a series of Python scripts that demonstrate how to interact with the Location Protocol using its reference implementation on the Ethereum Attestation Service (EAS).

## Overview

The scripts cover the following functionalities:
- **Schema Registration**: How to register a new schema for location attestations on EAS.
- **On-Chain Attestation**: How to create a location attestation that is stored on the blockchain.
- **Off-Chain Attestation**: How to create a signed location attestation that can be stored and shared off-chain.
- **Attestation Retrieval**: How to retrieve and decode an existing attestation from the blockchain.

These examples are configured to run on the **Sepolia testnet**.

## Setup

### 1. Install Dependencies

First, install the necessary Python packages.

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

You'll need an Ethereum account with some Sepolia ETH to pay for gas fees when sending transactions. You can get Sepolia ETH from a public faucet.

Create a `.env` file in this directory by copying the example file:

```bash
cp .env.example .env
```

Now, edit the `.env` file and add your details:

```
# Your private key from a wallet like MetaMask.
# IMPORTANT: This is a secret. Do not commit it to version control.
# Make sure this account has some Sepolia ETH.
PRIVATE_KEY="your_ethereum_private_key"

# An RPC endpoint URL for the Sepolia testnet.
# You can get one from services like Infura, Alchemy, or use a public one.
SEPOLIA_RPC_URL="https://sepolia.infura.io/v3/your_infura_project_id"
```

## Running the Scripts

The scripts are numbered in a suggested order of execution.

### 1. Register a Schema

This script registers a new schema for our location attestations.

```bash
python 1_register_schema.py
```
It will output the transaction hash and the UID of the newly registered schema. Copy the schema UID, as you might need it for the next scripts.

### 2. Create an On-Chain Attestation

This script creates a location attestation and submits it to the blockchain.

```bash
python 2_create_onchain_attestation.py
```
It will output the transaction hash and the UID of the new attestation.

### 3. Create an Off-Chain Attestation

This script demonstrates how to create a signed attestation that is not broadcast to the network. This is useful for saving gas and for private attestations.

```bash
python 3_create_offchain_attestation.py
```
It will print the signed attestation data. It also shows how the signature can be verified.

### 4. Retrieve an Attestation

This script fetches an existing on-chain attestation using its UID.

```bash
# Replace with an actual attestation UID from step 2
python 4_retrieve_attestation.py <attestation_uid>
```

## Running Tests

To ensure the utility functions are working correctly, you can run the provided unit tests:

```bash
pytest
``` 