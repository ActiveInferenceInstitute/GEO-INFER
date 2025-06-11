from web3 import Web3
from config import SEPOLIA_RPC_URL, EAS_CONTRACT_ADDRESS, SCHEMA_REGISTRY_ADDRESS

# ABIs are fetched from Sepolia Etherscan
EAS_ABI = [
    {"inputs": [{"internalType": "address", "name": "schemaRegistry", "type": "address"}], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "AccessDenied", "type": "error"},
    {"inputs": [], "name": "AlreadyRevoked", "type": "error"},
    {"inputs": [], "name": "AlreadyTimestamped", "type": "error"},
    {"inputs": [], "name": "DeadlineExpired", "type": "error"},
    {"inputs": [], "name": "InsufficientValue", "type": "error"},
    {"inputs": [], "name": "InvalidAttestation", "type": "error"},
    {"inputs": [], "name": "InvalidAttestations", "type": "error"},
    {"inputs": [], "name": "InvalidDelegateSignature", "type": "error"},
    {"inputs": [], "name": "InvalidLength", "type": "error"},
    {"inputs": [], "name": "InvalidRevocation", "type": "error"},
    {"inputs": [], "name": "InvalidRevocations", "type": "error"},
    {"inputs": [], "name": "InvalidSignature", "type": "error"},
    {"inputs": [], "name": "InvalidTimestamp", "type": "error"},
    {"inputs": [], "name": "NotDelegated", "type": "error"},
    {"inputs": [], "name": "NotFound", "type": "error"},
    {"inputs": [], "name": "NotRevokable", "type": "error"},
    {"inputs": [], "name": "WrongSchema", "type": "error"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "attester", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "Attested", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "revoker", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "Revoked", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "revoker", "type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"}, {"indexed": True, "internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"indexed": True, "internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "RevokedOffchain", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "bytes32", "name": "data", "type": "bytes32"}, {"indexed": True, "internalType": "uint64", "name": "timestamp", "type": "uint64"}], "name": "Timestamped", "type": "event"},
    {"inputs": [], "name": "ATTEST_TYPEHASH", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "DOMAIN_SEPARATOR", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "EIP712_VERSION", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "REVOKE_TYPEHASH", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint64", "name": "expirationTime", "type": "uint64"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "bytes32", "name": "refUID", "type": "bytes32"}, {"internalType": "bytes", "name": "data", "type": "bytes"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct AttestationRequestData", "name": "data", "type": "tuple"}], "internalType": "struct AttestationRequest", "name": "request", "type": "tuple"}], "name": "attest", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint64", "name": "expirationTime", "type": "uint64"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "bytes32", "name": "refUID", "type": "bytes32"}, {"internalType": "bytes", "name": "data", "type": "bytes"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct AttestationRequestData", "name": "data", "type": "tuple"}, {"components": [{"internalType": "uint8", "name": "v", "type": "uint8"}, {"internalType": "bytes32", "name": "r", "type": "bytes32"}, {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "internalType": "struct Signature", "name": "signature", "type": "tuple"}], "internalType": "struct DelegatedAttestationRequest", "name": "delegatedRequest", "type": "tuple"}], "name": "attestByDelegation", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "getAttestation", "outputs": [{"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"internalType": "uint64", "name": "time", "type": "uint64"}, {"internalType": "uint64", "name": "expirationTime", "type": "uint64"}, {"internalType": "uint64", "name": "revocationTime", "type": "uint64"}, {"internalType": "bytes32", "name": "refUID", "type": "bytes32"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "address", "name": "attester", "type": "address"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "bytes", "name": "data", "type": "bytes"}], "internalType": "struct Attestation", "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "attester", "type": "address"}], "name": "getAttesterNonce", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getChainId", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "address", "name": "revoker", "type": "address"}], "name": "getRevokerNonce", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "getSchemaRegistry", "outputs": [{"internalType": "contract ISchemaRegistry", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "data", "type": "bytes32"}], "name": "getTimestamp", "outputs": [{"internalType": "uint64", "name": "", "type": "uint64"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "isAttestationValid", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint64", "name": "expirationTime", "type": "uint64"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "bytes32", "name": "refUID", "type": "bytes32"}, {"internalType": "bytes", "name": "data", "type": "bytes"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct AttestationRequestData[]", "name": "data", "type": "tuple[]"}], "internalType": "struct MultiAttestationRequest[]", "name": "requests", "type": "tuple[]"}], "name": "multiAttest", "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint64", "name": "expirationTime", "type": "uint64"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "bytes32", "name": "refUID", "type": "bytes32"}, {"internalType": "bytes", "name": "data", "type": "bytes"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct AttestationRequestData[]", "name": "data", "type": "tuple[]"}, {"components": [{"internalType": "uint8", "name": "v", "type": "uint8"}, {"internalType": "bytes32", "name": "r", "type": "bytes32"}, {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "internalType": "struct Signature[]", "name": "signatures", "type": "tuple[]"}], "internalType": "struct MultiDelegatedAttestationRequest[]", "name": "delegatedRequests", "type": "tuple[]"}], "name": "multiAttestByDelegation", "outputs": [{"internalType": "bytes32[]", "name": "", "type": "bytes32[]"}], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct RevocationRequestData[]", "name": "data", "type": "tuple[]"}], "internalType": "struct MultiRevocationRequest[]", "name": "requests", "type": "tuple[]"}], "name": "multiRevoke", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct RevocationRequestData[]", "name": "data", "type": "tuple[]"}, {"components": [{"internalType": "uint8", "name": "v", "type": "uint8"}, {"internalType": "bytes32", "name": "r", "type": "bytes32"}, {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "internalType": "struct Signature[]", "name": "signatures", "type": "tuple[]"}], "internalType": "struct MultiDelegatedRevocationRequest[]", "name": "delegatedRequests", "type": "tuple[]"}], "name": "multiRevokeByDelegation", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "data", "type": "bytes32"}, {"internalType": "uint64", "name": "deadline", "type": "uint64"}], "name": "revokeOffchain", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct RevocationRequestData", "name": "data", "type": "tuple"}], "internalType": "struct RevocationRequest", "name": "request", "type": "tuple"}], "name": "revoke", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"components": [{"internalType": "bytes32", "name": "schema", "type": "bytes32"}, {"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "uint256", "name": "value", "type": "uint256"}], "internalType": "struct RevocationRequestData", "name": "data", "type": "tuple"}, {"components": [{"internalType": "uint8", "name": "v", "type": "uint8"}, {"internalType": "bytes32", "name": "r", "type": "bytes32"}, {"internalType": "bytes32", "name": "s", "type": "bytes32"}], "internalType": "struct Signature", "name": "signature", "type": "tuple"}], "internalType": "struct DelegatedRevocationRequest", "name": "delegatedRequest", "type": "tuple"}], "name": "revokeByDelegation", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "data", "type": "bytes32"}], "name": "timestamp", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

