"""
BDI Agent implementation.

This module contains the BDIState and BDIAgent classes that implement the
Belief-Desire-Intention cognitive architecture for geospatial agents.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from geo_infer_agent.core.agent_base import BaseAgent, AgentState

logger = logging.getLogger("geo_infer_agent.models.bdi")


# ---------------------------------------------------------------------------
# Lightweight BDI data types used internally by BDIState / BDIAgent.
# These are intentionally kept simple (plain classes, not dataclasses) so that
# BDIState can work without the richer bdi/belief.py / desire.py / plan.py
# dataclasses.  Serialization via to_dict / from_dict bridges both worlds.
# ---------------------------------------------------------------------------

class Belief:
    """
    A belief maintained by the agent about the world.

    Attributes:
        name: Unique identifier for the belief.
        value: Current value of the belief.
        confidence: Confidence level in [0, 1].
        timestamp: When the belief was last updated.
        metadata: Arbitrary additional information.
        history: Previous values of this belief.
    """

    def __init__(
        self,
        name: str,
        value: Any,
        confidence: float = 1.0,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.value = value
        self.confidence = max(0.0, min(1.0, confidence))
        self.timestamp = timestamp or datetime.now()
        self.metadata: Dict[str, Any] = metadata or {}
        self.history: List[Dict[str, Any]] = []

    def update(
        self,
        value: Any,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update this belief, storing the previous state in history."""
        self.history.append(
            {
                "value": self.value,
                "confidence": self.confidence,
                "timestamp": self.timestamp,
                "metadata": self.metadata.copy(),
            }
        )
        self.value = value
        if confidence is not None:
            self.confidence = max(0.0, min(1.0, confidence))
        if metadata:
            self.metadata.update(metadata)
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "history_length": len(self.history),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Belief":
        return Belief(
            name=data["name"],
            value=data["value"],
            confidence=data.get("confidence", 1.0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            metadata=data.get("metadata", {}),
        )


class Desire:
    """
    A goal the agent wants to achieve.

    Attributes:
        name: Unique identifier for the desire.
        description: Human-readable goal description.
        priority: Priority in [0, 1] (higher = more important).
        deadline: Optional deadline for achieving this desire.
        conditions: Belief values that must hold for the desire to be satisfied.
        achieved: Whether the desire has been achieved.
        achieved_at: When the desire was achieved.
    """

    def __init__(
        self,
        name: str,
        description: str,
        priority: float = 0.5,
        deadline: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.priority = max(0.0, min(1.0, priority))
        self.deadline = deadline
        self.conditions: Dict[str, Any] = conditions or {}
        self.created_at = datetime.now()
        self.achieved = False
        self.achieved_at: Optional[datetime] = None

    def set_achieved(self, achieved: bool = True) -> None:
        """Mark the desire as achieved or not."""
        self.achieved = achieved
        self.achieved_at = datetime.now() if achieved else None

    def is_expired(self) -> bool:
        """Return True if the desire has a past deadline."""
        if not self.deadline:
            return False
        return datetime.now() > self.deadline

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat(),
            "achieved": self.achieved,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Desire":
        desire = Desire(
            name=data["name"],
            description=data["description"],
            priority=data.get("priority", 0.5),
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            conditions=data.get("conditions", {}),
        )
        if data.get("created_at"):
            desire.created_at = datetime.fromisoformat(data["created_at"])
        desire.achieved = data.get("achieved", False)
        if data.get("achieved_at"):
            desire.achieved_at = datetime.fromisoformat(data["achieved_at"])
        return desire


class Plan:
    """
    A sequence of actions designed to satisfy a desire.

    Attributes:
        name: Unique identifier for the plan.
        desire_name: Name of the desire this plan targets.
        actions: Ordered list of action dictionaries.
        context_conditions: Belief values that must hold for this plan to apply.
        current_action_index: Index of the next action to execute.
        complete: Whether the plan has been fully executed.
        successful: Whether the plan completed successfully.
        execution_record: Log of executed actions and their results.
    """

    def __init__(
        self,
        name: str,
        desire_name: str,
        actions: List[Dict[str, Any]],
        context_conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.desire_name = desire_name
        self.actions = actions
        self.context_conditions: Dict[str, Any] = context_conditions or {}
        self.created_at = datetime.now()
        self.current_action_index = 0
        self.complete = False
        self.successful = False
        self.execution_record: List[Dict[str, Any]] = []

    def next_action(self) -> Optional[Dict[str, Any]]:
        """Return the next action to execute, or None if complete."""
        if self.complete or self.current_action_index >= len(self.actions):
            return None
        return self.actions[self.current_action_index]

    def record_action_result(
        self, action_index: int, result: Dict[str, Any], success: bool
    ) -> None:
        """Record the result of an executed action."""
        self.execution_record.append(
            {
                "action_index": action_index,
                "action": self.actions[action_index] if action_index < len(self.actions) else None,
                "result": result,
                "success": success,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def advance(self) -> bool:
        """Advance to the next action. Returns False when the plan is complete."""
        self.current_action_index += 1
        if self.current_action_index >= len(self.actions):
            self.complete = True
            return False
        return True

    def mark_complete(self, successful: bool) -> None:
        """Mark the plan as complete."""
        self.complete = True
        self.successful = successful

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "desire_name": self.desire_name,
            "actions": self.actions,
            "context_conditions": self.context_conditions,
            "created_at": self.created_at.isoformat(),
            "current_action_index": self.current_action_index,
            "complete": self.complete,
            "successful": self.successful,
            "execution_record": self.execution_record,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Plan":
        plan = Plan(
            name=data["name"],
            desire_name=data["desire_name"],
            actions=data["actions"],
            context_conditions=data.get("context_conditions", {}),
        )
        if data.get("created_at"):
            plan.created_at = datetime.fromisoformat(data["created_at"])
        plan.current_action_index = data.get("current_action_index", 0)
        plan.complete = data.get("complete", False)
        plan.successful = data.get("successful", False)
        plan.execution_record = data.get("execution_record", [])
        return plan


# ---------------------------------------------------------------------------
# BDIState
# ---------------------------------------------------------------------------

class BDIState(AgentState):
    """
    Extended agent state for BDI agents.

    Tracks beliefs, desires, and intentions (plans the agent is committed to).
    """

    def __init__(self, capacity: int = 1000) -> None:
        super().__init__(capacity)
        self.beliefs_dict: Dict[str, Belief] = {}
        self.desires_dict: Dict[str, Desire] = {}
        self.intentions: List[Plan] = []
        self.current_intention: Optional[Plan] = None
        # Expose beliefs/desires via the parent-class attribute names.
        self.beliefs = self.beliefs_dict
        self.desires = self.desires_dict

    # ------------------------------------------------------------------
    # Belief management
    # ------------------------------------------------------------------

    def add_belief(self, belief: Belief) -> None:
        """Add a new belief or merge into an existing one."""
        if belief.name in self.beliefs_dict:
            old = self.beliefs_dict[belief.name]
            old_value = old.value
            old_confidence = old.confidence
            old.update(value=belief.value, confidence=belief.confidence, metadata=belief.metadata)
            self.add_to_memory(
                {
                    "type": "belief_updated",
                    "name": belief.name,
                    "old_value": old_value,
                    "new_value": belief.value,
                    "old_confidence": old_confidence,
                    "new_confidence": belief.confidence,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            self.beliefs_dict[belief.name] = belief
            self.add_to_memory(
                {
                    "type": "belief_added",
                    "name": belief.name,
                    "value": belief.value,
                    "confidence": belief.confidence,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        self.last_update = datetime.now()

    def update_belief(
        self,
        name: str,
        value: Any,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update an existing belief or create it if absent."""
        if name in self.beliefs_dict:
            old = self.beliefs_dict[name]
            old_value = old.value
            old_confidence = old.confidence
            old.update(value=value, confidence=confidence, metadata=metadata)
            self.add_to_memory(
                {
                    "type": "belief_updated",
                    "name": name,
                    "old_value": old_value,
                    "new_value": value,
                    "old_confidence": old_confidence,
                    "new_confidence": confidence if confidence is not None else old_confidence,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            self.beliefs_dict[name] = Belief(
                name=name, value=value, confidence=confidence if confidence is not None else 1.0,
                metadata=metadata or {}
            )
            self.add_to_memory(
                {
                    "type": "belief_added",
                    "name": name,
                    "value": value,
                    "confidence": confidence if confidence is not None else 1.0,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        self.last_update = datetime.now()

    def get_belief(self, name: str) -> Optional[Belief]:
        """Return the named belief, or None if absent."""
        return self.beliefs_dict.get(name)

    # ------------------------------------------------------------------
    # Desire management
    # ------------------------------------------------------------------

    def add_desire(self, desire: Desire) -> None:
        """Add a desire to the desire set."""
        self.desires_dict[desire.name] = desire
        self.add_to_memory(
            {
                "type": "desire_added",
                "name": desire.name,
                "description": desire.description,
                "priority": desire.priority,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_desire(self, name: str) -> Optional[Desire]:
        """Return the named desire, or None if absent."""
        return self.desires_dict.get(name)

    def get_desires_by_priority(self) -> List[Desire]:
        """Return all desires ordered by priority (highest first)."""
        return sorted(self.desires_dict.values(), key=lambda d: d.priority, reverse=True)

    # ------------------------------------------------------------------
    # Intention (plan) management
    # ------------------------------------------------------------------

    def add_intention(self, plan: Plan) -> None:
        """Commit to a new intention."""
        self.intentions.append(plan)
        self.add_to_memory(
            {
                "type": "intention_added",
                "plan_name": plan.name,
                "desire_name": plan.desire_name,
                "actions_count": len(plan.actions),
                "timestamp": datetime.now().isoformat(),
            }
        )

    def set_current_intention(self, plan: Optional[Plan]) -> None:
        """Set the currently active intention."""
        self.current_intention = plan
        if plan:
            self.add_to_memory(
                {
                    "type": "intention_selected",
                    "plan_name": plan.name,
                    "desire_name": plan.desire_name,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            self.add_to_memory({"type": "intention_cleared", "timestamp": datetime.now().isoformat()})

    def get_current_intention(self) -> Optional[Plan]:
        """Return the currently active intention."""
        return self.current_intention

    def get_intentions_for_desire(self, desire_name: str) -> List[Plan]:
        """Return all non-complete intentions targeting the given desire."""
        return [p for p in self.intentions if p.desire_name == desire_name and not p.complete]

    def remove_completed_intentions(self) -> int:
        """Remove all completed intentions and return the count removed."""
        before = len(self.intentions)
        self.intentions = [i for i in self.intentions if not i.complete]
        return before - len(self.intentions)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "beliefs": {n: b.to_dict() for n, b in self.beliefs_dict.items()},
                "desires": {n: d.to_dict() for n, d in self.desires_dict.items()},
                "intentions": [i.to_dict() for i in self.intentions],
                "current_intention": self.current_intention.to_dict()
                if self.current_intention
                else None,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BDIState":
        state = cls()
        if "beliefs" in data:
            for name, bdata in data["beliefs"].items():
                if isinstance(bdata, dict):
                    state.beliefs_dict[name] = Belief.from_dict(bdata)
                else:
                    state.beliefs_dict[name] = Belief(name=name, value=bdata)
        if "desires" in data:
            for name, ddata in data["desires"].items():
                if isinstance(ddata, dict):
                    state.desires_dict[name] = Desire.from_dict(ddata)
        if "intentions" in data:
            state.intentions = [Plan.from_dict(p) for p in data["intentions"]]
        if data.get("current_intention"):
            state.current_intention = Plan.from_dict(data["current_intention"])
        return state


# ---------------------------------------------------------------------------
# BDIAgent
# ---------------------------------------------------------------------------

class BDIAgent(BaseAgent):
    """
    Belief-Desire-Intention (BDI) agent.

    Implements the BDI cognitive architecture, cycling through:
    1. Perceive the environment.
    2. Update beliefs from perceptions.
    3. Deliberate over desires to select an intention.
    4. Execute the next action of the current intention.
    """

    def __init__(
        self, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(agent_id, config)

        # Convenience alias used by some callers.
        self.id = self.agent_id

        self.state = BDIState(capacity=self.config.get("memory_capacity", 1000))
        self.plan_library: Dict[str, Dict[str, Any]] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self.perception_handlers: List[Callable] = []

        self.deliberation_interval: float = self.config.get("deliberation_interval", 5)
        self.commitment_strategy: str = self.config.get("commitment_strategy", "single_minded")

        logger.info("BDI agent %s initialized", self.agent_id)

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def register_action_handler(self, action_type: str, handler: Callable) -> None:
        """Register a callable to handle actions of the given type."""
        self.action_handlers[action_type] = handler
        logger.debug("Registered action handler for type: %s", action_type)

    # ------------------------------------------------------------------
    # BaseAgent interface
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Set up default handlers, load config data, and seed beliefs/desires."""
        logger.info("Initializing BDI agent %s", self.agent_id)
        self._register_default_action_handlers()
        self._register_default_perception_handlers()
        self._load_plans_from_config()
        self._initialize_beliefs()
        self._initialize_desires()
        logger.info("BDI agent %s initialization complete", self.agent_id)

    async def perceive(self) -> Dict[str, Any]:
        """
        Return a perception dict from the environment.

        Subclasses should override this to integrate real sensors or data
        sources.  Sensor readings can also be provided via the
        ``sensor_readings`` key in the agent config for deterministic or
        test deployments.
        """
        perceptions: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
        }
        if "region" in self.config:
            perceptions["region"] = self.config["region"]

        static_readings = self.config.get("sensor_readings")
        if static_readings and isinstance(static_readings, dict):
            perceptions["sensors"] = dict(static_readings)
        else:
            perceptions["sensors"] = {}

        logger.debug("BDI agent %s perceptions: %s", self.agent_id, perceptions)
        return perceptions

    def update_beliefs(self, perception: Dict[str, Any]) -> None:
        """Update beliefs from a perception dict by running all perception handlers."""
        for handler in self.perception_handlers:
            handler(self, perception)
        self.state.update_belief("last_perception_time", datetime.now())
        logger.debug("BDI agent %s beliefs updated from perception", self.agent_id)

    async def decide(self) -> Optional[Dict[str, Any]]:
        """
        Select the next action to perform.

        Continues the current intention when valid, or deliberates to find a
        new one.
        """
        current = self.state.get_current_intention()
        if current and not current.complete and self._is_intention_valid(current):
            action = current.next_action()
            if action:
                logger.debug("BDI agent %s continuing intention %s", self.agent_id, current.name)
                return action

        # Clear stale/invalid intention and deliberate.
        self.state.set_current_intention(None)
        for desire in self.state.get_desires_by_priority():
            if desire.achieved or desire.is_expired():
                continue
            plan = self._find_plan_for_desire(desire.name)
            if plan:
                self.state.set_current_intention(plan)
                action = plan.next_action()
                if action:
                    logger.debug("BDI agent %s selected intention %s", self.agent_id, plan.name)
                    return action

        logger.debug("BDI agent %s found no valid intentions", self.agent_id)
        return None

    async def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the given action using registered handlers."""
        if not action or ("type" not in action and "action_type" not in action):
            logger.warning("BDI agent %s received invalid action: %s", self.agent_id, action)
            return {"success": False, "error": "Invalid action"}

        action_type = action.get("type") or action.get("action_type")
        if action_type not in self.action_handlers:
            logger.warning("BDI agent %s has no handler for action %s", self.agent_id, action_type)
            return {"success": False, "error": f"No handler for action type {action_type}"}

        try:
            result = await self.action_handlers[action_type](self, action)
            current = self.state.get_current_intention()
            if current:
                current.record_action_result(
                    current.current_action_index, result, result.get("success", False)
                )
                if result.get("success", False):
                    current.advance()
                    if current.complete and self._is_desire_satisfied(current.desire_name):
                        desire = self.state.get_desire(current.desire_name)
                        if desire:
                            desire.set_achieved(True)
                            logger.info(
                                "BDI agent %s achieved desire %s", self.agent_id, desire.name
                            )
            return result
        except Exception as exc:
            logger.error(
                "BDI agent %s error executing action %s: %s", self.agent_id, action_type, exc
            )
            return {"success": False, "error": str(exc)}

    async def shutdown(self) -> None:
        """Shut down the agent."""
        logger.info("BDI agent %s shutting down", self.agent_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _register_default_action_handlers(self) -> None:
        self.action_handlers["wait"] = self._handle_wait_action
        self.action_handlers["update_belief"] = self._handle_update_belief_action
        self.action_handlers["query_belief"] = self._handle_query_belief_action
        self.action_handlers["log"] = self._handle_log_action

    def _register_default_perception_handlers(self) -> None:
        self.perception_handlers.append(self._handle_sensor_perceptions)

    def _handle_sensor_perceptions(
        self, agent: "BDIAgent", perception: Dict[str, Any]
    ) -> None:
        if "sensors" in perception:
            for sensor_name, value in perception["sensors"].items():
                agent.state.update_belief(f"sensor.{sensor_name}", value)

    async def _handle_wait_action(
        self, agent: "BDIAgent", action: Dict[str, Any]
    ) -> Dict[str, Any]:
        duration = action.get("duration", 1)
        await asyncio.sleep(duration)
        return {"success": True, "duration": duration}

    async def _handle_update_belief_action(
        self, agent: "BDIAgent", action: Dict[str, Any]
    ) -> Dict[str, Any]:
        belief_name = action.get("belief_name")
        if not belief_name:
            return {"success": False, "error": "Missing belief name"}
        agent.state.update_belief(
            belief_name,
            action.get("belief_value"),
            action.get("confidence"),
            action.get("metadata"),
        )
        return {"success": True, "belief_name": belief_name, "belief_value": action.get("belief_value")}

    async def _handle_query_belief_action(
        self, agent: "BDIAgent", action: Dict[str, Any]
    ) -> Dict[str, Any]:
        belief_name = action.get("belief_name")
        if not belief_name:
            return {"success": False, "error": "Missing belief name"}
        belief = agent.state.get_belief(belief_name)
        if not belief:
            return {"success": False, "error": f"Belief {belief_name} not found"}
        return {
            "success": True,
            "belief_name": belief_name,
            "belief_value": belief.value,
            "confidence": belief.confidence,
            "timestamp": belief.timestamp.isoformat(),
        }

    async def _handle_log_action(
        self, agent: "BDIAgent", action: Dict[str, Any]
    ) -> Dict[str, Any]:
        message = action.get("message", "")
        level = action.get("level", "info")
        log_fn = {
            "debug": logger.debug,
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
        }.get(level, logger.info)
        log_fn("BDI agent %s: %s", agent.agent_id, message)
        return {"success": True, "message": message, "level": level}

    def _load_plans_from_config(self) -> None:
        for template in self.config.get("plans", []):
            if not all(k in template for k in ("name", "desire_name", "actions")):
                logger.warning(
                    "BDI agent %s skipping invalid plan template: %s", self.agent_id, template
                )
                continue
            self.plan_library[template["name"]] = template
        logger.debug(
            "BDI agent %s loaded %d plan templates", self.agent_id, len(self.plan_library)
        )

    def _initialize_beliefs(self) -> None:
        for belief_name, belief_data in self.config.get("initial_beliefs", {}).items():
            if isinstance(belief_data, dict):
                belief = Belief(
                    name=belief_name,
                    value=belief_data.get("value"),
                    confidence=belief_data.get("confidence", 1.0),
                    metadata=belief_data.get("metadata", {}),
                )
                self.state.add_belief(belief)
            else:
                self.state.update_belief(belief_name, belief_data)
        logger.debug(
            "BDI agent %s initialized beliefs from config", self.agent_id
        )

    def _initialize_desires(self) -> None:
        for desire_data in self.config.get("initial_desires", []):
            if "name" not in desire_data or "description" not in desire_data:
                logger.warning(
                    "BDI agent %s skipping invalid desire: %s", self.agent_id, desire_data
                )
                continue
            deadline = None
            if "deadline" in desire_data:
                try:
                    deadline = datetime.fromisoformat(desire_data["deadline"])
                except (ValueError, TypeError):
                    logger.warning(
                        "BDI agent %s invalid deadline format: %s",
                        self.agent_id,
                        desire_data["deadline"],
                    )
            desire = Desire(
                name=desire_data["name"],
                description=desire_data["description"],
                priority=desire_data.get("priority", 0.5),
                deadline=deadline,
                conditions=desire_data.get("conditions", {}),
            )
            self.state.add_desire(desire)
        logger.debug("BDI agent %s initialized desires from config", self.agent_id)

    def _find_plan_for_desire(self, desire_name: str) -> Optional[Plan]:
        """Find or create a plan for the given desire."""
        # Reuse an existing non-complete intention.
        for plan in self.state.get_intentions_for_desire(desire_name):
            if not plan.complete:
                return plan

        # Instantiate from the plan library.
        for plan_name, template in self.plan_library.items():
            if template["desire_name"] != desire_name:
                continue
            if self._check_context_conditions(template.get("context_conditions", {})):
                plan = Plan(
                    name=plan_name,
                    desire_name=desire_name,
                    actions=template["actions"],
                    context_conditions=template.get("context_conditions", {}),
                )
                self.state.add_intention(plan)
                return plan
        return None

    def _check_context_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Return True if every condition matches the corresponding belief value."""
        for belief_name, expected in conditions.items():
            belief = self.state.get_belief(belief_name)
            if not belief or belief.value != expected:
                return False
        return True

    def _is_intention_valid(self, intention: Plan) -> bool:
        """Return True if the intention's desire still exists, is unachieved, and unexpired."""
        desire = self.state.get_desire(intention.desire_name)
        if not desire or desire.achieved or desire.is_expired():
            return False
        return self._check_context_conditions(intention.context_conditions)

    def _is_desire_satisfied(self, desire_name: str) -> bool:
        """Return True if all conditions of the desire match current beliefs."""
        desire = self.state.get_desire(desire_name)
        if not desire:
            return False
        for belief_name, expected in desire.conditions.items():
            belief = self.state.get_belief(belief_name)
            if not belief or belief.value != expected:
                return False
        return True
