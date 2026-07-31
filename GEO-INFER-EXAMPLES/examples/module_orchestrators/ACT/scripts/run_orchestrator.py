#!/usr/bin/env python3
"""
ACT Module Orchestrator - GEO-INFER Examples
Demonstrates: Active Inference

Thin orchestrator pattern: Focuses on orchestration structure and patterns,
not detailed module implementations.
"""

import sys
import time
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
import numpy as np

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'src'))

def setup_logging():
    """Configure logging for the orchestrator."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('act_orchestrator')

class ACTOrchestrator:
    """Thin orchestrator for GEO-INFER-ACT module demonstrations."""
    
    def __init__(self, config_path=None):
        """Initialize the ACT orchestrator."""
        self.logger = setup_logging()
        self.config = self._load_config(config_path)
        np.random.seed(42)  # Reproducible results
        self.module_name = 'ACT'
        self.dependencies = ['MATH', 'BAYES']
    
    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'orchestrator_config.yaml'
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return {'operations': {'sample_size': 10}}
    
    def run_orchestrator(self, output_dir: Optional[Any] = None):
        """Run the complete ACT module demonstration.

        Args:
            output_dir: Optional override for the results output directory.
                Accepts a path-like object. When omitted, results are written
                to the bundled ``output/`` directory next to this script so
                tests can redirect to a clean temporary location.
        """
        self.logger.info("🚀 Starting ACT Module Orchestrator (Thin)")
        self.logger.info("Demonstrating: Active Inference")
        
        start_time = time.time()
        results = {
            'module': 'ACT',
            'timestamp': datetime.now().isoformat(),
            'orchestrator_type': 'thin',
            'operations': {}
        }
        
        try:
            # Operation 1: Module Initialization
            self.logger.info("\n🔧 OPERATION 1: Module Initialization")
            init_results = self._demonstrate_initialization()
            results['operations']['initialization'] = init_results
            self.logger.info("✅ Module initialization orchestrated")
            
            # Operation 2: Core Operations
            self.logger.info("\n⚙️ OPERATION 2: Core Operations")
            core_results = self._demonstrate_core_operations()
            results['operations']['core'] = core_results
            self.logger.info("✅ Core operations orchestrated")
            
            # Operation 3: Dependency Integration
            self.logger.info("\n🔗 OPERATION 3: Dependency Integration")
            integration_results = self._demonstrate_integration()
            results['operations']['integration'] = integration_results
            self.logger.info("✅ Integration orchestrated")
            
            # Operation 4: Error Handling
            self.logger.info("\n🛡️ OPERATION 4: Error Handling")
            error_results = self._demonstrate_error_handling()
            results['operations']['error_handling'] = error_results
            self.logger.info("✅ Error handling orchestrated")
            
            # Operation 5: Workflow Demonstration
            self.logger.info("\n🔄 OPERATION 5: Complete Workflow")
            workflow_results = self._demonstrate_workflow()
            results['operations']['workflow'] = workflow_results
            self.logger.info("✅ Workflow orchestrated")
            
            execution_time = time.time() - start_time
            results['execution_metadata'] = {
                'execution_time_seconds': execution_time,
                'operations_completed': len(results['operations']),
                'status': 'success',
                'orchestrator_type': 'thin'
            }
            
            self._display_summary(results, execution_time)
            self._save_results(results, output_dir=output_dir)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Orchestrator failed: {e}", exc_info=True)
            results['execution_metadata'] = {
                'status': 'error',
                'error': str(e)
            }
            self._save_results(results, output_dir=output_dir)
            raise
    
    def _demonstrate_initialization(self):
        """Demonstrate module initialization orchestration."""
        return {
            'module': 'ACT',
            'status': 'initialized',
            'config_loaded': True,
            'orchestration_note': 'Thin orchestrator - demonstrates initialization pattern'
        }
    
    def _demonstrate_core_operations(self):
        """Demonstrate core module operations orchestration."""
        # Thin orchestrator: demonstrate operation structure, not implementation
        operations = ['operation_1', 'operation_2', 'operation_3']
        return {
            'operations': operations,
            'orchestration_note': 'Thin orchestrator - demonstrates operation orchestration pattern',
            'note': 'Actual module operations would be called here in production'
        }
    
    def _demonstrate_integration(self):
        """Demonstrate integration with dependencies."""
        deps = ['MATH', 'BAYES']
        return {
            'dependencies': deps if deps != ['All modules'] else 'all_modules',
            'integration_status': 'orchestrated',
            'orchestration_note': 'Thin orchestrator - demonstrates dependency integration pattern',
            'note': 'Actual dependency modules would be integrated here in production'
        }
    
    def _demonstrate_error_handling(self):
        """Demonstrate error handling orchestration."""
        return {
            'error_handling': 'orchestrated',
            'validation': 'pattern_demonstrated',
            'orchestration_note': 'Thin orchestrator - demonstrates error handling pattern',
            'note': 'Actual error handling would be implemented here in production'
        }
    
    def _demonstrate_workflow(self):
        """Demonstrate complete workflow orchestration."""
        workflow_steps = [
            'initialization',
            'core_operations',
            'dependency_integration',
            'error_handling',
            'workflow_completion'
        ]
        return {
            'workflow': 'orchestrated',
            'steps': workflow_steps,
            'orchestration_note': 'Thin orchestrator - demonstrates workflow orchestration pattern',
            'note': 'Actual workflow would be executed here in production'
        }
    
    def _display_summary(self, results, execution_time):
        """Display results summary."""
        print("\n" + "="*70)
        print(f"🎯 ACT MODULE ORCHESTRATOR RESULTS (Thin)")
        print("="*70)
        
        print(f"\n📊 Operations Orchestrated:")
        for op_name, op_data in results['operations'].items():
            print(f"  ✅ {op_name}: orchestrated")
        
        print(f"\n⚡ Performance:")
        print(f"  ├─ Execution Time: {execution_time:.2f} seconds")
        print(f"  ├─ Module: GEO-INFER-ACT")
        print(f"  ├─ Orchestrator Type: Thin (orchestration patterns)")
        print(f"  └─ Status: {results['execution_metadata']['status']}")
        
        print(f"\n💡 Orchestration Patterns Demonstrated:")
        print(f"  ├─ Module Initialization Pattern")
        print(f"  ├─ Core Operations Pattern")
        print(f"  ├─ Dependency Integration Pattern")
        print(f"  ├─ Error Handling Pattern")
        print(f"  └─ Complete Workflow Pattern")
        
        if self.dependencies:
            print(f"\n🔗 Dependencies: {', '.join(self.dependencies)}")
        
        print(f"\n✨ ACT thin orchestrator demonstration complete!")
        print("📝 Note: This is a thin orchestrator focusing on orchestration patterns")
        print("🚀 For detailed implementations, see module-specific examples")
        print("="*70)
    
    def _save_results(self, results, output_dir: Optional[Any] = None):
        """Save results to JSON file and write a deterministic manifest receipt.

        The manifest follows the GEO-INFER deterministic visualization receipt
        pattern (input hash, H3 version metadata, artifact checks, accessibility
        checks) so the orchestrator output is auditable alongside SPACE/PLACE
        dashboards.

        Args:
            results: Results dictionary to serialize.
            output_dir: Optional output directory override (path-like). Defaults
                to the bundled ``output/`` directory next to this script.
        """
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'output'
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'act_orchestrator_results_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        self._write_manifest_receipt(output_file, results)
        self.logger.info(f"📁 Results saved to: {output_file.name}")

    @staticmethod
    def _write_manifest_receipt(artifact_path: Path, input_payload: dict) -> Path:
        """Write a deterministic manifest JSON next to ``artifact_path``.

        Mirrors the SPACE ``InteractiveVisualizationEngine`` receipt schema so
        ACT outputs are auditable in the same way as geospatial dashboards.
        Records the input hash, installed H3 version (environment metadata),
        artifact checks, and JSON accessibility checks.
        """
        try:
            import h3 as _h3
            h3_version = _h3.__version__
        except Exception:
            h3_version = None

        input_digest = hashlib.sha256(
            json.dumps(input_payload, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()

        try:
            json.loads(artifact_path.read_text(encoding='utf-8'))
            valid_json = True
        except Exception:
            valid_json = False

        manifest = {
            'schema_version': 'geo-infer-act-orchestrator/v1',
            'generated_at': datetime.now().isoformat(),
            'input_sha256': input_digest,
            'h3_version': h3_version,
            'artifacts': [
                {
                    'path': artifact_path.name,
                    'bytes': artifact_path.stat().st_size,
                }
            ],
            'accessibility': {
                'nonempty': artifact_path.stat().st_size > 0,
                'valid_json': valid_json,
            },
        }
        manifest_path = artifact_path.with_suffix('.manifest.json')
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + '\n', encoding='utf-8'
        )
        return manifest_path

def main():
    """Main function."""
    print(f"🌟 GEO-INFER-ACT Module Orchestrator (Thin)")
    print(f"Demonstrating: Active Inference")
    print("Orchestrator Type: Thin (focuses on orchestration patterns)")
    
    try:
        config_path = Path(__file__).parent.parent / 'config' / 'orchestrator_config.yaml'
        orchestrator = ACTOrchestrator(config_path=config_path)
        orchestrator.run_orchestrator()
        return 0
    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
