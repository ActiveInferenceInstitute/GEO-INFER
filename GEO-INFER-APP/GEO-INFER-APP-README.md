# GEO-INFER-APP

## Overview
GEO-INFER-APP provides user interfaces, accessibility tools, and application development within the GEO-INFER framework. This module serves as the presentation layer for end users, enabling intuitive interaction with geospatial data and analysis capabilities.

## Key Features
- Map-centric GIS interfaces with interactive visualizations
- Mobile-friendly data collection tools
- Multilingual support and accessibility features for inclusivity
- Configurable dashboards and visualization components

## Directory Structure
```
GEO-INFER-APP/
├── docs/                 # Documentation
├── examples/             # Example use cases
├── src/                  # Source code
│   └── geo_infer_app/    # Main package
│       ├── api/          # API client connections
│       ├── components/   # Reusable UI components
│       ├── core/         # Core functionality
│       └── utils/        # Utility functions
└── tests/                # Test suite
```

## Getting Started
1. Installation
   ```bash
   # Backend
   pip install -e .
   
   # Frontend
   cd frontend
   npm install
   ```

2. Configuration
   ```bash
   cp config/example.yaml config/local.yaml
   # Edit local.yaml with your configuration
   ```

3. Running the Application
   ```bash
   # Backend
   python -m geo_infer_app.app
   
   # Frontend
   cd frontend
   npm run dev
   ```

## UI Components
GEO-INFER-APP provides a rich set of geospatial UI components:
- Interactive maps with multiple layer support
- Time-series visualizations
- Spatial data editors
- Form-based data collection tools
- Dashboard builder
- Report generators

## Technology Stack
- Backend: Python with FastAPI
- Frontend: React with TypeScript
- Map Rendering: Leaflet, Mapbox GL, deck.gl
- Data Visualization: D3.js, Plotly
- State Management: Redux/Context API
- Styling: Tailwind CSS

## Accessibility
The module is designed with accessibility in mind:
- WCAG 2.1 AA compliance
- Screen reader support
- Keyboard navigation
- Color contrast considerations
- Responsive design for various devices

## Internationalization
Built-in support for multiple languages through:
- Message translation systems
- Right-to-left (RTL) text handling
- Locale-specific formatting of dates, numbers, and currencies
- Cultural considerations in design

## Integration with Other Modules
GEO-INFER-APP integrates with:
- GEO-INFER-API for data access
- GEO-INFER-SPACE for spatial visualizations
- GEO-INFER-TIME for temporal visualizations
- GEO-INFER-CIV for community engagement features

## Contributing
Follow the contribution guidelines in the main GEO-INFER documentation. 