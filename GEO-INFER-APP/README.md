# GEO-INFER-APP

**User Interfaces, Application Development, and Accessibility**

## Overview

GEO-INFER-APP is the primary human-computer interaction layer for the GEO-INFER framework. It provides tools, components, and design patterns to build accessible geospatial applications and dashboards.

### Documentation
- Module page: ../GEO-INFER-INTRA/docs/modules/geo-infer-app.md
- Modules index: ../GEO-INFER-INTRA/docs/modules/index.md

## Core Objectives

-   **User-Centric Design:** Prioritize the needs and workflows of end-users to create intuitive and efficient interfaces.
-   **Accessibility (a11y):** Ensure applications are usable by people with a wide range of disabilities, adhering to standards like WCAG.
-   **Internationalization (i18n) & Localization (L10n):** Design applications that can be easily adapted to different languages, regions, and cultural contexts.
-   **Interactivity & Visualization:** Provide rich, interactive map-based visualizations and data exploration tools.
-   **Modularity & Reusability:** Develop a library of reusable UI components to accelerate application development.
-   **Responsiveness:** Ensure applications work seamlessly across various devices (desktops, tablets, mobiles).
-   **Seamless Integration:** Provide a cohesive frontend experience that seamlessly integrates functionalities from various backend GEO-INFER modules via GEO-INFER-API.

## Key Features

-   **Map-Centric GIS Interfaces:** Core focus on interactive maps as the primary way to display, query, and interact with geospatial data, supporting multiple base layers, thematic overlays, and drawing tools.
-   **Configurable Dashboards & Visualization Components:** A rich library of reusable UI components (charts, graphs, tables, indicators, spatial editors) that can be assembled into custom dashboards for monitoring, analysis, and reporting.
-   **Mobile-Friendly Data Collection Tools:** Responsive design and specific components optimized for field data collection on mobile devices, including offline capabilities and GPS integration.
-   **Comprehensive Accessibility Suite:** Built-in support for WCAG 2.1 AA (or higher) standards, including screen reader compatibility, keyboard navigation, sufficient color contrast, and ARIA attributes.
-   **Multilingual Support & Internationalization Framework:** Tools and processes for translating application interfaces into multiple languages, handling right-to-left (RTL) text, and adapting to locale-specific formats.
-   **Theming & White-Labeling Capabilities:** Allows for customization of the look and feel of applications to match organizational branding or specific project needs.
-   **User Authentication & Profile Management:** Secure integration with authentication systems (via GEO-INFER-API & GEO-INFER-SEC) and interfaces for user profile management.
-   **Client-Side SDK for GEO-INFER-API:** Provides a well-structured JavaScript/TypeScript SDK to simplify communication with backend GEO-INFER services.

## Conceptual Application Architecture

```mermaid
graph TD
    subgraph User_Interaction_Layer as "User / Browser"
        USER[User]
    end

    subgraph Frontend_Application as "GEO-INFER-APP Frontend (e.g., React, Vue, Angular)"
        direction LR
        VIEW[Views / Pages]
        COMPONENTS[Reusable UI Components]
        STATE[State Management (Redux, Context API etc.)]
        ROUTING[Client-Side Routing]
        API_CLIENT[GEO-INFER API Client (SDK)]
    end

    subgraph Backend_Services as "GEO-INFER Backend (via GEO-INFER-API)"
        GEO_API[GEO-INFER-API Gateway]
    end

    subgraph GEO_INFER_Modules as "Core GEO-INFER Modules"
        DATA[DATA]
        SPACE[SPACE]
        TIME[TIME]
        AI[AI]
        CIV[CIV]
        OTHERS[...Other Modules]
    end
    
    USER -- Interacts with --> VIEW
    VIEW -- Composed of --> COMPONENTS
    COMPONENTS -- Manages/Uses --> STATE
    VIEW -- Controlled by --> ROUTING
    COMPONENTS -- Fetches/Sends Data via --> API_CLIENT
    API_CLIENT -- HTTP Requests --> GEO_API
    
    GEO_API -- Proxies to --> DATA
    GEO_API -- Proxies to --> SPACE
    GEO_API -- Proxies to --> TIME
    GEO_API -- Proxies to --> AI
    GEO_API -- Proxies to --> CIV
    GEO_API -- Proxies to --> OTHERS

    classDef appLayer fill:#e6fffb,stroke:#00c4a7,stroke-width:2px;
    class Frontend_Application appLayer;
    classDef apiLayer fill:#e6faff,stroke:#00b8d4,stroke-width:2px;
    class Backend_Services apiLayer;

```

