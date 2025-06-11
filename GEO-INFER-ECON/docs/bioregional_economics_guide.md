# Bioregional Economics Module Guide

## Overview

The bioregional economics module in GEO-INFER-ECON provides comprehensive tools for analyzing economic systems within ecological boundaries, integrating natural capital, ecosystem services, and sustainable development principles. It bridges ecological science and economic theory to support regenerative and circular economic models.

## Core Principles

### Ecological Economics Foundation
- **Biophysical Equilibrium**: Economic activity constrained by ecological limits
- **Thermodynamic Models**: Energy and material flow analysis
- **Carrying Capacity**: Regional capacity for sustainable economic activity
- **Ecological Footprint**: Impact assessment within bioregional boundaries

### Bioregional Approach
- **Natural Boundaries**: Economic analysis within watershed, ecosystem, or ecological regions
- **Local Self-Reliance**: Emphasis on local production and circular resource flows
- **Community Governance**: Participatory and adaptive management systems
- **Regenerative Design**: Economic activities that enhance ecological health

## Key Components

### 1. Natural Capital Accounting
- **Ecosystem Assets Valuation**: Forests, wetlands, soil, water bodies
- **Biodiversity Credits**: Tradeable units representing biodiversity conservation
- **Carbon Accounting**: Comprehensive carbon stock and flow analysis
- **Water Resource Accounting**: Watershed-level water balance and valuation

### 2. Ecosystem Services Markets
- **Provisioning Services**: Food, fiber, freshwater, energy resources
- **Regulating Services**: Climate regulation, water purification, pollination
- **Cultural Services**: Recreation, spiritual, educational values
- **Supporting Services**: Nutrient cycling, habitat provision

### 3. Bioregional Market Design
- **Payment for Ecosystem Services (PES)**: Market mechanisms for conservation
- **Habitat Banking**: Biodiversity offset markets
- **Carbon Markets**: Regional carbon sequestration and trading
- **Local Food Systems**: Community-supported agriculture and food networks

### 4. Circular Economy Models
- **Material Flow Analysis**: Tracking resource flows and waste streams
- **Industrial Ecology**: Inter-industry symbiosis and efficiency
- **Waste-to-Resource Systems**: Circular material and energy loops
- **Regenerative Design**: Biomimetic and nature-based solutions

## Usage Examples

### Ecosystem Service Valuation

```python
from geo_infer_econ.bioregional import BioregionalMarketDesign, BioregionalAsset

# Create forest asset
forest_asset = BioregionalAsset(
    asset_id="forest_001",
    asset_type="forest",
    location=(45.0, -120.0),
    area_hectares=100.0,
    ecological_attributes={
        'carbon_storage': 500.0,  # tons CO2
        'biodiversity_index': 0.8,
        'water_filtration': 0.9
    },
    economic_attributes={
        'market_value': 500000,
        'annual_income': 10000
    },
    ownership_type="community",
    ecosystem_services={
        'carbon_sequestration': 10.0,  # tons CO2/year
        'biodiversity_habitat': 0.8,
        'water_regulation': 0.9
    }
)

# Initialize market design
market = BioregionalMarketDesign(bioregion_boundary)
market.register_asset(forest_asset)

# Create carbon credits
quality_params = {
    'additionality': 0.9,
    'permanence': 0.8,
    'measurability': 0.85,
    'leakage_risk': 0.1,
    'co_benefits': 0.7
}

carbon_credit = market.create_ecosystem_service_credit(
    asset_id="forest_001",
    service_type="carbon",
    quantity=10.0,
    quality_parameters=quality_params
)
```

### Bioregional Market Trading

```python
from geo_infer_econ.bioregional import EcosystemServicesMarkets

# Initialize trading system
es_market = EcosystemServicesMarkets(market)

# Submit buy order for carbon credits
buy_order_id = es_market.submit_buy_order(
    participant_id="buyer_001",
    service_type="carbon",
    quantity=5.0,
    max_price=45.0
)

# Submit sell order
sell_order_id = es_market.submit_sell_order(
    participant_id="seller_001",
    credit_id=carbon_credit.credit_id,
    min_price=40.0
)

# Clear market and execute trades
transactions = es_market.clear_market()
```

### Natural Capital Assessment

```python
from geo_infer_econ.bioregional import NaturalCapitalAccounting

# Initialize natural capital accounting
nca = NaturalCapitalAccounting(bioregion_boundary)

# Comprehensive asset valuation
valuation_results = nca.assess_regional_natural_capital({
    'forests': forest_assets,
    'wetlands': wetland_assets,
    'agricultural_land': ag_assets
})

# Generate natural capital statements
statements = nca.generate_capital_statements(valuation_results)
```

