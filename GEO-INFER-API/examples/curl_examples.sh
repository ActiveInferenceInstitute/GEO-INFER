#!/bin/bash
# Example CURL commands for interacting with GEO-INFER-API GeoJSON polygon endpoints

# Set the API base URL (change this to match your deployment)
API_BASE_URL="http://localhost:8000/api/v1"

# Set text colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Feature ID for our examples
FEATURE_ID="sf-triangle-curl-demo"

# Function to print section headers
print_header() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${GREEN}$1${NC}"
  echo -e "${BLUE}========================================${NC}"
}

# Function to run a curl command and pretty-print the JSON response
run_curl() {
  echo -e "${YELLOW}COMMAND:${NC} $1"
  echo -e "${YELLOW}RESPONSE:${NC}"
  eval $1 | jq '.'
  echo ""
}

# Start of examples
echo -e "${GREEN}GEO-INFER-API CURL Examples${NC}"

# 1. List available feature collections
print_header "1. List available feature collections"
run_curl "curl -s ${API_BASE_URL}/collections"

# 2. Get polygon collection metadata
print_header "2. Get polygon collection metadata"
run_curl "curl -s ${API_BASE_URL}/collections/polygons"

# 3. Create a polygon feature
print_header "3. Create a polygon feature"
# Sample GeoJSON polygon (triangle around San Francisco)
cat > sf_polygon.json << EOF
{
  "type": "Feature",
  "id": "${FEATURE_ID}",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.51, 37.77],
        [-122.42, 37.81],
        [-122.37, 37.73],
        [-122.51, 37.77]
      ]
    ]
  },
  "properties": {
    "name": "San Francisco Triangle",
    "description": "A triangular area in San Francisco",
    "tags": ["example", "demo", "triangle"]
  }
}
EOF

run_curl "curl -s -X POST ${API_BASE_URL}/collections/polygons/items -H 'Content-Type: application/json' -d @sf_polygon.json"

# 4. List polygon features
print_header "4. List polygon features"
run_curl "curl -s ${API_BASE_URL}/collections/polygons/items"

# 5. Get a specific polygon feature
print_header "5. Get a specific polygon feature"
run_curl "curl -s ${API_BASE_URL}/collections/polygons/items/${FEATURE_ID}"

# 6. Calculate the area of a polygon
print_header "6. Calculate polygon area"
run_curl "curl -s -X POST ${API_BASE_URL}/operations/polygon/area -H 'Content-Type: application/json' -d @sf_polygon.json"

# 7. Check if a point is inside a polygon
print_header "7. Check if a point is inside a polygon"
run_curl "curl -s -X POST '${API_BASE_URL}/operations/polygon/contains?lon=-122.42&lat=37.78' -H 'Content-Type: application/json' -d @sf_polygon.json"

# 8. Simplify a polygon
print_header "8. Simplify a polygon"
run_curl "curl -s -X POST '${API_BASE_URL}/operations/polygon/simplify?tolerance=0.05' -H 'Content-Type: application/json' -d @sf_polygon.json"

# 9. Update a polygon feature
print_header "9. Update a polygon feature"
# Updated GeoJSON polygon with new properties
cat > sf_polygon_updated.json << EOF
{
  "type": "Feature",
  "id": "${FEATURE_ID}",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.51, 37.77],
        [-122.42, 37.81],
        [-122.37, 37.73],
        [-122.51, 37.77]
      ]
    ]
  },
  "properties": {
    "name": "San Francisco Triangle",
    "description": "A triangular area in San Francisco",
    "tags": ["example", "demo", "triangle"],
    "updated": true,
    "last_modified": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  }
}
EOF

run_curl "curl -s -X PUT ${API_BASE_URL}/collections/polygons/items/${FEATURE_ID} -H 'Content-Type: application/json' -d @sf_polygon_updated.json"

# 10. Delete a polygon feature
print_header "10. Delete a polygon feature"
run_curl "curl -s -X DELETE ${API_BASE_URL}/collections/polygons/items/${FEATURE_ID} -v"

# 11. List polygon features again to confirm deletion
print_header "11. List polygon features after deletion"
run_curl "curl -s ${API_BASE_URL}/collections/polygons/items"

# Clean up temporary files
rm -f sf_polygon.json sf_polygon_updated.json

echo -e "${GREEN}CURL examples completed!${NC}" 