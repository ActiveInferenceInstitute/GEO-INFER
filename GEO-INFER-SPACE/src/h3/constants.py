#!/usr/bin/env python3
"""
H3 Constants Module

Defines constants used throughout the H3 geospatial operations.
"""

import h3 as h3_lib

# H3 Version
H3_VERSION = "4.3.0"

# H3 Resolution Limits
MAX_H3_RES = 15
MIN_H3_RES = 0

# Available H3 Resolutions
H3_RESOLUTIONS = list(range(MIN_H3_RES, MAX_H3_RES + 1))

# Coordinate Limits
LAT_MIN = -90.0
LAT_MAX = 90.0
LNG_MIN = -180.0
LNG_MAX = 180.0

# Earth Constants
WGS84_EARTH_RADIUS_KM = 6371.0

# Error Messages
ERROR_MESSAGES = {
    'INVALID_CELL': 'Invalid H3 cell index',
    'INVALID_RESOLUTION': 'Invalid H3 resolution',
    'INVALID_COORDINATES': 'Invalid coordinates',
    'INVALID_POLYGON': 'Invalid polygon format'
}

# H3 Area Constants (km²) for different resolutions
H3_AREA_KM2 = {
    0: 4250546.8477000,
    1: 607220.9782429,
    2: 86745.8540347,
    3: 12392.2648621,
    4: 1770.3235517,
    5: 252.9033645,
    6: 36.1290521,
    7: 5.1612932,
    8: 0.7373276,
    9: 0.1053325,
    10: 0.0150475,
    11: 0.0021496,
    12: 0.0003071,
    13: 0.0000439,
    14: 0.0000063,
    15: 0.0000009
}

# H3 Edge Length Constants (km) for different resolutions
H3_EDGE_LENGTH_KM = {
    0: 1107.712591,
    1: 418.6760055,
    2: 158.2446558,
    3: 59.81085794,
    4: 22.6063794,
    5: 8.544408276,
    6: 3.229482772,
    7: 1.220629759,
    8: 0.461354684,
    9: 0.174375668,
    10: 0.065907807,
    11: 0.024910561,
    12: 0.009415526,
    13: 0.003559893,
    14: 0.001348575,
    15: 0.000509713
} 