## Advanced Features

### Biodiversity Credit Systems
- **Habitat Banking**: Create and trade biodiversity offset credits
- **Species-Specific Credits**: Credits for endangered species habitat
- **Connectivity Credits**: Value for landscape connectivity and corridors
- **Restoration Credits**: Credits for habitat restoration activities

### Local Food System Optimization
- **Food Miles Minimization**: Optimize local production and distribution
- **Nutritional Security**: Ensure regional food security and nutrition
- **Seasonal Production Planning**: Align production with ecological cycles
- **Community-Supported Agriculture**: Direct producer-consumer relationships

### Circular Economy Metrics
- **Circularity Indicators**: Material circularity rate, waste reduction
- **Resource Efficiency**: Input-output efficiency analysis
- **Regenerative Capacity**: Ecosystem regeneration and enhancement
- **Resilience Metrics**: Economic-ecological system resilience

## Integration with Ecological Data

### Biodiversity Monitoring
- Integration with species occurrence databases
- Habitat suitability modeling
- Connectivity analysis using landscape metrics
- Population viability assessments

### Ecosystem Service Mapping
- Remote sensing data integration
- Land use/land cover analysis
- Service flow modeling and quantification
- Spatial prioritization for conservation

### Climate Change Adaptation
- Climate vulnerability assessments
- Ecosystem-based adaptation strategies
- Carbon sequestration potential mapping
- Climate resilience planning

## Market Mechanisms

### Payment for Ecosystem Services (PES)
- **Direct Payments**: Government payments to landowners
- **Market-Based**: Private buyer-seller transactions
- **Reverse Auctions**: Competitive bidding for conservation contracts
- **Results-Based**: Payments tied to measured outcomes

### Biodiversity Offset Markets
- **No Net Loss**: Development impacts offset by conservation gains
- **Net Positive Impact**: Conservation gains exceed development impacts
- **Like-for-Like**: Offset same habitat types as impacted
- **Out-of-Kind**: Different but ecologically equivalent habitats

### Carbon Markets
- **Voluntary Markets**: Voluntary carbon offset purchases
- **Compliance Markets**: Regulatory cap-and-trade systems
- **Nature-Based Solutions**: Forest and land use carbon projects
- **Blue Carbon**: Coastal and marine carbon sequestration

## Governance and Institutions

### Bioregional Governance Models
- **Watershed Councils**: Collaborative watershed management
- **Community Land Trusts**: Community-owned land stewardship
- **Indigenous Governance**: Traditional ecological knowledge integration
- **Adaptive Management**: Learning-based management systems

### Stakeholder Engagement
- **Multi-Stakeholder Platforms**: Inclusive decision-making processes
- **Participatory Monitoring**: Community-based monitoring systems
- **Conflict Resolution**: Mediation and consensus-building processes
- **Capacity Building**: Education and skill development programs

## Configuration

Bioregional models are configured through the `bioregional` section:

```yaml
bioregional:
  ecological_economics:
    biophysical_equilibrium: true
    carrying_capacity_analysis: true
    ecological_footprint: true
  natural_capital:
    ecosystem_services_valuation: true
    biodiversity_credits: true
    carbon_accounting: true
  bioregional_markets:
    ecosystem_services_markets: true
    habitat_banking: true
    local_food_systems: true
  sustainability_metrics:
    resilience_indicators: true
    regenerative_metrics: true
    planetary_boundaries: true
```

## Research Applications

- **Conservation Economics**: Optimal conservation investment strategies
- **Sustainable Agriculture**: Economic analysis of regenerative farming
- **Watershed Management**: Economic instruments for water quality
- **Climate Finance**: Nature-based climate solutions economics
- **Urban Ecology**: Green infrastructure economic analysis
- **Indigenous Economics**: Traditional ecological knowledge economics
- **Restoration Economics**: Cost-effectiveness of ecosystem restoration
- **Circular Cities**: Urban circular economy transition strategies

## Integration with Other Modules

- **GEO-INFER-SPACE**: Spatial ecosystem service mapping and analysis
- **GEO-INFER-TIME**: Temporal dynamics of ecosystem services
- **GEO-INFER-DATA**: Integration with ecological and environmental datasets
- **GEO-INFER-AI**: Machine learning for ecosystem service prediction
- **GEO-INFER-RISK**: Climate and ecological risk assessment
- **GEO-INFER-AG**: Sustainable agriculture and agroecology economics 