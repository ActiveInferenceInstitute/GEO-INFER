# Agent
: bioregional ## Scope
 This directory contains bioregional components for the module. It provides 40 classes and 1 functions. ## Classes
 and Functions ### BioregionalGovernanceModel
s
 Bioregional governance modeling. **Methods**: - `model_governance(governance_data: Dict[str, Any]) -> Dict[str, Any]`: Model bioregional governance systems. ### CommunityResourceManagemen
t
 Community resource management. **Methods**: - `manage_resources(resource_data: Dict[str, Any]) -> Dict[str, Any]`: Manage community resources. ### AdaptiveManagementSystem
s
 Adaptive management systems. **Methods**: - `design_adaptive_system(system_params: Dict[str, Any]) -> Dict[str, Any]`: Design adaptive management system. ### StakeholderEngagemen
t
 Stakeholder engagement processes. **Methods**: - `engage_stakeholders(stakeholder_data: Dict[str, Any]) -> Dict[str, Any]`: Engage stakeholders in decision-making. ### CooperativeEconomic
s
 Cooperative economics models. **Methods**: - `model_cooperative(cooperative_data: Dict[str, Any]) -> Dict[str, Any]`: Model cooperative economic systems. ### BioregionalAsse
t
 Represents a bioregional asset with ecological and economic attributes ### MarketParticipan
t
 Represents a participant in bioregional markets ### EcosystemServiceCredi
t
 Represents a tradeable ecosystem service credit ### BioregionalMarketDesig
n
 Core engine for designing and operating bioregional markets **Methods**: - `register_asset(asset: BioregionalAsset) -> bool`: Register a bioregional asset in the market system - `register_participant(participant: MarketParticipant) -> bool`: Register a market participant - `create_ecosystem_service_credit(asset_id: str, service_type: str, quantity: float, quality_parameters: Dict[str, Any]) -> EcosystemServiceCredit`: Create ecosystem service credits from bioregional assets ### EcosystemServicesMarket
s
 Specialized markets for different ecosystem services **Methods**: - `submit_buy_order(participant_id: str, service_type: str, quantity: float, max_price: float, location_preferences: Dict[str, Any]) -> str`: Submit a buy order for ecosystem services - `submit_sell_order(participant_id: str, credit_id: str, min_price: float) -> str`: Submit a sell order for ecosystem service credits - `clear_market() -> List[Dict[str, Any]]`: Clear the market and execute trades ### BiodiversityMarket
s
 Specialized markets for biodiversity credits and habitat banking **Methods**: - `create_habitat_bank(bank_id: str, asset_ids: List[str], credit_types: List[str]) -> Dict[str, Any]`: Create a habitat bank for biodiversity credit generation - `calculate_mitigation_requirement(impact_location: Tuple[float, float], impact_area: float, habitat_type: str) -> Dict[str, float]`: Calculate biodiversity mitigation requirements for development impacts - `match_credits_to_requirements(requirement_id: str) -> List[Dict[str, Any]]`: Match available biodiversity credits to mitigation requirements ### LocalFoodSystem
s
 Markets and systems for local and regional food production and distribution **Methods**: - `optimize_local_food_system(optimization_objectives: List[str]) -> Dict[str, Any]`: Optimize local food system for multiple objectives using algorithms - `calculate_food_miles(producer_id: str, consumer_id: str) -> float`: Calculate food miles between producer and consumer ### CircularEconomyModel
s
 Circular economy modeling. **Methods**: - `model_circular_flows(flow_data: Dict[str, Any]) -> pd.DataFrame`: Model circular economy flows. ### MaterialFlowAnalysi
s
 Material flow analysis. **Methods**: - `analyze_flows(material_data: Dict[str, Any]) -> pd.DataFrame`: Analyze material flows. ### IndustrialEcologyModel
s
 Industrial ecology models. **Methods**: - `model_industrial_ecology(data: Dict[str, Any]) -> Dict[str, Any]`: Model industrial ecology systems. ### WasteToResourceSystem
s
 Waste-to-resource systems. **Methods**: - `design_system(waste_data: Dict[str, Any]) -> Dict[str, Any]`: Design waste-to-resource system. ### RegenerativeDesig
n
 Regenerative design principles. **Methods**: - `design_regenerative_system(design_params: Dict[str, Any]) -> Dict[str, Any]`: Design regenerative system. ### EcologicalEconomicsConfi
g
 Configuration for ecological economics models. ### BiophysicalEquilibriumModel
