"""
Core components for active inference modeling.

This module contains the essential classes and functions for
implementing active inference models and algorithms.
"""

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.variational_inference import VariationalInference
from geo_infer_act.core.free_energy import FreeEnergy, ExpectedFreeEnergy
from geo_infer_act.core.markov_decision_process import MarkovDecisionProcess
from geo_infer_act.core.belief_updating import BayesianBeliefUpdate
from geo_infer_act.core.policy_selection import PolicySelection
from geo_infer_act.core.dynamic_causal_model import DynamicCausalModel 