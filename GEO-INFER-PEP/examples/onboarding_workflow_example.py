"""
Complete Employee Onboarding Workflow Example

This example demonstrates the complete employee onboarding process using GEO-INFER-PEP:
1. Import candidate data from talent acquisition
2. Process employee onboarding workflow
3. Generate comprehensive reports
4. Display workflow results and analytics

This showcases the integration between different PEP modules (Talent, HR, CRM).

Prerequisites:
- CSV files with candidate and job requisition data
- The geo_infer_pep module installed
"""

import os
import tempfile
import csv
from datetime import datetime
from pathlib import Path
from geo_infer_pep.methods import (
    import_talent_data_from_csv,
    process_employee_onboarding_workflow,
    generate_comprehensive_hr_dashboard,
    generate_comprehensive_talent_dashboard,
    clear_all_data,
    get_all_employees,
    get_all_candidates
)
from geo_infer_pep.models.talent_models import CandidateStatus, Offer

def create_sample_talent_data():
    """Create sample talent data files for demonstration."""
    temp_dir = tempfile.gettempdir()

    # Create candidates CSV
    candidates_data = [
        ['candidate_id', 'first_name', 'last_name', 'email', 'phone_number', 'linkedin_profile',
         'applied_at', 'status', 'job_requisition_id', 'current_company', 'current_title', 'skills'],
        ['cand001', 'Sarah', 'Johnson', 'sarah.johnson@email.com', '555-1001', 'linkedin.com/in/sarahjohnson',
         '2023-12-01T09:00:00', 'offer_accepted', 'req001', 'Tech Solutions Inc', 'Senior Developer', 'python,javascript,react'],
        ['cand002', 'Michael', 'Chen', 'michael.chen@email.com', '555-1002', 'linkedin.com/in/michaelchen',
         '2023-12-05T14:30:00', 'interviewing', 'req002', 'Data Corp', 'Data Scientist', 'python,r,sql,machine learning'],
        ['cand003', 'Emily', 'Rodriguez', 'emily.rodriguez@email.com', '555-1003', 'linkedin.com/in/emilyrodriguez',
         '2023-11-28T11:15:00', 'offer_accepted', 'req001', 'StartupXYZ', 'Full Stack Developer', 'nodejs,react,python,docker'],
        ['cand004', 'David', 'Williams', 'david.williams@email.com', '555-1004', 'linkedin.com/in/davidwilliams',
         '2023-12-08T16:45:00', 'applied', 'req003', 'Enterprise Ltd', 'Product Manager', 'agile,scrum,product management']
    ]

    candidates_csv = os.path.join(temp_dir, 'sample_candidates.csv')
    with open(candidates_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(candidates_data)

    # Create requisitions CSV
    requisitions_data = [
        ['requisition_id', 'job_title', 'department', 'location', 'status', 'opened_at', 'closed_at', 'hiring_manager_id'],
        ['req001', 'Senior Full Stack Developer', 'Engineering', 'San Francisco, CA', 'open', '2023-11-15', '', 'emp001'],
        ['req002', 'Data Scientist', 'Data Science', 'Remote', 'open', '2023-11-20', '', 'emp002'],
        ['req003', 'Product Manager', 'Product', 'New York, NY', 'open', '2023-12-01', '', 'emp003']
    ]

    requisitions_csv = os.path.join(temp_dir, 'sample_requisitions.csv')
    with open(requisitions_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(requisitions_data)

    return candidates_csv, requisitions_csv

def demonstrate_onboarding_workflow():
    """Demonstrate the complete onboarding workflow."""
    print("\n🔄 Step 3: Demonstrating Onboarding Workflows...")

    # Get candidates who are ready for onboarding (offer accepted)
    candidates = get_all_candidates()
    offer_accepted_candidates = [c for c in candidates if c.status == CandidateStatus.OFFER_ACCEPTED]

    print(f"Found {len(offer_accepted_candidates)} candidates ready for onboarding:")

    successful_onboardings = 0
    failed_onboardings = 0

    for candidate in offer_accepted_candidates:
        print(f"\n🎯 Processing onboarding for: {candidate.first_name} {candidate.last_name} ({candidate.candidate_id})")

        # Prepare employee data for onboarding
        employee_data = {
            "candidate_id": candidate.candidate_id,
            "name": f"{candidate.first_name} {candidate.last_name}"
        }

        try:
            # Process the onboarding workflow
            success = process_employee_onboarding_workflow(employee_data)

            if success:
                successful_onboardings += 1
                print(f"✅ Onboarding completed successfully for {candidate.first_name}")
            else:
                failed_onboardings += 1
                print(f"❌ Onboarding failed for {candidate.first_name}")

        except Exception as e:
            failed_onboardings += 1
            print(f"❌ Onboarding error for {candidate.first_name}: {str(e)}")

    print("
📊 Onboarding Results:"    print(f"  - Successful: {successful_onboardings}")
    print(f"  - Failed: {failed_onboardings}")

    return successful_onboardings, failed_onboardings

def main():
    """Main example function demonstrating complete onboarding workflow."""
    print("🚀 GEO-INFER-PEP Complete Onboarding Workflow Example")
    print("=" * 60)

    # Step 1: Create and import talent data
    print("\n📊 Step 1: Creating and importing talent data...")
    candidates_csv, requisitions_csv = create_sample_talent_data()
    print(f"Created sample data files:")
    print(f"  - Candidates: {candidates_csv}")
    print(f"  - Requisitions: {requisitions_csv}")

    # Import talent data
    try:
        talent_result = import_talent_data_from_csv(candidates_csv, requisitions_csv)
        print(f"✅ Successfully imported talent data: {talent_result}")
    except Exception as e:
        print(f"❌ Error importing talent data: {str(e)}")
        return

    # Step 2: Display initial talent dashboard
    print("\n📈 Step 2: Initial Talent Dashboard...")
    try:
        talent_dashboard = generate_comprehensive_talent_dashboard()

        if "message" not in talent_dashboard:
            print("📊 Talent Metrics:"            print(f"  - Total Candidates: {talent_dashboard.get('total_candidates', 0)}")

            status_breakdown = talent_dashboard.get('status_breakdown', {})
            print("\n📋 Candidate Status Breakdown:")
            for status, count in status_breakdown.items():
                print(f"  - {status.title()}: {count} candidates")
        else:
            print(f"⚠️  {talent_dashboard['message']}")

    except Exception as e:
        print(f"❌ Error generating talent dashboard: {str(e)}")

    # Step 3: Process onboarding workflows
    successful, failed = demonstrate_onboarding_workflow()

    # Step 4: Display HR dashboard after onboarding
    print("\n📈 Step 4: HR Dashboard After Onboarding...")
    try:
        hr_dashboard = generate_comprehensive_hr_dashboard()

        if "message" not in hr_dashboard:
            print("🏢 HR Metrics After Onboarding:"            print(f"  - Total Employees: {hr_dashboard.get('total_employees', 0)}")
            print(f"  - Active Employees: {hr_dashboard.get('active_employees', 0)}")

            dept_breakdown = hr_dashboard.get('headcount_by_department', {})
            if dept_breakdown:
                print("\n🏢 Department Breakdown:")
                for dept, count in dept_breakdown.items():
                    print(f"  - {dept}: {count} employees")
        else:
            print(f"⚠️  {hr_dashboard['message']}")

    except Exception as e:
        print(f"❌ Error generating HR dashboard: {str(e)}")

    # Step 5: Display final employee details
    print("\n👥 Step 5: New Employee Details...")
    try:
        employees = get_all_employees()
        if employees:
            print(f"Successfully onboarded {len(employees)} employees:")

            for emp in employees:
                print(f"\n  👤 {emp.first_name} {emp.last_name} ({emp.employee_id})")
                print(f"     Department: {emp.department}")
                print(f"     Job Title: {emp.job_title}")
                print(f"     Status: {emp.employment_status.value}")
                print(f"     Hire Date: {emp.hire_date}")

                # Show enrichment data
                if "tenure_years" in emp.custom_fields:
                    tenure_years = emp.custom_fields["tenure_years"]
                    print(".1f")

                if "service_milestone" in emp.custom_fields:
                    print(f"     Milestone: {emp.custom_fields['service_milestone']}")
        else:
            print("No employees found after onboarding process.")

    except Exception as e:
        print(f"❌ Error retrieving employee data: {str(e)}")

    # Step 6: Clean up
    print("\n🧹 Step 6: Cleaning up...")
    try:
        clear_all_data()
        os.remove(candidates_csv)
        os.remove(requisitions_csv)
        print("✅ Cleanup completed successfully!")
    except Exception as e:
        print(f"⚠️  Warning during cleanup: {str(e)}")

    # Step 7: Summary
    print("\n🎉 Onboarding Workflow Example Completed!")
    print("=" * 60)
    print("\n📋 Summary:")
    print(f"  - Sample candidates created: 4")
    print(f"  - Job requisitions created: 3")
    print(f"  - Successful onboardings: {successful}")
    print(f"  - Failed onboardings: {failed}")

    print("\n💡 Key Features Demonstrated:")
    print("  ✅ Real data import and processing")
    print("  ✅ Candidate-to-employee conversion")
    print("  ✅ Data cleaning and enrichment")
    print("  ✅ Automated workflow processing")
    print("  ✅ Dashboard and analytics generation")
    print("  ✅ End-to-end integration between modules")

    print("\n🚀 Next Steps:")
    print("  - Try with your own HR/talent data")
    print("  - Customize the onboarding workflow")
    print("  - Add more validation and business rules")
    print("  - Integrate with external systems (HRIS, ATS)")
    print("  - Add automated notifications and approvals")

if __name__ == "__main__":
    main()
