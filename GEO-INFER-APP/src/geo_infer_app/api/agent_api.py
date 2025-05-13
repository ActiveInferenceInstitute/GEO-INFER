#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GEO-INFER-APP Agent API

This module provides integration with GEO-INFER-AGENT,
allowing the application to create, manage, and interact with 
intelligent agents.
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

class AgentAPIClient:
    """
    Client for interacting with GEO-INFER-AGENT.
    
    Provides methods for creating, managing, and communicating with
    intelligent agents from within the GEO-INFER-APP.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Agent API client.
        
        Args:
            config: Configuration options for the API client
        """
        self.config = config or {}
        self.base_url = self.config.get("base_url", "http://localhost:8000/api/agents")
        self.agents = {}
        self.agent_status_callbacks = {}
        self._status_monitoring_task = None
    
    async def initialize(self) -> None:
        """Initialize the API client and connect to agent service."""
        logger.info("Initializing Agent API client")
        
        # Start status monitoring task
        self._status_monitoring_task = asyncio.create_task(self._monitor_agent_status())
        
        # Load any persisted agent configurations
        await self._load_saved_agents()
    
    async def shutdown(self) -> None:
        """Clean up resources when shutting down."""
        logger.info("Shutting down Agent API client")
        
        # Cancel status monitoring task
        if self._status_monitoring_task:
            self._status_monitoring_task.cancel()
            try:
                await self._status_monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Save agent configurations
        await self._save_agents()
    
    async def create_agent(self, agent_type: str, config: Dict[str, Any]) -> str:
        """
        Create a new agent.
        
        Args:
            agent_type: Type of agent to create (bdi, active_inference, rl, rule_based, hybrid)
            config: Agent configuration
            
        Returns:
            ID of the created agent
        """
        logger.info(f"Creating agent of type: {agent_type}")
        
        # In a real implementation, this would make an API call to the agent service
        agent_id = f"{agent_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store agent info
        self.agents[agent_id] = {
            "id": agent_id,
            "type": agent_type,
            "config": config,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
        
        return agent_id
    
    async def start_agent(self, agent_id: str) -> bool:
        """
        Start an agent.
        
        Args:
            agent_id: ID of agent to start
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        logger.info(f"Starting agent: {agent_id}")
        
        # Update agent status
        self.agents[agent_id]["status"] = "running"
        self.agents[agent_id]["last_update"] = datetime.now().isoformat()
        
        # Notify status callbacks
        await self._notify_status_change(agent_id, "running")
        
        return True
    
    async def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent.
        
        Args:
            agent_id: ID of agent to stop
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        logger.info(f"Stopping agent: {agent_id}")
        
        # Update agent status
        self.agents[agent_id]["status"] = "stopped"
        self.agents[agent_id]["last_update"] = datetime.now().isoformat()
        
        # Notify status callbacks
        await self._notify_status_change(agent_id, "stopped")
        
        return True
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of agent to delete
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        logger.info(f"Deleting agent: {agent_id}")
        
        # Notify status callbacks
        await self._notify_status_change(agent_id, "deleted")
        
        # Remove agent
        del self.agents[agent_id]
        
        return True
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an agent.
        
        Args:
            agent_id: ID of agent
            
        Returns:
            Status information or None if agent not found
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return None
        
        agent_info = self.agents[agent_id].copy()
        
        # In a real implementation, this would make an API call to get up-to-date status
        
        return agent_info
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents.
        
        Returns:
            List of agent information dictionaries
        """
        return list(self.agents.values())
    
    async def send_command(self, agent_id: str, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a command to an agent.
        
        Args:
            agent_id: ID of agent
            command: Command to send
            
        Returns:
            Command result or None if failed
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return None
        
        if self.agents[agent_id]["status"] != "running":
            logger.error(f"Agent not running: {agent_id}")
            return None
        
        logger.info(f"Sending command to agent {agent_id}: {command.get('command_type', 'unknown')}")
        
        # In a real implementation, this would make an API call to send the command
        
        # Mock response
        result = {
            "status": "success",
            "command_id": command.get("command_id", "unknown"),
            "result": "Command processed",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    async def get_agent_metrics(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for an agent.
        
        Args:
            agent_id: ID of agent
            
        Returns:
            Metrics or None if agent not found
        """
        if agent_id not in self.agents:
            logger.error(f"Agent not found: {agent_id}")
            return None
        
        logger.info(f"Getting metrics for agent: {agent_id}")
        
        # In a real implementation, this would make an API call to get metrics
        
        # Mock metrics
        metrics = {
            "decision_count": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "uptime": 0
        }
        
        return metrics
    
    def register_status_callback(self, agent_id: str, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback for agent status changes.
        
        Args:
            agent_id: ID of agent to monitor
            callback: Function to call when status changes (agent_id, status)
        """
        if agent_id not in self.agent_status_callbacks:
            self.agent_status_callbacks[agent_id] = []
            
        self.agent_status_callbacks[agent_id].append(callback)
    
    def unregister_status_callback(self, agent_id: str, callback: Callable[[str, str], None]) -> bool:
        """
        Unregister a status callback.
        
        Args:
            agent_id: ID of agent
            callback: Callback to remove
            
        Returns:
            True if callback was removed, False otherwise
        """
        if agent_id not in self.agent_status_callbacks:
            return False
            
        try:
            self.agent_status_callbacks[agent_id].remove(callback)
            return True
        except ValueError:
            return False
    
    async def _notify_status_change(self, agent_id: str, status: str) -> None:
        """
        Notify all registered callbacks of a status change.
        
        Args:
            agent_id: ID of agent
            status: New status
        """
        if agent_id in self.agent_status_callbacks:
            for callback in self.agent_status_callbacks[agent_id]:
                try:
                    callback(agent_id, status)
                except Exception as e:
                    logger.error(f"Error in status callback: {e}")
    
    async def _monitor_agent_status(self) -> None:
        """Periodically check status of all agents."""
        try:
            while True:
                # In a real implementation, this would poll the agent service
                # for status updates
                
                await asyncio.sleep(5)  # Check every 5 seconds
        except asyncio.CancelledError:
            logger.info("Agent status monitoring task cancelled")
            raise
    
    async def _load_saved_agents(self) -> None:
        """Load saved agent configurations."""
        config_path = self.config.get("agents_config_path", "agent_configs.json")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.agents = json.load(f)
                logger.info(f"Loaded {len(self.agents)} agent configurations")
        except Exception as e:
            logger.error(f"Error loading agent configurations: {e}")
    
    async def _save_agents(self) -> None:
        """Save agent configurations."""
        config_path = self.config.get("agents_config_path", "agent_configs.json")
        
        try:
            with open(config_path, 'w') as f:
                json.dump(self.agents, f, indent=2)
            logger.info(f"Saved {len(self.agents)} agent configurations")
        except Exception as e:
            logger.error(f"Error saving agent configurations: {e}")


class AgentManager:
    """
    High-level manager for agents in the application.
    
    Provides a simplified interface for working with agents
    and manages agent lifecycle in the application context.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent manager.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.api_client = AgentAPIClient(config.get("api_config"))
        self.active_agents = set()
    
    async def initialize(self) -> None:
        """Initialize the agent manager."""
        await self.api_client.initialize()
        
        # Auto-start agents if configured
        if self.config.get("auto_start_agents", False):
            await self._start_saved_agents()
    
    async def shutdown(self) -> None:
        """Clean up resources when shutting down."""
        # Stop all active agents
        for agent_id in list(self.active_agents):
            await self.stop_agent(agent_id)
            
        await self.api_client.shutdown()
    
    async def create_agent(self, agent_type: str, name: str, config: Dict[str, Any]) -> str:
        """
        Create a new agent with the given configuration.
        
        Args:
            agent_type: Type of agent to create
            name: Human-readable name for the agent
            config: Agent configuration
            
        Returns:
            ID of the created agent
        """
        # Add name to config
        config["name"] = name
        
        # Create agent
        agent_id = await self.api_client.create_agent(agent_type, config)
        
        return agent_id
    
    async def start_agent(self, agent_id: str) -> bool:
        """
        Start an agent.
        
        Args:
            agent_id: ID of agent to start
            
        Returns:
            True if successful, False otherwise
        """
        success = await self.api_client.start_agent(agent_id)
        
        if success:
            self.active_agents.add(agent_id)
            
        return success
    
    async def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent.
        
        Args:
            agent_id: ID of agent to stop
            
        Returns:
            True if successful, False otherwise
        """
        success = await self.api_client.stop_agent(agent_id)
        
        if success and agent_id in self.active_agents:
            self.active_agents.remove(agent_id)
            
        return success
    
    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: ID of agent to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Stop agent if running
        if agent_id in self.active_agents:
            await self.stop_agent(agent_id)
            
        success = await self.api_client.delete_agent(agent_id)
        
        return success
    
    async def send_command(self, agent_id: str, command_type: str, 
                         parameters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Send a command to an agent.
        
        Args:
            agent_id: ID of agent
            command_type: Type of command to send
            parameters: Command parameters
            
        Returns:
            Command result or None if failed
        """
        command = {
            "command_type": command_type,
            "command_id": f"cmd_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "parameters": parameters or {}
        }
        
        return await self.api_client.send_command(agent_id, command)
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an agent.
        
        Args:
            agent_id: ID of agent
            
        Returns:
            Agent information or None if not found
        """
        return await self.api_client.get_agent_status(agent_id)
    
    async def list_agents(self, 
                        filter_type: Optional[str] = None, 
                        active_only: bool = False) -> List[Dict[str, Any]]:
        """
        List agents, optionally filtered.
        
        Args:
            filter_type: Filter by agent type
            active_only: Only include active agents
            
        Returns:
            List of agent information dictionaries
        """
        agents = await self.api_client.list_agents()
        
        # Apply filters
        if active_only:
            agents = [a for a in agents if a["id"] in self.active_agents]
            
        if filter_type:
            agents = [a for a in agents if a["type"] == filter_type]
            
        return agents
    
    async def get_agent_metrics(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for an agent.
        
        Args:
            agent_id: ID of agent
            
        Returns:
            Metrics or None if agent not found
        """
        return await self.api_client.get_agent_metrics(agent_id)
    
    def register_status_callback(self, agent_id: str, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback for agent status changes.
        
        Args:
            agent_id: ID of agent to monitor
            callback: Function to call when status changes
        """
        self.api_client.register_status_callback(agent_id, callback)
    
    def unregister_status_callback(self, agent_id: str, callback: Callable[[str, str], None]) -> bool:
        """
        Unregister a status callback.
        
        Args:
            agent_id: ID of agent
            callback: Callback to remove
            
        Returns:
            True if callback was removed, False otherwise
        """
        return self.api_client.unregister_status_callback(agent_id, callback)
    
    async def _start_saved_agents(self) -> None:
        """Start all previously saved agents marked as active."""
        agents = await self.api_client.list_agents()
        
        for agent in agents:
            if agent.get("status") == "running":
                agent_id = agent["id"]
                await self.start_agent(agent_id) 