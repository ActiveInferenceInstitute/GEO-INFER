# models
 ## Overview
 This directory contains models components. It includes 5 Python modules. ## Components
 ### active_inferenc
e
.py Active Inference Agent. **Classes**: `GenerativeModel`, `ActiveInferenceState`, `ActiveInferenceAgent` ### bd
i
.py Belief-Desire-Intention (BDI) Agent. **Classes**: `Belief`, `Desire`, `Plan`, `BDIState`, `BDIAgent` ### hybri
d
.py Hybrid Agent Architecture. **Classes**: `SubAgentWrapper`, `HybridState`, `HybridAgent` ### r
l
.py Reinforcement Learning Agent. **Classes**: `Experience`, `QTable`, `ReplayBuffer`, `RLState`, `RLAgent` ### rule_base
d
.py Rule-based Agent. **Classes**: `Rule`, `RuleSet`, `RuleBasedState`, `RuleBasedAgent` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 