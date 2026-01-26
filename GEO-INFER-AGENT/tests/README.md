# GEO
-INFER-AGENT Test Suite This directory contains tests for the GEO-INFER-AGENT agent framework. ## Directory
 Structure ``` tests/ ├── unit/ # Unit tests │ └── models/ # Model-specific unit tests │ ├── test_active_inference.py # Active Inference agent tests │ ├── test_bdi.py # BDI agent tests │ └── test_rl.py # Reinforcement learning tests └── integration/ # Integration tests (future) └── performance/ # Performance benchmarks (future) ``` ## Test
 Categories ### Uni
t
 Tests #### Activ
e
 Inference Agents **File**: `unit/models/test_active_inference.py` Tests the core Active Inference agent implementation: ```python def test_active_inference_agent_initialization(): """Test agent creation with valid parameters""" agent = ActiveInferenceAgent( agent_id="test_agent", generative_model=simple_model, precision_parameters={'sensory': 1.0} ) assert agent.agent_id == "test_agent" assert agent.lifecycle == AgentLifecycle.CREATED def test_belief_updating(): """Test variational belief updating""" agent = ActiveInferenceAgent(...) observations = generate_test_observations() beliefs = agent.update_beliefs(observations) assert 'posterior' in beliefs assert beliefs['posterior'].shape == expected_shape def test_free_energy_minimization(): """Test expected free energy minimization""" agent = ActiveInferenceAgent(...) beliefs = agent.update_beliefs(test_observations) actions = agent.select_actions(beliefs, available_actions) assert len(actions) > 0 assert all(action in available_actions for action in actions) ``` #### BD
I
 Agents **File**: `unit/models/test_bdi.py` Tests Belief-Desire-Intention agent reasoning: ```python def test_bdi_reasoning_cycle(): """Test BDI reasoning cycle""" agent = BDIAgent( initial_beliefs={'location': 'warehouse'}, goals=['deliver_package'], plans=[delivery_plan] ) # Update beliefs agent.update_beliefs({'package_location': 'destination'}) # Deliberate goals current_goals = agent.deliberate() # Plan actions intentions = agent.means_ends_reasoning(current_goals) assert 'deliver_package' in [g.name for g in current_goals] assert len(intentions) > 0 ``` #### Reinforcemen
t
 Learning Agents **File**: `unit/models/test_rl.py` Tests reinforcement learning agent learning: ```python def test_q_learning(): """Test Q-learning algorithm""" agent = RLAgent( state_space=['position', 'cargo'], action_space=['move', 'load', 'unload'], learning_rate=0.1, discount_factor=0.9 ) # Simulate learning episode state = initial_state for _ in range(max_steps): action = agent.select_action(state) next_state, reward = environment.step(action) agent.learn(state, action, reward, next_state) state = next_state # Verify learning learned_policy = agent.get_policy() assert len(learned_policy) == len(state_space) ``` ## Running
 Tests ### Ru
n
 All Tests ```bash # From project root python -m pytest tests/ # Or from tests directory cd tests python -m pytest . ``` ### Ru
n
 Specific Test Categories ```bash # Unit tests only python -m pytest tests/unit/ # Model tests only python -m pytest tests/unit/models/ # Single test file python -m pytest tests/unit/models/test_active_inference.py # Single test function python -m pytest tests/unit/models/test_active_inference.py::test_belief_updating ``` ### Ru
n
 with Coverage ```bash # Generate coverage report python -m pytest --cov=geo_infer_agent --cov-report=html tests/ # View coverage report open htmlcov/index.html ``` ### Ru
n
 with Verbose Output ```bash # test output python -m pytest -v tests/ # Show print statements python -m pytest -s tests/ ``` ## Test
 Configuration ### Pytes
t
 Configuration Tests use the following pytest configuration (from `pytest.ini` in project root): ```ini [tool:pytest] testpaths = tests python_files = test_*.py python_classes = Test* python_functions = test_* addopts = -v --tb=short --strict-markers markers = unit: Unit tests integration: Integration tests performance: Performance tests slow: Slow running tests ``` ### Tes
