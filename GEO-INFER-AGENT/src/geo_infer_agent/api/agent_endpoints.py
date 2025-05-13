#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
REST API endpoints for the GEO-INFER-AGENT system.

This module defines RESTful API endpoints that allow:
- Creating and managing agents
- Retrieving agent state
- Controlling agent execution
- Configuring agent parameters
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Body, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from geo_infer_agent.core.agent_base import BaseAgent
from geo_infer_agent.core.agent_registry import AgentRegistry

logger = logging.getLogger("geo_infer_agent.api.endpoints")

# Define API models
class AgentCreate(BaseModel):
    """Model for creating a new agent."""
    agent_type: str = Field(..., description="Type of agent to create")
    agent_id: Optional[str] = Field(None, description="Custom ID for the agent (auto-generated if not provided)")
    config: Dict[str, Any] = Field({}, description="Agent configuration")
    region: Optional[str] = Field(None, description="Geospatial region for agent operation (GeoJSON)")

class AgentAction(BaseModel):
    """Model for triggering an agent action."""
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field({}, description="Action parameters")

class AgentMessage(BaseModel):
    """Model for agent-to-agent messages."""
    to_agent_id: str = Field(..., description="Target agent ID")
    content: Dict[str, Any] = Field(..., description="Message content")

class AgentResponse(BaseModel):
    """Standard response model for agent operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

# Initialize API
app = FastAPI(
    title="GEO-INFER-AGENT API",
    description="API for managing autonomous geospatial agents",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent registry
agent_registry = AgentRegistry()

@app.get("/agents", response_model=List[Dict[str, Any]], tags=["Agents"])
async def list_agents():
    """List all registered agents."""
    return agent_registry.list_agents()

@app.post("/agents", response_model=AgentResponse, tags=["Agents"])
async def create_agent(agent_data: AgentCreate, background_tasks: BackgroundTasks):
    """Create a new agent."""
    try:
        agent_id = await agent_registry.create_agent(
            agent_type=agent_data.agent_type,
            agent_id=agent_data.agent_id,
            config=agent_data.config,
            region=agent_data.region
        )
        
        # Start agent in background
        background_tasks.add_task(agent_registry.start_agent, agent_id)
        
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} created successfully",
            data={"agent_id": agent_id}
        )
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def get_agent(agent_id: str):
    """Get agent details."""
    try:
        agent_info = agent_registry.get_agent_info(agent_id)
        return AgentResponse(
            success=True,
            message=f"Details for agent {agent_id}",
            data=agent_info
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.delete("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def delete_agent(agent_id: str):
    """Delete an agent."""
    try:
        await agent_registry.stop_agent(agent_id)
        agent_registry.remove_agent(agent_id)
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} deleted successfully",
            data=None
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.post("/agents/{agent_id}/start", response_model=AgentResponse, tags=["Control"])
async def start_agent(agent_id: str, background_tasks: BackgroundTasks):
    """Start an agent."""
    try:
        if agent_registry.is_agent_running(agent_id):
            return AgentResponse(
                success=False,
                message=f"Agent {agent_id} is already running",
                data=None
            )
        
        background_tasks.add_task(agent_registry.start_agent, agent_id)
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} started",
            data=None
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.post("/agents/{agent_id}/stop", response_model=AgentResponse, tags=["Control"])
async def stop_agent(agent_id: str):
    """Stop an agent."""
    try:
        await agent_registry.stop_agent(agent_id)
        return AgentResponse(
            success=True,
            message=f"Agent {agent_id} stopped",
            data=None
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.post("/agents/{agent_id}/action", response_model=AgentResponse, tags=["Control"])
async def agent_action(agent_id: str, action_data: AgentAction):
    """Perform an action on an agent."""
    try:
        result = await agent_registry.agent_action(
            agent_id=agent_id,
            action=action_data.action,
            parameters=action_data.parameters
        )
        return AgentResponse(
            success=True,
            message=f"Action '{action_data.action}' executed on agent {agent_id}",
            data=result
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/{agent_id}/state", response_model=AgentResponse, tags=["State"])
async def get_agent_state(agent_id: str):
    """Get the current state of an agent."""
    try:
        state = await agent_registry.get_agent_state(agent_id)
        return AgentResponse(
            success=True,
            message=f"Current state of agent {agent_id}",
            data=state
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.post("/agents/{agent_id}/message", response_model=AgentResponse, tags=["Communication"])
async def send_message(agent_id: str, message: AgentMessage):
    """Send a message from one agent to another."""
    try:
        success = await agent_registry.send_message(
            from_agent_id=agent_id,
            to_agent_id=message.to_agent_id,
            content=message.content
        )
        return AgentResponse(
            success=success,
            message=f"Message sent from {agent_id} to {message.to_agent_id}" if success else "Failed to send message",
            data=None
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} or {message.to_agent_id} not found")

def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_api_server() 