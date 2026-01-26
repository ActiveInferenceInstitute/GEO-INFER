# Agent
: api ## Scope
 This directory contains api components for the module. It provides 0 classes and 11 functions. ## Classes
 and Functions ### init_security_ap
i
 `init_security_api(app: Flask, secret_key: str, enable_anonymization: bool, enable_compliance: bool) -> None` Initialize the security API with necessary components. ### token_require
d
 `token_required(f)` Decorator to require a valid JWT token for API access. ### get_toke
n
 `get_token()` Generate a JWT token for a user. ### get_role
s
 `get_roles()` Get all roles assigned to the authenticated user. ### anonymize_dat
a
 `anonymize_data()` Anonymize geospatial data. ### check_location_acces
s
 `check_location_access()` Check if the user has access to a specific location. ### check_complianc
e
 `check_compliance()` Check data compliance with regulations. ### filter_dat
a
 `filter_data()` Filter geospatial data based on user permissions. ### unauthorize
d
 `unauthorized(error)` ### forbidde
n
 `forbidden(error)` ### decorate
d
 `decorated(*args, **kwargs)` ## Capabilities
 - **11 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SEC/src/geo_infer_sec/api` - **Type**: Directory Node 