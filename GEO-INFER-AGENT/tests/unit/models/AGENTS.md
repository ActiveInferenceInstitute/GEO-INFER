# Agent
: models

## Scope
 This directory contains models components for the module. It provides 8 classes and 0 functions.

## Classes
 and Functions

### TestGenerativeModel
 Test cases for the GenerativeModel class.

**Methods**:
- `setUp()`: Set up test fixtures.
- `test_initialization()`: Test if the model initializes with correct dimensions.
- `test_update_likelihood()`: Test updating the likelihood mapping.
- `test_update_transition()`: Test updating the transition probabilities.
- `test_infer_state()`: Test state inference from an observation.
- `test_predict_next_state()`: Test next state prediction.
- `test_select_action()`: Test action selection through expected free energy minimization.
- `test_to_from_dict()`: Test serialization to and from dictionary.

### TestActiveInferenceState
 Test cases for the ActiveInferenceState class.

**Methods**:
- `setUp()`: Set up test fixtures.
- `test_initialization()`: Test if the state initializes correctly.
- `test_update_with_observation()`: Test updating state with observation.
- `test_record_action()`: Test recording an action.
- `test_update_preferences()`: Test updating preferences.
- `test_select_action()`: Test action selection.
- `test_to_from_dict()`: Test serialization to and from dictionary.

### TestActiveInferenceAgent
 Test cases for the ActiveInferenceAgent class.

**Methods**:
- `setUp()`: Set up test fixtures.
- `test_initialization()`: Test if the agent initializes with correct parameters.

### TestBelief
 Tests for the Belief class.

**Methods**:
- `test_belief_initialization()`: Test that a belief can be initialized with correct values.
- `test_belief_update()`: Test that a belief can be updated.
- `test_belief_to_dict()`: Test conversion to dictionary.
- `test_belief_from_dict()`: Test creation from dictionary.

### TestDesire
 Tests for the Desire class.

**Methods**:
- `test_desire_initialization()`: Test that a desire can be initialized with correct values.
- `test_desire_set_achieved()`: Test setting a desire as achieved.
- `test_desire_is_expired()`: Test checking if a desire has expired.
- `test_desire_to_dict()`: Test conversion to dictionary.
- `test_desire_from_dict()`: Test creation from dictionary.

### TestPlan
 Tests for the Plan class.

**Methods**:
- `test_plan_initialization()`: Test that a plan can be initialized with correct values.
- `test_plan_next_action()`: Test getting the next action from a plan.
- `test_plan_mark_complete()`: Test marking a plan as complete.
- `test_plan_to_dict()`: Test conversion to dictionary.
- `test_plan_from_dict()`: Test creation from dictionary.

### TestBDIState
 Tests for the BDIState class.

**Methods**:
- `test_state_initialization()`: Test that a BDI state can be initialized.
- `test_add_belief()`: Test adding a belief to the state.
- `test_update_belief()`: Test updating a belief in the state.
- `test_add_desire()`: Test adding a desire to the state.
- `test_get_desires_by_priority()`: Test getting desires sorted by priority.
- `test_add_intention()`: Test adding an intention to the state.
- `test_set_current_intention()`: Test setting the current intention.
- `test_to_dict_and_from_dict()`: Test conversion to and from dictionary.

### TestBDIAgent
 Tests for the BDIAgent class.

## Capabilities

- **8 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-AGENT/tests/unit/models`
- **Type**: Directory Node
