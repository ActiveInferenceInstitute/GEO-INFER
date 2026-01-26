# Agent
: microeconomics ## Scope
 This directory contains microeconomics components for the module. It provides 34 classes and 10 functions. ## Classes
 and Functions ### BehavioralParameter
s
 Parameters for behavioral economic models ### ProspectTheor
y
 Prospect theory implementation with value function and probability weighting **Methods**: - `value_function(outcomes: np.ndarray, reference_point: float) -> np.ndarray`: Prospect theory value function - `probability_weighting(probabilities: np.ndarray) -> np.ndarray`: Probability weighting function (Prelec or other) - `prospect_value(outcomes: np.ndarray, probabilities: np.ndarray, reference_point: float) -> float`: Calculate overall prospect value ### BoundedRationalit
y
 Models of bounded rationality and cognitive limitations **Methods**: - `satisficing_model(alternatives: List[Dict[str, Any]], aspiration_level: float) -> Dict[str, Any]`: Satisficing choice model (Simon, 1955) - `recognition_heuristic(alternatives: List[str], recognition_memory: Dict[str, float]) -> str`: Recognition heuristic for decision making ### SocialPreference
s
 Models of social preferences and fairness **Methods**: - `fehr_schmidt_model(own_payoff: float, other_payoff: float, alpha: float, beta: float) -> float`: Fehr-Schmidt model of inequity aversion - `calculate_social_welfare(payoffs: List[float], social_welfare_function: str) -> float`: Calculate social welfare using different welfare functions ### TimePreference
s
 Models of time preferences and discounting **Methods**: - `hyperbolic_discounting(delay: float, k: float) -> float`: Hyperbolic discounting function - `quasi_hyperbolic_discounting(delay: float, beta: float, delta: float) -> float`: Quasi-hyperbolic discounting (β-δ model) - `analyze_time_inconsistency(reward_sizes: List[float], delays: List[float], discount_params: Dict[str, float]) -> Dict[str, Any]`: Analyze time inconsistency in intertemporal choice ### MentalAccountin
g
 Mental accounting and framing effects **Methods**: - `analyze_framing_effect(problem_framing: Dict[str, Any], choice_options: List[Dict[str, Any]]) -> Dict[str, Any]`: Analyze how problem framing affects choices - `mental_accounting_segregation(transactions: List[Dict[str, Any]]) -> Dict[str, Any]`: Analyze how people mentally segregate or integrate financial transactions ### NudgeAnalysi
s
 Analysis of nudges and behavioral interventions **Methods**: - `evaluate_nudge_effectiveness(nudge_type: str, target_behavior: str, population_characteristics: Dict[str, Any]) -> Dict[str, Any]`: Evaluate the effectiveness of different nudge types ### BehavioralEconomicsEngin
e
 Main behavioral economics modeling engine **Methods**: - `analyze_behavioral_choice(choice_problem: Dict[str, Any]) -> Dict[str, Any]`: behavioral analysis of a choice problem - `evaluate_nudge_intervention(nudge_design: Dict[str, Any], target_population: Dict[str, Any]) -> Dict[str, Any]`: Evaluate a behavioral nudge intervention ### ConsumerProfil
e
 Profile of an individual consumer with spatial attributes ### UtilityFunction
s
 Collection of utility function implementations for consumer theory **Methods**: - `cobb_douglas(quantities: np.ndarray, alpha: np.ndarray) -> float`: Cobb-Douglas utility function: U = ∏(x_i^α_i) - `ces_utility(quantities: np.ndarray, alpha: np.ndarray, rho: float) -> float`: Constant Elasticity of Substitution (CES) utility function - `linear_utility(quantities: np.ndarray, alpha: np.ndarray) -> float`: Linear utility function: U = ∑(α_i * x_i) - `leontief_utility(quantities: np.ndarray, alpha: np.ndarray) -> float`: Leontief utility function: U = min(x_i/α_i) - `spatial_utility(quantities: np.ndarray, alpha: np.ndarray, location: Tuple[float, float], accessibility_weight: float) -> float`: Spatial utility function incorporating location-based preferences ### DemandFunction
