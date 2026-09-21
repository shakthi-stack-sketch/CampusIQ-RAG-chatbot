import sys
import os
import traceback

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tests.test_campusiq_upgrade import (
    setup_test_environment,
    test_vectorstore_indexed,
    test_mess_menu_all_days_indexed,
    test_monday_breakfast_retrieval,
    test_tuesday_lunch_retrieval,
    test_wednesday_dinner_retrieval,
    test_thursday_retrieval,
    test_friday_snacks_retrieval,
    test_saturday_dinner_retrieval,
    test_sunday_breakfast_retrieval,
    test_full_weekly_menu_retrieval,
    test_academic_iat_count,
    test_dress_code_norms,
    test_hostel_leave_card_colors,
    test_clubs_retrieval,
    test_followup_contextualization_clubs_ai,
    test_followup_contextualization_menu,
    test_anti_hallucination_fake_event,
    test_anti_hallucination_fake_fee,
    test_anti_hallucination_fake_office,
    test_anti_hallucination_fake_staff,
    test_anti_hallucination_fake_opportunity,
    test_saved_answers_lifecycle,
    test_vault_document_isolation,
    test_campus_pulse_items,
    test_verified_opportunities_items,
    test_verified_locations_items
)

def run_all():
    print("=" * 70)
    print("CAMPUSIQ — SAFE PRODUCT UPGRADE: AUTOMATED VERIFICATION SUITE")
    print("=" * 70)

    setup_test_environment()

    test_functions = [
        ("Vectorstore Index Count", test_vectorstore_indexed),
        ("Mess Menu All 7 Days Validation", test_mess_menu_all_days_indexed),
        ("Monday Breakfast Retrieval", test_monday_breakfast_retrieval),
        ("Tuesday Lunch Retrieval", test_tuesday_lunch_retrieval),
        ("Wednesday Dinner Retrieval", test_wednesday_dinner_retrieval),
        ("Thursday Food Retrieval", test_thursday_retrieval),
        ("Friday Snacks Retrieval", test_friday_snacks_retrieval),
        ("Saturday Dinner Retrieval", test_saturday_dinner_retrieval),
        ("Sunday Breakfast Retrieval", test_sunday_breakfast_retrieval),
        ("Full Weekly Menu Retrieval (All 7 Days)", test_full_weekly_menu_retrieval),
        ("Academic Assessments & IAT Count", test_academic_iat_count),
        ("Dress Code (Formal vs Casual)", test_dress_code_norms),
        ("Hostel Leave Cards (Pink/Yellow)", test_hostel_leave_card_colors),
        ("Clubs & Student Development", test_clubs_retrieval),
        ("Multi-Turn Follow-Up (Clubs -> AI)", test_followup_contextualization_clubs_ai),
        ("Multi-Turn Follow-Up (Menu -> Thursday)", test_followup_contextualization_menu),
        ("Anti-Hallucination: Fake Event (Mars Hackathon)", test_anti_hallucination_fake_event),
        ("Anti-Hallucination: Fake Fee (Quantum Lab)", test_anti_hallucination_fake_fee),
        ("Anti-Hallucination: Fake Office (Room 909)", test_anti_hallucination_fake_office),
        ("Anti-Hallucination: Fake Staff Member", test_anti_hallucination_fake_staff),
        ("Anti-Hallucination: Fake Opportunity & Link", test_anti_hallucination_fake_opportunity),
        ("Saved Answers CRUD Lifecycle", test_saved_answers_lifecycle),
        ("Personal Knowledge Vault Isolation (User A vs B)", test_vault_document_isolation),
        ("Campus Pulse Verified Updates", test_campus_pulse_items),
        ("Verified Opportunities Finder", test_verified_opportunities_items),
        ("Verified Locations & Office Guide", test_verified_locations_items)
    ]

    passed = 0
    failed = 0

    for name, func in test_functions:
        print(f"Running: {name} ... ", end="", flush=True)
        try:
            func()
            print("[PASS]")
            passed += 1
        except Exception as e:
            print(f"[FAIL]: {e}")
            traceback.print_exc()
            failed += 1

    print("=" * 70)
    print(f"TEST SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL {len(test_functions)})")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_all()
