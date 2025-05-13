#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for GEO-INFER-AGENT

This module provides a command-line interface for interacting with
the GEO-INFER-AGENT autonomous agent functionality.
"""

import os
import sys
import argparse
import logging
import yaml
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib

from geo_infer_agent.core.agent_base import BaseAgent

# Configure logger
logger = logging.getLogger("geo_infer_agent.cli")

def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the CLI.
    
    Args:
        verbose: Whether to use verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce verbosity of some modules
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
        
    try:
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(f)
            elif config_path.endswith('.json'):
                config = json.load(f)
            else:
                logger.error(f"Unsupported file format: {config_path}")
                sys.exit(1)
                
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        sys.exit(1)

def load_agent_class(agent_type: str) -> type:
    """
    Dynamically load agent class based on type.
    
    Args:
        agent_type: Type of agent to load
        
    Returns:
        Agent class
    """
    # Map of agent types to module paths
    agent_modules = {
        "default": "geo_infer_agent.core.agent_base.ExampleAgent",
        "data_collector": "geo_infer_agent.agents.data_collector.DataCollectorAgent",
        "analyzer": "geo_infer_agent.agents.analyzer.AnalyzerAgent",
        "monitor": "geo_infer_agent.agents.monitor.MonitorAgent",
        "decision": "geo_infer_agent.agents.decision.DecisionAgent",
        "coordinator": "geo_infer_agent.agents.coordinator.CoordinatorAgent",
        "learner": "geo_infer_agent.agents.learner.LearnerAgent",
        # Add more agent types as needed
    }
    
    if agent_type not in agent_modules:
        logger.error(f"Unknown agent type: {agent_type}")
        logger.info(f"Available agent types: {', '.join(agent_modules.keys())}")
        sys.exit(1)
    
    try:
        # Split module path and class name
        module_path, class_name = agent_modules[agent_type].rsplit(".", 1)
        
        # Import module
        module = importlib.import_module(module_path)
        
        # Get class
        agent_class = getattr(module, class_name)
        
        return agent_class
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load agent class for type '{agent_type}': {str(e)}")
        logger.error("Make sure the required agent modules are installed")
        sys.exit(1)

async def run_agent(args: argparse.Namespace) -> None:
    """
    Run an agent instance.
    
    Args:
        args: Command-line arguments
    """
    # Load configuration
    config_path = args.config
    if not config_path:
        logger.error("No configuration file specified")
        sys.exit(1)
        
    config = load_config(config_path)
    
    # Determine agent type
    agent_type = args.type or config.get("agent_type", "default")
    
    # Load agent class
    agent_class = load_agent_class(agent_type)
    
    try:
        # Create agent instance
        agent = agent_class(agent_id=args.id, config=config)
        
        # If state file provided, load state
        if args.state:
            if os.path.exists(args.state):
                agent = agent_class.load_state(args.state, config=config)
                logger.info(f"Loaded agent state from {args.state}")
            else:
                logger.warning(f"State file not found: {args.state}")
        
        # Run agent
        logger.info(f"Starting agent {agent.agent_id} of type {agent_type}")
        await agent.run()
        
        # Save state if requested
        if args.save_state:
            state_path = agent.save_state(args.save_state)
            logger.info(f"Saved agent state to {state_path}")
            
    except KeyboardInterrupt:
        logger.info("Agent execution interrupted")
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}", exc_info=True)
        sys.exit(1)

def list_agents_command(args: argparse.Namespace) -> None:
    """
    List available agent types.
    
    Args:
        args: Command-line arguments
    """
    # List of available agent types and descriptions
    agents = {
        "default": "Basic example agent for testing",
        "data_collector": "Collects data from various sources",
        "analyzer": "Analyzes data using various models",
        "monitor": "Monitors areas for changes or events",
        "decision": "Makes decisions based on analysis",
        "coordinator": "Coordinates multiple other agents",
        "learner": "Learns from environment and other agents",
    }
    
    print("Available Agent Types:\n")
    for agent_type, description in agents.items():
        print(f"  {agent_type:15s} - {description}")
    
    print("\nUse with: geo-infer-agent run --type <agent_type>")

def create_config_command(args: argparse.Namespace) -> None:
    """
    Create a configuration file template.
    
    Args:
        args: Command-line arguments
    """
    # Define the output path
    output_path = args.output or "agent_config.yaml"
    
    # Check if file already exists
    if os.path.exists(output_path) and not args.force:
        logger.error(f"File already exists: {output_path}. Use --force to overwrite.")
        sys.exit(1)
    
    # Determine which agent type to create config for
    agent_type = args.type or "default"
    
    # Load template configs
    template_path = os.path.join(os.path.dirname(__file__), "config", "templates", f"{agent_type}.yaml")
    if not os.path.exists(template_path):
        # Fallback to example config
        template_path = os.path.join(os.path.dirname(__file__), "config", "example.yaml")
        
    try:
        with open(template_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Customize config
        if agent_type != "default":
            config["agent_type"] = agent_type
            
        # Write config to file
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
        logger.info(f"Created configuration template at {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to create configuration file: {str(e)}")
        sys.exit(1)

def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="GEO-INFER-AGENT - Autonomous agent framework for geospatial applications",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run an agent')
    run_parser.add_argument('--config', '-c', required=True, help='Path to configuration file')
    run_parser.add_argument('--type', '-t', help='Agent type to run')
    run_parser.add_argument('--id', help='Agent ID (generated if not provided)')
    run_parser.add_argument('--state', '-s', help='Path to state file to load')
    run_parser.add_argument('--save-state', help='Path to save state after execution')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available agent types')
    
    # Create-config command
    config_parser = subparsers.add_parser('create-config', help='Create a configuration template')
    config_parser.add_argument('--type', '-t', help='Agent type to create config for')
    config_parser.add_argument('--output', '-o', help='Output file path')
    config_parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle commands
    if args.command == 'run':
        asyncio.run(run_agent(args))
    elif args.command == 'list':
        list_agents_command(args)
    elif args.command == 'create-config':
        create_config_command(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 