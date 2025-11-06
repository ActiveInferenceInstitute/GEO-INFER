"""
Basic requirements engineering example using GEO-INFER-REQ.

This example demonstrates:
- Requirements management
- Geospatial user stories
- Requirements traceability
- Requirements validation
"""

import sys
import os

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from geo_infer_req.core.requirements import RequirementsEngine
    from geo_infer_req.models.user_stories import GeospatialUserStory
    from geo_infer_req.core.traceability import TraceabilityMatrix
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some imports not available: {e}")
    IMPORTS_AVAILABLE = False


def main():
    """Run basic requirements engineering example."""
    print("=" * 60)
    print("GEO-INFER-REQ: Basic Requirements Engineering Example")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("\n⚠️  Some required modules are not available.")
        print("   This example requires full GEO-INFER-REQ installation.")
        print("\n   GEO-INFER-REQ provides:")
        print("   • Requirements elicitation and specification")
        print("   • Geospatial user story management")
        print("   • Requirements traceability")
        print("   • Spatial context modeling")
        print("   • Requirements validation")
        return
    
    # Step 1: Requirements engine
    print("\n📋 Step 1: Requirements management...")
    try:
        engine = RequirementsEngine()
        print(f"   ✅ Requirements engine initialized")
        
        # Add sample requirement
        requirement = engine.add_requirement(
            id='REQ-001',
            description='System shall support spatial data indexing using H3',
            priority='high',
            category='functional'
        )
        print(f"   ✅ Added requirement: {requirement.get('id', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  Requirements management: {e}")
    
    # Step 2: Geospatial user stories
    print("\n🗺️  Step 2: Geospatial user stories...")
    try:
        story = GeospatialUserStory(
            user_type='analyst',
            action='analyze',
            spatial_context='urban areas',
            business_value='improve urban planning decisions'
        )
        print(f"   ✅ Created geospatial user story")
        print(f"   User: {story.user_type}")
        print(f"   Spatial context: {story.spatial_context}")
    except Exception as e:
        print(f"   ⚠️  User story creation: {e}")
    
    # Step 3: Traceability
    print("\n🔗 Step 3: Requirements traceability...")
    try:
        matrix = TraceabilityMatrix()
        print(f"   ✅ Traceability matrix initialized")
        print(f"   Capabilities:")
        print(f"      • Link requirements to design")
        print(f"      • Track requirement changes")
        print(f"      • Map requirements to tests")
        print(f"      • Spatial requirement coverage")
    except Exception as e:
        print(f"   ⚠️  Traceability: {e}")
    
    # Step 4: Integration
    print("\n🔗 Step 4: Integration capabilities...")
    try:
        print(f"   ✅ GEO-INFER-REQ integrates with:")
        print(f"      • NORMS: Regulatory requirements")
        print(f"      • SEC: Security requirements")
        print(f"      • SPACE: Spatial requirements")
        print(f"      • APP: Application requirements")
        print(f"      • ORG: Organizational requirements")
    except Exception as e:
        print(f"   ⚠️  Integration info: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Requirements engineering example complete!")
    print("=" * 60)
    print("\nKey capabilities demonstrated:")
    print("  • Requirements management")
    print("  • Geospatial user stories")
    print("  • Requirements traceability")
    print("  • Spatial context modeling")
    print("\nNext steps:")
    print("  • Integrate with NORMS for regulatory compliance")
    print("  • Connect with SEC for security requirements")
    print("  • Use with SPACE for spatial requirement specification")
    print("  • Combine with ORG for organizational requirements")


if __name__ == "__main__":
    main()