s
 Models for biophysical equilibrium analysis in ecological economics. **Methods**: - `analyze_equilibrium(model_type: str, parameters: Dict[str, Any], time_steps: int) -> Dict[str, Any]`: Analyze equilibrium for a specific model type. - `calculate_ecosystem_value(service_values: List[float], valuation_method: str) -> float`: Calculate total ecosystem value. ### EcosystemServicesValuatio
n
 Ecosystem services valuation. **Methods**: - `value_services(services: List[Dict[str, Any]]) -> Dict[str, float]`: Value ecosystem services. ### ProvisioningService
s
 Provisioning ecosystem services. **Methods**: - `value_provisioning(data: Dict[str, Any]) -> float`: Value provisioning services. ### RegulatingService
s
 Regulating ecosystem services. **Methods**: - `value_regulating(data: Dict[str, Any]) -> float`: Value regulating services. ### CulturalService
s
 Cultural ecosystem services. **Methods**: - `value_cultural(data: Dict[str, Any]) -> float`: Value cultural services. ### SupportingService
s
 Supporting ecosystem services. **Methods**: - `value_supporting(data: Dict[str, Any]) -> float`: Value supporting services. ### ServiceFlowModelin
g
 Ecosystem service flow modeling. **Methods**: - `model_flows(flow_data: Dict[str, Any]) -> pd.DataFrame`: Model ecosystem service flows. ### NaturalCapitalAccountin
g
 Natural capital accounting and valuation. **Methods**: - `account_assets(assets: List[Dict[str, Any]]) -> pd.DataFrame`: Account for natural capital assets. - `value_assets(assets: pd.DataFrame) -> pd.Series`: Value natural capital assets. ### EcosystemAssetsValuatio
n
 Ecosystem assets valuation. **Methods**: - `value_ecosystem_assets(assets: List[Dict[str, Any]]) -> Dict[str, float]`: Value ecosystem assets. ### BiodiversityCredit
s
 Biodiversity credits and trading. **Methods**: - `calculate_credits(biodiversity_data: Dict[str, Any]) -> float`: Calculate biodiversity credits. ### CarbonAccountin
g
 Carbon accounting and sequestration. **Methods**: - `account_carbon(carbon_data: Dict[str, Any]) -> pd.DataFrame`: Account for carbon stocks and flows. ### WaterResourceAccountin
g
 Water resource accounting. **Methods**: - `account_water(water_data: Dict[str, Any]) -> pd.DataFrame`: Account for water resources. ### LandscapeEconomic
s
 Landscape economics analysis. **Methods**: - `analyze_landscape(landscape_data: gpd.GeoDataFrame) -> Dict[str, Any]`: Analyze landscape economics. ### HabitatConnectivit
y
 Habitat connectivity analysis. **Methods**: - `analyze_connectivity(habitat_data: gpd.GeoDataFrame) -> Dict[str, Any]`: Analyze habitat connectivity. ### EcosystemNetworkAnalysi
s
 Ecosystem network analysis. **Methods**: - `analyze_network(network_data: Dict[str, Any]) -> Dict[str, Any]`: Analyze ecosystem networks. ### ConservationPrioritizatio
n
 Conservation prioritization. **Methods**: - `prioritize_areas(conservation_data: Dict[str, Any]) -> pd.DataFrame`: Prioritize conservation areas. ### RestorationEconomic
s
 Restoration economics. **Methods**: - `analyze_restoration(restoration_data: Dict[str, Any]) -> Dict[str, Any]`: Analyze restoration economics. ### SustainabilityIndicator
s
 Sustainability indicators calculation. **Methods**: - `calculate_indicators(data: Dict[str, Any]) -> pd.DataFrame`: Calculate sustainability indicators. ### ResilienceMetric
s
 Resilience metrics. **Methods**: - `calculate_resilience(resilience_data: Dict[str, Any]) -> Dict[str, float]`: Calculate resilience metrics. ### RegenerativeMetric
s
 Regenerative metrics. **Methods**: - `calculate_regenerative(data: Dict[str, Any]) -> Dict[str, float]`: Calculate regenerative metrics. ### WellbeingIndicator
s
 Wellbeing indicators. **Methods**: - `calculate_wellbeing(wellbeing_data: Dict[str, Any]) -> Dict[str, float]`: Calculate wellbeing indicators. ### PlanetaryBoundarie
s
 Planetary boundaries assessment. **Methods**: - `assess_boundaries(boundary_data: Dict[str, Any]) -> Dict[str, Any]`: Assess planetary boundaries. ### example_bioregional_marke
t
 `example_bioregional_market()` Example usage of bioregional market design ## Capabilities
 - **40 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-ECON/src/geo_infer_econ/bioregional` - **Type**: Directory Node 