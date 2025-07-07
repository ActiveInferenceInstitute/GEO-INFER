- <h3>Searching Realms by name:</h3>

  - <strong>Method:</strong> GET
  - <strong>URL:</strong> `https://api.guardiansofearth.io/realms?query=name&regEx={searchText}`
  - <strong>Params:</strong>
    - regEx: string (complpete or partial Realm name) <strong>Required</strong>
    - limit: int
    - offset: int
  - <strong>Example request:</strong> `https://api.guardiansofearth.io/realms?query=name&regEx=Avana`
  - <strong>Example response:</strong>

  ```
  [
    {
      "_id": 6472,
      "name": "The Avana Retreat Vietnam",
      "logo": "https://balconymediagroup.com/wp-content/uploads/2022/09/Logo-Avana-Standard-300x233.png",
      "header_thumb": "https://biosmart-ui.s3.de.io.cloud.ovh.net/region-headers/region_6472_header_thumbnail.png"
    },
    {
      "_id": 8155,
      "name": "Havana @ Crescent",
      "logo": "https://goe-site-assets.s3.us-east-2.amazonaws.com/general_assets/bundlesxbioquest/tiny_away_logo.svg",
      "header_thumb": "https://biosmart-ui.s3.de.io.cloud.ovh.net/region-headers/region_8155_header_thumbnail.png"
    }
  ]
  ```

- <h3>Getting a list of all Realms:</h3>

  - <strong>Method:</strong> GET
  - <strong>URL:</strong> `https://portal.biosmart.life/api/v1/contest/109/regions.json`
  - <strong>Params:</strong>
    - limit: int
    - offset: int
    - sort_by: string, enum: ["id", "bioscore"]
    - sort_order: string, enum: ["desc", "asc"]
  - <strong>Response:</strong> Array of Realm objects like "realm_schema.json"

- <h3>Getting Realm details with an id:</h3>

  - <strong>Method:</strong> GET
  - <strong>URL:</strong> `https://portal.biosmart.life/api/v1/region/:id`
  - <strong>Example Request:</strong> `https://portal.biosmart.life/api/v1/region/2188`
  - <strong>Example Response:</strong> "realm_schema.json" object
  