s
 Implementation of various demand function derivations and estimations **Methods**: - `marshallian_demand_cobb_douglas(income: float, prices: np.ndarray, alpha: np.ndarray) -> np.ndarray`: Marshallian (uncompensated) demand for Cobb-Douglas utility - `hicksian_demand_cobb_douglas(prices: np.ndarray, alpha: np.ndarray, utility_target: float) -> np.ndarray`: Hicksian (compensated) demand for Cobb-Douglas utility - `estimate_demand_system(data: pd.DataFrame, method: str) -> Dict[str, Any]`: Estimate demand system from consumer data ### ConsumerChoiceModel
s
 Consumer choice modeling with spatial considerations **Methods**: - `solve_utility_maximization(consumer: ConsumerProfile, prices: np.ndarray, goods: List[str]) -> Dict[str, Any]`: Solve consumer utility maximization problem - `spatial_consumer_choice(consumer: ConsumerProfile, spatial_markets: gpd.GeoDataFrame, transport_costs: Dict[str, float]) -> Dict[str, Any]`: Model consumer choice with spatial market selection ### WelfareAnalysi
s
 Consumer welfare analysis tools **Methods**: - `consumer_surplus_linear(demand_function: Callable, price: float, quantity: float) -> float`: Calculate consumer surplus for linear demand - `equivalent_variation(utility_function: Callable, income: float, prices_old: np.ndarray, prices_new: np.ndarray, alpha: np.ndarray) -> float`: Calculate equivalent variation for price change - `compensating_variation(utility_function: Callable, income: float, prices_old: np.ndarray, prices_new: np.ndarray, alpha: np.ndarray) -> float`: Calculate compensating variation for price change ### ConsumerSurplu
s
 Consumer surplus calculation and analysis **Methods**: - `calculate_surplus_integral(demand_function: Callable, price_range: Tuple[float, float], market_price: float) -> float`: Calculate consumer surplus by integrating under demand curve - `spatial_surplus_analysis(consumers: List[ConsumerProfile], spatial_markets: gpd.GeoDataFrame) -> Dict[str, Any]`: Analyze consumer surplus across spatial markets ### Gam
e
 Definition of a strategic form game ### ExtensiveFormGam
e
 Definition of an form game ### NashEquilibriu
m
 Nash equilibrium computation and analysis **Methods**: - `find_nash_equilibrium(game: Game) -> List[Dict[str, Any]]`: Find Nash equilibria in strategic form games - `compute_mixed_strategy_equilibrium(game: Game) -> Dict[str, Any]`: Compute mixed strategy Nash equilibrium ### AuctionTheor
y
 Auction theory and mechanism design **Methods**: - `analyze_first_price_auction(values: List[float], n_bidders: int) -> Dict[str, Any]`: Analyze first-price sealed-bid auction - `analyze_second_price_auction(values: List[float]) -> Dict[str, Any]`: Analyze second-price sealed-bid auction (Vickrey auction) ### EvolutionaryGame
s
 Evolutionary game theory and population dynamics **Methods**: - `replicator_dynamics(payoff_matrix: np.ndarray, initial_frequencies: np.ndarray, time_steps: int) -> Dict[str, Any]`: Simulate replicator dynamics for evolutionary games ### SpatialGame
s
 Spatial game theory and location models **Methods**: - `location_game_analysis(locations: np.ndarray, demand_function: Callable) -> Dict[str, Any]`: Analyze location choice in spatial competition (Hotelling model) ### BargainingTheor
y
 Bargaining theory and cooperative games **Methods**: - `nash_bargaining_solution(utility_possibilities: np.ndarray, disagreement_point: np.ndarray, risk_aversion: float) -> Dict[str, Any]`: Compute Nash bargaining solution ### GameTheoryModel
s
 Main game theory modeling class **Methods**: - `analyze_strategic_game(game: Game) -> Dict[str, Any]`: analysis of strategic form game - `analyze_auction_game(auction_type: str, valuations: List[float], n_bidders: int) -> Dict[str, Any]`: Analyze auction game - `analyze_evolutionary_game(payoff_matrix: np.ndarray, initial_frequencies: np.ndarray) -> Dict[str, Any]`: Analyze evolutionary game dynamics - `analyze_location_game(locations: np.ndarray, demand_function: Callable) -> Dict[str, Any]`: Analyze spatial location game ### MarketDefinitio
n
 Definition of a market for antitrust analysis ### CompetitionAnalysi