## Directory Structure
```
GEO-INFER-APP/
├── config/               # Configuration for frontend builds, API endpoints, themes
├── docs/                 # UI/UX guidelines, component library documentation, accessibility notes
├── examples/             # Example application setups or specific feature implementations
├── src/                  # Source code for the main application shell or core library
│   └── geo_infer_app/    # Main Python package (if a backend-for-frontend is used)
│       ├── api/          # Client-side API interaction layer / SDK 
│       ├── components/   # Reusable UI components (e.g., maps, charts, forms, spatial editors)
│       │   ├── agent/    # Specific components for agent-based modeling interfaces
│       │   ├── map/      # Map components (Leaflet, MapboxGL, DeckGL wrappers)
│       │   └── viz/      # Data visualization components (D3, Plotly wrappers)
│       ├── core/         # Core frontend logic, state management, routing
│       ├── layouts/      # Common page layouts and structures
│       ├── themes/       # Theming files (CSS variables, style guides)
│       ├── locales/      # Internationalization files (translation strings)
│       └── utils/        # Utility functions, helper scripts for frontend
├── tests/                # Frontend unit and integration tests (e.g., Jest, Cypress, Playwright)
├── public/               # Static assets (images, fonts, etc.)
└── (frontend_framework_specific_files) # e.g., package.json, vite.config.js, tsconfig.json for React/Vue/etc.
```

## Getting Started

### Prerequisites
-   **Backend:** Python 3.9+ (if a Backend-for-Frontend - BFF - is part of APP, e.g., using FastAPI).
-   **Frontend:** Node.js and npm/yarn for managing JavaScript dependencies and build processes.
-   Familiarity with a modern JavaScript framework (e.g., React, Vue, Angular, Svelte).
-   Access to a running GEO-INFER-API instance.

### Installation
```bash
# If GEO-INFER-APP includes a Python backend (e.g., for serving the app or BFF)
# pip install -e .

# For the frontend application (assuming a common structure)
# cd src/geo_infer_app/frontend  # Or wherever the frontend source lives
# npm install
# # or yarn install
```

### Configuration
Frontend applications typically configure API endpoint URLs, map API keys (e.g., Mapbox token), and other settings in environment variables (`.env` files) or configuration files within the frontend source tree.
```bash
# Example for frontend .env file
# VITE_GEO_INFER_API_URL=http://localhost:8000/api/v1
# VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here
```

### Running the Application
```bash
# If there's a Python backend for GEO-INFER-APP
# python -m geo_infer_app.server # Or similar command

# For the frontend development server
# cd src/geo_infer_app/frontend # Or equivalent path
# npm run dev
# # or yarn dev
```
This usually starts a local development server (e.g., on `http://localhost:3000` or `http://localhost:5173`).

## UI Components Library

GEO-INFER-APP aims to provide a rich, well-documented library of reusable geospatial UI components:

-   **Interactive Map Views:**
    -   Support for various base maps (OSM, satellite, custom).
    -   Layer management (vector, raster, WMS, heatmaps, clusters).
    -   Drawing and editing tools for points, lines, polygons.
    -   Popups and tooltips for feature interaction.
    -   Geocoding and reverse geocoding search bars.
-   **Data Visualization Components:**
    -   Time-series charts (line, bar, area).
    -   Statistical plots (scatter, histogram, box plots).
    -   Network graphs for relationship visualization.
    -   Choropleth and proportional symbol maps.
-   **Spatial Data Editors & Forms:**
    -   Form-based input with geospatial fields (e.g., coordinate pickers, geometry drawing).
    -   Attribute table editors linked to map features.
-   **Dashboard & Layout Components:**
    -   Grid systems for responsive layouts.
    -   Draggable and resizable panel/widget containers.
    -   Template for common application dashboards.
-   **Reporting & Export Tools:**
    -   Components for generating printable map layouts.
    -   Data export buttons (CSV, GeoJSON, KML, Shapefile via API).
-   **User Interaction Elements:**
    -   Sliders for temporal or parameter adjustments.
    -   Filters and search components for data tables and maps.
    -   User feedback and notification systems.

