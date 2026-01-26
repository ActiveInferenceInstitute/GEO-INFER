# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 2 classes and 3 functions. ## Classes
 and Functions ### SecurityConfi
g
 Configuration for security utilities. ### SecurityUtil
s
 Utility class for security and privacy operations. **Methods**: - `generate_secure_key(length: Optional[int]) -> bytes`: Generate a cryptographically secure random key. - `hash_password(password: str, salt: Optional[bytes]) -> Tuple[bytes, bytes]`: Hash a password using PBKDF2. - `verify_password(password: str, stored_hash: bytes, salt: bytes) -> bool`: Verify a password against stored hash. - `encrypt_data(data: Union[str, bytes], key: bytes) -> Tuple[bytes, bytes]`: Encrypt data using AES-256-CBC. - `decrypt_data(encrypted_data: bytes, key: bytes, iv: bytes) -> bytes`: Decrypt data using AES-256-CBC. - `anonymize_spatial_data(data: pd.DataFrame, lat_col: str, lon_col: str, precision: int) -> pd.DataFrame`: Anonymize spatial data by reducing precision. - `apply_k_anonymity(data: pd.DataFrame, sensitive_cols: List[str], quasi_identifiers: List[str]) -> pd.DataFrame`: Apply k-anonymity to protect sensitive data. - `add_noise_to_numerical(data: pd.DataFrame, columns: List[str], noise_level: float) -> pd.DataFrame`: Add noise to numerical columns for privacy protection. - `check_access_control(user_id: str, resource: str, action: str) -> bool`: Check if user has permission to perform action on resource. - `record_failed_attempt(user_id: str)`: Record a failed authentication attempt. - `get_audit_log(start_time: Optional[datetime], end_time: Optional[datetime], user_id: Optional[str]) -> List[Dict[str, Any]]`: Get audit log entries with optional filtering. - `cleanup_audit_log()`: Remove old audit log entries based on retention policy. - `generate_secure_token(user_id: str, expiration_hours: int) -> str`: Generate a secure token for user authentication. - `validate_token(token: str) -> Optional[str]`: Validate a secure token and return user ID if valid. - `sanitize_input(input_data: str) -> str`: Sanitize user input to prevent injection attacks. - `validate_file_upload(file_path: str, allowed_extensions: List[str], max_size_mb: int) -> Tuple[bool, str]`: Validate file upload for security. ### create_security_util
s
 `create_security_utils(config: Optional[SecurityConfig]) -> SecurityUtils` Create a SecurityUtils instance. ### hash_password_simpl
e
 `hash_password_simple(password: str) -> str` Simple password hashing function. ### verify_password_simpl
e
 `verify_password_simple(password: str, stored_hash: str) -> bool` Simple password verification function. ## Capabilities
 - **2 classes** for core functionality - **3 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SEC/src/geo_infer_sec/utils` - **Type**: Directory Node 