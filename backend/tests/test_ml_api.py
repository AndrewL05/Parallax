import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_health_check():
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/api/ml/health")
        data = response.json()

        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")

        assert response.status_code == 200
        assert data.get("status") in ["healthy", "degraded"]
        print("\n[OK] Health check passed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Health check failed: {e}")
        return False


def test_generate_scenarios():  
    print_section("TEST 2: Generate Complete Scenarios")

    payload = {
        "user_profile": {
            "age": 28,
            "education": "bachelors",
            "field": "technology",
            "experience_years": 4,
            "current_salary": 85000,
            "location_type": "urban",
            "remote_work": "hybrid"
        },
        "years": 10,
        "include_narratives": True
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/scenarios/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            assert data.get("success") is True
            assert "data" in data
            assert "scenarios" in data["data"]
            assert "comparisons" in data["data"]

            scenarios = data["data"]["scenarios"]
            print(f"\nGenerated {len(scenarios)} scenarios")

            for scenario_type in ["optimistic", "realistic", "pessimistic"]:
                if scenario_type in scenarios:
                    scenario = scenarios[scenario_type]
                    stats = scenario["statistics"]

                    print(f"\n{scenario_type.upper()}:")
                    print(f"  Final Salary: ${stats['final_salary']:,.2f}")
                    print(f"  Salary Growth: {stats['salary_growth']:.1f}%")
                    print(f"  Avg Life Satisfaction: {stats['avg_life_satisfaction']}/10")
                    print(f"  Timeline Length: {len(scenario['timeline'])} years")

                    if "narrative" in scenario:
                        print(f"  Has Narrative: Yes ({len(scenario['narrative'])} chars)")

            print("\n[OK] Scenario generation passed")
            return True
        else:
            print(f"Error: {response.text}")
            print("\n[FAIL] Scenario generation failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Scenario generation failed: {e}")
        return False


def test_single_scenario():
    print_section("TEST 3: Generate Single Scenario (Realistic)")

    payload = {
        "user_profile": {
            "age": 35,
            "education": "masters",
            "field": "finance",
            "experience_years": 10,
            "current_salary": 120000,
            "location_type": "urban",
            "remote_work": "none"
        },
        "years": 5,
        "include_narratives": False
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/scenarios/single?scenario_type=realistic",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            assert data.get("success") is True
            result = data["data"]

            print(f"\nScenario Type: {result['type']}")
            print(f"Timeline Length: {len(result['timeline'])} years")
            print(f"Final Salary: ${result['statistics']['final_salary']:,.2f}")
            print(f"Salary Growth: {result['statistics']['salary_growth']:.1f}%")

            print("\n[OK] Single scenario generation passed")
            return True
        else:
            print(f"Error: {response.text}")
            print("\n[FAIL] Single scenario generation failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Single scenario generation failed: {e}")
        return False


def test_quick_prediction():
    print_section("TEST 4: Quick Prediction (5 Years)")

    payload = {
        "user_profile": {
            "age": 25,
            "education": "bachelors",
            "field": "healthcare",
            "experience_years": 2,
            "location_type": "suburban",
            "remote_work": "none"
        },
        "target_year": 5
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/predict/quick",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            assert data.get("success") is True
            result = data["data"]

            print(f"\nTarget Year: {result['target_year']}")
            print(f"Target Age: {result['target_age']}")

            for scenario_type, predictions in result["predictions"].items():
                print(f"\n{scenario_type.upper()}:")
                print(f"  Salary: ${predictions['salary']:,.2f}")
                print(f"  Life Satisfaction: {predictions['life_satisfaction']:.2f}/10")
                print(f"  Career Growth Index: {predictions['career_growth_index']:.2f}/100")

            print("\n[OK] Quick prediction passed")
            return True
        else:
            print(f"Error: {response.text}")
            print("\n[FAIL] Quick prediction failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Quick prediction failed: {e}")
        return False


def test_career_insights():
    print_section("TEST 5: Career Insights")

    payload = {
        "age": 30,
        "education": "bachelors",
        "field": "business",
        "experience_years": 6,
        "current_salary": 75000,
        "location_type": "urban",
        "remote_work": "hybrid"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/insights/career",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            assert data.get("success") is True
            insights = data["data"]

            print(f"\nCareer Stage: {insights['career_stage']}")
            print(f"Current Field: {insights['current_field']}")
            print(f"Growth Potential: {insights['growth_potential']}%")
            print(f"Expected 5-Year Salary: ${insights['expected_5yr_salary']:,.2f}")
            print(f"Expected Satisfaction: {insights['expected_satisfaction']:.2f}/10")

            print(f"\nRecommendations:")
            for i, rec in enumerate(insights.get('recommendations', []), 1):
                print(f"  {i}. {rec}")

            print("\n[OK] Career insights passed")
            return True
        else:
            print(f"Error: {response.text}")
            print("\n[FAIL] Career insights failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Career insights failed: {e}")
        return False


def test_validation():  
    print_section("TEST 6: Input Validation")

    invalid_payload = {
        "user_profile": {
            "age": 15, 
            "education": "bachelors",
            "field": "technology",
            "experience_years": 4,
            "location_type": "urban",
            "remote_work": "hybrid"
        },
        "years": 10
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ml/scenarios/generate",
            json=invalid_payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 422:
            print("Validation error correctly detected")
            print(f"Error: {response.json()}")
            print("\n[OK] Validation test passed")
            return True
        else:
            print("\n[FAIL] Validation should have failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Validation test error: {e}")
        return False


def test_example_documentation():
    print_section("TEST 7: Example Documentation")

    try:
        response = requests.get(f"{BASE_URL}/api/ml/docs/example")

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("\nExample Request:")
            print(json.dumps(data["example_request"], indent=2))

            print("\nSupported Fields:")
            print(", ".join(data["supported_fields"]))

            print("\nSupported Education Levels:")
            print(", ".join(data["supported_education_levels"]))

            print("\n[OK] Documentation endpoint passed")
            return True
        else:
            print(f"Error: {response.text}")
            print("\n[FAIL] Documentation endpoint failed")
            return False

    except Exception as e:
        print(f"\n[FAIL] Documentation endpoint failed: {e}")
        return False


def run_all_tests():
    print("\n" + "=" * 70)
    print("  ML API INTEGRATION TESTS")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print("Make sure the FastAPI server is running!")
    print()

    tests = [
        ("Health Check", test_health_check),
        ("Generate Complete Scenarios", test_generate_scenarios),
        ("Generate Single Scenario", test_single_scenario),
        ("Quick Prediction", test_quick_prediction),
        ("Career Insights", test_career_insights),
        ("Input Validation", test_validation),
        ("Example Documentation", test_example_documentation),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    print_section("TEST SUMMARY")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n[OK] All tests passed successfully!")
    else:
        print(f"\n[WARN] {total_count - passed_count} test(s) failed")


if __name__ == "__main__":
    run_all_tests()