## Technology Stack (Example)

While flexible, a common modern stack might include:

-   **Backend (Optional BFF):** Python with FastAPI or Flask.
-   **Frontend Framework:** React with TypeScript, Vue.js, or SvelteKit.
-   **Map Rendering Libraries:** Leaflet, Mapbox GL JS, OpenLayers, Deck.gl, CesiumJS (for 3D).
-   **Data Visualization Libraries:** D3.js, Plotly.js, ECharts, Chart.js.
-   **State Management:** Redux, Zustand, Pinia, or framework-specific solutions (e.g., React Context).
-   **Styling:** Tailwind CSS, Material-UI, Bootstrap, CSS Modules, Styled Components.
-   **Build Tools:** Vite, Webpack.
-   **Testing:** Jest, Vitest, React Testing Library, Cypress, Playwright.

## Accessibility (a11y) Commitment

The module is designed with a strong commitment to web accessibility:

-   **WCAG Compliance:** Aiming for WCAG 2.1 Level AA or higher as a baseline.
-   **Semantic HTML:** Using HTML elements according to their intended purpose.
-   **ARIA Roles & Attributes:** Enhancing accessibility for dynamic content and custom components where standard HTML is insufficient.
-   **Keyboard Navigation:** Ensuring all interactive elements are focusable and operable via keyboard.
-   **Screen Reader Support:** Testing with common screen readers (e.g., NVDA, JAWS, VoiceOver).
-   **Color Contrast:** Providing sufficient contrast between text and background, and for UI elements.
-   **Focus Management:** Ensuring logical focus order and visible focus indicators.
-   **Responsive Design:** Adapting layouts and interactions for various screen sizes and orientations.
-   **Accessibility Audits:** Regular automated and manual testing for accessibility issues.

## Internationalization (i18n) & Localization (L10n)

Built-in support for creating applications that can serve a global audience:

-   **Message Translation Systems:** Using libraries like `i18next`, `react-i18next`, or `vue-i18n` to manage and load translated strings for UI elements.
-   **Right-to-Left (RTL) Text Handling:** CSS and layout considerations for languages written from right to left (e.g., Arabic, Hebrew).
-   **Locale-Specific Formatting:** Correctly formatting dates, numbers, currencies, and other locale-sensitive data.
-   **Cultural Considerations in Design:** Awareness of how colors, icons, and layouts might be perceived in different cultures.
-   **Pluralization Rules:** Handling language-specific rules for pluralizing nouns in dynamic messages.

## Integration with Other Modules

GEO-INFER-APP is the primary presentation layer, integrating heavily with:

-   **GEO-INFER-API:** Consumes data and services from all backend modules exposed through the API Gateway. This is its main point of contact with the rest of the framework.
-   **GEO-INFER-SPACE, GEO-INFER-TIME, GEO-INFER-AI, etc.:** The analytical and modeling capabilities of these modules are made accessible and visual through applications built with APP, via API.
-   **GEO-INFER-CIV:** APP provides the frontend components and interfaces for participatory mapping tools, surveys, and community engagement platforms developed in CIV.
-   **GEO-INFER-DATA:** Visualizes datasets managed by DATA and allows users to interact with them (query, filter, explore metadata).
-   **GEO-INFER-SEC:** User authentication and authorization flows are handled in the frontend by APP, coordinating with GEO-INFER-API and GEO-INFER-SEC.
-   **GEO-INFER-INTRA:** UI/UX guidelines, component documentation, and accessibility best practices from INTRA guide the development within APP.

## Contributing

Frontend developers, UI/UX designers, accessibility experts, and those with experience in geospatial visualization are highly encouraged to contribute. Areas include:

-   Developing new reusable UI components.
-   Improving existing components for better performance, accessibility, or features.
-   Creating example applications or dashboards.
-   Enhancing the theming system.
-   Writing documentation for UI components and design patterns.
-   Conducting usability testing and accessibility audits.
-   Adding or improving internationalization support.

Follow the contribution guidelines in the main GEO-INFER documentation (`CONTRIBUTING.md`) and specific frontend coding standards or design guidelines in `GEO-INFER-APP/docs/CONTRIBUTING_APP.md` (to be created).

## License

This module is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0). Please see the `LICENSE` file in the root of the GEO-INFER repository for full details. 