t
 Fixtures Common test fixtures are defined in `conftest.py`: ```python @pytest.fixture def sample_generative_model(): """Provide a sample generative model for testing""" return create_test_generative_model() @pytest.fixture def mock_agent(): """Provide a mock agent for testing""" return Mock(spec=BaseAgent) @pytest.fixture def test_environment(): """Provide a test environment for agent testing""" return create_test_environment() ``` ## Test
 Data Test data is stored in `tests/data/` directory: - `test_observations.json`: Sample observation data - `test_models.yaml`: Test model configurations - `test_environments/`: Environment configurations for testing ## Performance
 Testing ### Benchmar
k
 Tests Performance benchmarks are implemented using pytest-benchmark: ```bash # Run performance benchmarks python -m pytest tests/ --benchmark-only # Compare benchmark results python -m pytest tests/ --benchmark-compare ``` ### Profilin
g
 Tests Memory and CPU profiling using pytest-profiling: ```bash # Profile test performance python -m pytest --profile tests/unit/models/test_active_inference.py ``` ## Continuous
 Integration ### GitHu
b
 Actions Tests are automatically run on: - Push to main branch - Pull requests - Scheduled nightly runs CI configuration: `.github/workflows/test.yml` ### Tes
t
 Requirements ```txt pytest>=7.0.0 pytest-cov>=4.0.0 pytest-benchmark>=4.0.0 pytest-mock>=3.0.0 pytest-xdist>=3.0.0 # Parallel test execution ``` ## Writing
 Tests ### Tes
t
 Structure Guidelines 1. **Test Naming**: Use descriptive names starting with `test_` 2. **Test Organization**: Group related tests in classes 3. **Fixture Usage**: Use fixtures for common test data 4. **Assertion Clarity**: Use clear, descriptive assertions 5. **Documentation**: Include docstrings for complex tests ### Exampl
e
 Test Template ```python import pytest from geo_infer_agent.models.bdi import BDIAgent class TestBDIAgent: """Test suite for BDI agent functionality""" @pytest.fixture def sample_bdi_agent(self): """Create a sample BDI agent for testing""" return BDIAgent( agent_id="test_bdi", initial_beliefs={'location': 'home'}, goals=['go_to_work'] ) def test_agent_creation(self, sample_bdi_agent): """Test successful agent creation""" assert sample_bdi_agent.agent_id == "test_bdi" assert 'location' in sample_bdi_agent.beliefs def test_belief_update(self, sample_bdi_agent): """Test belief updating mechanism""" new_beliefs = {'location': 'work', 'traffic': 'heavy'} sample_bdi_agent.update_beliefs(new_beliefs) assert sample_bdi_agent.beliefs['location'] == 'work' assert sample_bdi_agent.beliefs['traffic'] == 'heavy' def test_goal_deliberation(self, sample_bdi_agent): """Test goal deliberation process""" sample_bdi_agent.update_beliefs({'time': 'late'}) current_goals = sample_bdi_agent.deliberate() assert len(current_goals) > 0 # Verify goal selection logic ``` ### Mockin
g
 and Fixtures Use pytest-mock for mocking dependencies: ```python def test_agent_with_mocked_environment(self, mocker, sample_bdi_agent): """Test agent behavior with mocked environment""" mock_env = mocker.Mock() mock_env.get_observations.return_value = {'obstacle': 'none'} # Test agent perception observations = sample_bdi_agent.perceive(mock_env) mock_env.get_observations.assert_called_once() assert 'obstacle' in observations ``` ## Test
 Coverage Goals - **Unit Tests**: >90% coverage of core functionality - **Integration Tests**: Cover major component interactions - **Performance Tests**: Benchmark critical operations - **Edge Cases**: Test boundary conditions and error handling ## Troubleshooting
 ### Commo
n
 Test Issues 1. **Import Errors**: Ensure PYTHONPATH includes src directory 2. **Fixture Errors**: Check fixture definitions in conftest.py 3. **Async Tests**: Use pytest-asyncio for async test functions 4. **Database Tests**: Use pytest-django or similar for database testing ### Debuggin
g
 Tests ```bash # Run tests with debugging python -m pytest --pdb tests/unit/models/test_active_inference.py::test_belief_updating # Run with traceback python -m pytest --tb=long tests/ # Run tests in parallel for speed python -m pytest -n auto tests/ ``` ## Contributing
 When adding functionality: 1. Add corresponding unit tests 2. Ensure >90% test coverage for code 3. Add integration tests for component interactions 4. Update this README with test categories 5. Run test suite before submitting PR 