SCHEMA_REGISTRY_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "AccessDenied", "type": "error"},
    {"inputs": [], "name": "AlreadyExists", "type": "error"},
    {"inputs": [], "name": "InvalidLength", "type": "error"},
    {"inputs": [], "name": "NotFound", "type": "error"},
    {"anonymous": False, "inputs": [{"indexed": False, "internalType": "address", "name": "previousAdmin", "type": "address"}, {"indexed": False, "internalType": "address", "name": "newAdmin", "type": "address"}], "name": "AdminChanged", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "beacon", "type": "address"}], "name": "BeaconUpgraded", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "caller", "type": "address"}, {"indexed": True, "internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"indexed": False, "internalType": "string", "name": "schema", "type": "string"}], "name": "Registered", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "implementation", "type": "address"}], "name": "Upgraded", "type": "event"},
    {"inputs": [], "name": "VERSION", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}], "name": "getSchema", "outputs": [{"components": [{"internalType": "bytes32", "name": "uid", "type": "bytes32"}, {"internalType": "address", "name": "resolver", "type": "address"}, {"internalType": "bool", "name": "revocable", "type": "bool"}, {"internalType": "string", "name": "schema", "type": "string"}], "internalType": "struct SchemaRecord", "name": "", "type": "tuple"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "schema", "type": "string"}, {"internalType": "address", "name": "resolver", "type": "address"}, {"internalType": "bool", "name": "revocable", "type": "bool"}], "name": "register", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "nonpayable", "type": "function"}
]

def get_eas_contract(w3):
    """Returns an instance of the EAS contract."""
    return w3.eth.contract(address=EAS_CONTRACT_ADDRESS, abi=EAS_ABI)

def get_schema_registry_contract(w3):
    """Returns an instance of the Schema Registry contract."""
    return w3.eth.contract(address=SCHEMA_REGISTRY_ADDRESS, abi=SCHEMA_REGISTRY_ABI)

def get_w3_instance():
    """Returns a web3 instance connected to the Sepolia testnet."""
    w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("Unable to connect to Sepolia RPC endpoint.")
    return w3 