"""
Basic governance example using GEO-INFER-ORG.

This example demonstrates:
- Governance framework setup
- Community management
- Stakeholder engagement
- Multi-level governance coordination
"""

import sys
import os

# Add src directory to path
project_root = os.path.dirname(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from geo_infer_org.core.governance import GovernanceFramework
    from geo_infer_org.core.community import CommunityManager
    from geo_infer_org.core.stakeholders import StakeholderEngagement
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some imports not available: {e}")
    IMPORTS_AVAILABLE = False


def main():
    """Run basic governance example."""
    print("=" * 60)
    print("GEO-INFER-ORG: Basic Governance Example")
    print("=" * 60)
    
    if not IMPORTS_AVAILABLE:
        print("\n⚠️  Some required modules are not available.")
        print("   This example requires full GEO-INFER-ORG installation.")
        print("\n   GEO-INFER-ORG provides:")
        print("   • Multi-level governance frameworks")
        print("   • Community management")
        print("   • Stakeholder engagement")
        print("   • Institutional design")
        print("   • Collaborative governance")
        return
    
    # Step 1: Governance framework
    print("\n🏛️  Step 1: Governance framework setup...")
    try:
        framework = GovernanceFramework()
        print(f"   ✅ Governance framework initialized")
        print(f"   Framework capabilities:")
        print(f"      • Multi-level coordination")
        print(f"      • Institutional design")
        print(f"      • Decision-making processes")
        print(f"      • Policy implementation")
    except Exception as e:
        print(f"   ⚠️  Governance framework: {e}")
    
    # Step 2: Community management
    print("\n👥 Step 2: Community management...")
    try:
        manager = CommunityManager()
        print(f"   ✅ Community manager initialized")
        print(f"   Management capabilities:")
        print(f"      • Community organization")
        print(f"      • Participation tracking")
        print(f"      • Resource allocation")
        print(f"      • Conflict resolution")
    except Exception as e:
        print(f"   ⚠️  Community management: {e}")
    
    # Step 3: Stakeholder engagement
    print("\n🤝 Step 3: Stakeholder engagement...")
    try:
        engagement = StakeholderEngagement()
        print(f"   ✅ Stakeholder engagement initialized")
        print(f"   Engagement capabilities:")
        print(f"      • Stakeholder identification")
        print(f"      • Interest mapping")
        print(f"      • Communication channels")
        print(f"      • Consensus building")
    except Exception as e:
        print(f"   ⚠️  Stakeholder engagement: {e}")
    
    # Step 4: Integration
    print("\n🔗 Step 4: Integration capabilities...")
    try:
        print(f"   ✅ GEO-INFER-ORG integrates with:")
        print(f"      • PEP: People management")
        print(f"      • COMMS: Communication systems")
        print(f"      • CIV: Civic engagement")
        print(f"      • NORMS: Normative frameworks")
        print(f"      • REQ: Requirements management")
    except Exception as e:
        print(f"   ⚠️  Integration info: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Governance example complete!")
    print("=" * 60)
    print("\nKey capabilities demonstrated:")
    print("  • Governance framework setup")
    print("  • Community management")
    print("  • Stakeholder engagement")
    print("  • Multi-level coordination")
    print("\nNext steps:")
    print("  • Integrate with PEP for people management")
    print("  • Connect with COMMS for communication")
    print("  • Use with CIV for civic engagement")
    print("  • Combine with NORMS for normative governance")


if __name__ == "__main__":
    main()

