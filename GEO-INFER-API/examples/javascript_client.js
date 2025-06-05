/**
 * Example JavaScript client for the GEO-INFER-API GeoJSON polygon endpoints.
 * 
 * This script demonstrates how to interact with the GEO-INFER-API
 * for working with GeoJSON polygon features.
 */

// API base URL (change this to match your deployment)
const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * List available feature collections
 * @returns {Promise<Object>} Collections response
 */
async function listCollections() {
  const response = await fetch(`${API_BASE_URL}/collections`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Get metadata about the polygon collection
 * @returns {Promise<Object>} Collection metadata
 */
async function getPolygonCollection() {
  const response = await fetch(`${API_BASE_URL}/collections/polygons`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * List polygon features with optional filtering
 * @param {string} [bbox] - Optional bounding box in format "minLon,minLat,maxLon,maxLat"
 * @param {number} [limit=10] - Maximum number of features to return
 * @returns {Promise<Object>} FeatureCollection of polygons
 */
async function listPolygonFeatures(bbox, limit = 10) {
  const params = new URLSearchParams({ limit });
  if (bbox) {
    params.append('bbox', bbox);
  }
  
  const response = await fetch(
    `${API_BASE_URL}/collections/polygons/items?${params.toString()}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Get a specific polygon feature by ID
 * @param {string} featureId - ID of the feature to retrieve
 * @returns {Promise<Object>} GeoJSON Feature
 */
async function getPolygonFeature(featureId) {
  const response = await fetch(
    `${API_BASE_URL}/collections/polygons/items/${featureId}`
  );
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Create a new polygon feature
 * @param {Array} coords - List of rings where each ring is a list of [lon, lat] coordinates
 * @param {Object} [properties={}] - Properties to attach to the feature
 * @param {string} [featureId] - Optional feature ID
 * @returns {Promise<Object>} Created GeoJSON Feature
 */
async function createPolygonFeature(coords, properties = {}, featureId = null) {
  // Generate a feature ID if none provided
  if (!featureId) {
    featureId = 'f_' + Math.random().toString(36).substr(2, 9);
  }
  
  // Create the GeoJSON Feature
  const feature = {
    type: 'Feature',
    id: featureId,
    geometry: {
      type: 'Polygon',
      coordinates: coords
    },
    properties: properties
  };
  
  // Send the request
  const response = await fetch(
    `${API_BASE_URL}/collections/polygons/items`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(feature)
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Update an existing polygon feature
 * @param {string} featureId - ID of the feature to update
 * @param {Array} coords - New coordinates for the polygon
 * @param {Object} [properties={}] - New properties
 * @returns {Promise<Object>} Updated GeoJSON Feature
 */
async function updatePolygonFeature(featureId, coords, properties = {}) {
  // Create the GeoJSON Feature
  const feature = {
    type: 'Feature',
    id: featureId,
    geometry: {
      type: 'Polygon',
      coordinates: coords
    },
    properties: properties
  };
  
  // Send the request
  const response = await fetch(
    `${API_BASE_URL}/collections/polygons/items/${featureId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(feature)
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Delete a polygon feature
 * @param {string} featureId - ID of the feature to delete
 * @returns {Promise<void>}
 */
async function deletePolygonFeature(featureId) {
  const response = await fetch(
    `${API_BASE_URL}/collections/polygons/items/${featureId}`,
    { method: 'DELETE' }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return;
}

/**
 * Calculate the area of a polygon
 * @param {Object} feature - GeoJSON Feature with Polygon geometry
 * @returns {Promise<Object>} Area calculation result
 */
async function calculatePolygonArea(feature) {
  const response = await fetch(
    `${API_BASE_URL}/operations/polygon/area`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(feature)
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Simplify a polygon
 * @param {Object} feature - GeoJSON Feature with Polygon geometry
 * @param {number} [tolerance=0.01] - Simplification tolerance
 * @returns {Promise<Object>} Simplified polygon feature
 */
async function simplifyPolygon(feature, tolerance = 0.01) {
  const params = new URLSearchParams({ tolerance });
  
  const response = await fetch(
    `${API_BASE_URL}/operations/polygon/simplify?${params.toString()}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(feature)
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Check if a point is inside a polygon
 * @param {Object} feature - GeoJSON Feature with Polygon geometry
 * @param {number} lon - Longitude of the point
 * @param {number} lat - Latitude of the point
 * @returns {Promise<Object>} Result indicating if the point is inside
 */
async function checkPointInPolygon(feature, lon, lat) {
  const params = new URLSearchParams({ lon, lat });
  
  const response = await fetch(
    `${API_BASE_URL}/operations/polygon/contains?${params.toString()}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(feature)
    }
  );
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

/**
 * Example usage
 */
async function runExample() {
  console.log('GEO-INFER-API JavaScript Client Example');
  console.log('-'.repeat(40));
  
  // Define a sample polygon (triangle around the San Francisco area)
  const sfPolygon = [
    [
      [-122.51, 37.77],
      [-122.42, 37.81],
      [-122.37, 37.73],
      [-122.51, 37.77]  // Close the polygon
    ]
  ];
  
  // Define properties
  const sfProperties = {
    name: 'San Francisco Triangle',
    description: 'A triangular area in San Francisco',
    tags: ['example', 'demo', 'triangle']
  };
  
  try {
    // List collections
    console.log('\n1. Listing collections...');
    const collections = await listCollections();
    console.log(`Found ${collections.collections.length} collections`);
    
    // Create a polygon feature
    console.log('\n2. Creating a polygon feature...');
    const featureId = 'sf-triangle-js-demo';
    const createdFeature = await createPolygonFeature(
      sfPolygon, 
      sfProperties, 
      featureId
    );
    console.log(`Created feature with ID: ${createdFeature.id}`);
    
    // Get the feature
    console.log('\n3. Retrieving the feature...');
    const retrievedFeature = await getPolygonFeature(featureId);
    console.log(`Retrieved feature: ${retrievedFeature.id}`);
    
    // Calculate area
    console.log('\n4. Calculating polygon area...');
    const areaResult = await calculatePolygonArea(retrievedFeature);
    console.log(`Area: ${areaResult.area_sq_km.toFixed(2)} square kilometers`);
    
    // Check if a point is inside
    console.log('\n5. Checking if a point is inside the polygon...');
    // Point in downtown San Francisco
    const containsResult = await checkPointInPolygon(retrievedFeature, -122.42, 37.78);
    console.log(`Contains point: ${containsResult.contains}`);
    
    // Simplify the polygon
    console.log('\n6. Simplifying the polygon...');
    const simplified = await simplifyPolygon(retrievedFeature, 0.05);
    console.log('Simplified polygon created');
    
    // Update the feature
    console.log('\n7. Updating the feature...');
    const updatedProperties = {
      ...sfProperties,
      updated: true
    };
    const updatedFeature = await updatePolygonFeature(
      featureId, 
      sfPolygon, 
      updatedProperties
    );
    console.log(`Updated feature: ${updatedFeature.id}`);
    
    // List features
    console.log('\n8. Listing all polygon features...');
    const features = await listPolygonFeatures();
    console.log(`Found ${features.features.length} features`);
    
    // Delete the feature
    console.log('\n9. Deleting the feature...');
    await deletePolygonFeature(featureId);
    console.log(`Deleted feature with ID: ${featureId}`);
    
    console.log('\nAll operations completed successfully!');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run the example if this script is executed directly
if (typeof require !== 'undefined' && require.main === module) {
  runExample();
}

// For browser usage, expose the functions
if (typeof window !== 'undefined') {
  window.geoInferApi = {
    listCollections,
    getPolygonCollection,
    listPolygonFeatures,
    getPolygonFeature,
    createPolygonFeature,
    updatePolygonFeature,
    deletePolygonFeature,
    calculatePolygonArea,
    simplifyPolygon,
    checkPointInPolygon,
    runExample
  };
} 