s
 Analysis of market competition and structure **Methods**: - `calculate_price_correlation_matrix(price_data: pd.DataFrame) -> np.ndarray`: Calculate price correlation matrix for market definition - `test_market_definition(price_data: pd.DataFrame, candidate_market: List[str]) -> Dict[str, Any]`: Test whether candidate products/locations constitute a relevant market - `analyze_entry_barriers(industry_data: pd.DataFrame) -> Dict[str, Any]`: Analyze entry barriers in an industry ### SpatialMarketAnalysi
s
 Spatial market analysis and geographic market delineation **Methods**: - `delineate_geographic_markets(price_data: pd.DataFrame, locations: List[str]) -> Dict[str, Any]`: Delineate geographic markets based on price integration - `calculate_market_accessibility(locations: np.ndarray, market_centers: np.ndarray) -> np.ndarray`: Calculate market accessibility for different locations ### MarketStructureAnalysi
s
 Main market structure analysis class **Methods**: - `analyze_market_power(market_data: pd.DataFrame) -> Dict[str, Any]`: Analyze market power and concentration - `analyze_spatial_market_structure(spatial_data: pd.DataFrame) -> Dict[str, Any]`: Analyze market structure in spatial context ### FirmProfil
e
 Profile of a firm for producer theory analysis ### ProductionFunction
s
 Collection of production function implementations **Methods**: - `cobb_douglas(inputs: np.ndarray, alpha: np.ndarray) -> float`: Cobb-Douglas production function: Q = A * ∏(X_i^α_i) - `ces_production(inputs: np.ndarray, alpha: np.ndarray, rho: float, A: float) -> float`: Constant Elasticity of Substitution production function - `translog_production(inputs: np.ndarray, beta: np.ndarray) -> float`: Translog production function for flexible functional forms - `leontief_production(inputs: np.ndarray, alpha: np.ndarray) -> float`: Leontief fixed proportions production function ### CostMinimizatio
n
 Cost minimization and cost function analysis **Methods**: - `minimize_cost(output_target: float, input_prices: np.ndarray, production_params: Dict[str, Any]) -> Dict[str, Any]`: Solve cost minimization problem ### TechnicalEfficienc
y
 Technical efficiency analysis using DEA and SFA **Methods**: - `data_envelopment_analysis(inputs: np.ndarray, outputs: np.ndarray) -> np.ndarray`: Calculate technical efficiency using Data Envelopment Analysis (DEA) ### ProducerTheoryModel
s
 Main producer theory modeling class **Methods**: - `analyze_production_possibilities(firms: List[FirmProfile]) -> Dict[str, Any]`: Analyze production possibilities frontier for multiple firms - `calculate_cost_function(output_level: float, input_prices: np.ndarray, production_params: Dict[str, Any]) -> Dict[str, Any]`: Calculate cost function for given output level ### MarketStructureAnalysi
s
 Analysis of market structure and competition **Methods**: - `calculate_market_concentration(market_shares: np.ndarray) -> Dict[str, float]`: Calculate market concentration indices ### GameTheoryModel
s
 Game theory applications in economics **Methods**: - `solve_cournot_game(n_firms: int, demand_params: Dict[str, float], cost_params: List[float]) -> Dict[str, Any]`: Solve Cournot oligopoly game ### BehavioralEconomicsEngin
e
 Behavioral economics modeling and analysis **Methods**: - `prospect_theory_valuation(outcomes: np.ndarray, probabilities: np.ndarray, reference_point: float, alpha: float, beta: float, lambda_param: float) -> float`: Calculate prospect theory value function - `analyze_risk_preferences(choice_data: pd.DataFrame) -> Dict[str, Any]`: Analyze risk preferences from choice data ### example_consumer_analysi
s
 `example_consumer_analysis()` Example usage of consumer theory models ### objectiv
e
 `objective(quantities)` Negative utility to minimize ### budget_constrain
t
 `budget_constraint(quantities)` Budget constraint: sum(p_i * x_i) <= income ### objectiv
e
 `objective(test_income)` ### objectiv
e
 `objective(test_income)` ### integran
d
 `integrand(p)` ### equation
s
 `equations(p)` ### cost_functio
n
 `cost_function(inputs)` Cost function to minimize ### production_constrain
t
 `production_constraint(inputs)` Constraint: output >= target ### reaction_functio
n
 `reaction_function(i, q_others)` ## Capabilities
 - **34 classes** for core functionality - **10 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-ECON/src/geo_infer_econ/microeconomics` - **Type**: Directory Node 