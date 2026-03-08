"""
Scenario Simulator

Generate realistic future life scenarios using trained ML models.
Creates multiple scenario variations (optimistic, realistic, pessimistic)
based on user input and trained XGBoost salary model.
"""

import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ml.profession_data import (
    detect_profession,
    get_profession_salary,
    get_training_config,
    calculate_training_salary,
    PROFESSION_SALARIES,
    TRAINING_CAREERS,
)

logger = logging.getLogger(__name__)

POSITION_LEVELS_INT = {1: "entry", 2: "mid", 3: "senior", 4: "lead", 5: "executive"}
POSITION_LEVELS_STR = {v: k for k, v in POSITION_LEVELS_INT.items()}


class ScenarioSimulator:
    """
    Generate future life scenarios with multiple variations using trained ML models.
    """

    def __init__(self, models_dir: str = "models", features_dir: str = "data/features"):
        self.models_dir = Path(models_dir)
        self.features_dir = Path(features_dir)
        self.model = None
        self.scaler = None
        self.encoders = None
        self.feature_cols = None
        self.feature_stats = None

        self._load_models()
        self._load_feature_stats()

    def _load_models(self):
        """Load trained ML model and preprocessing artifacts."""
        try:
            model_path = self.models_dir / "salary_model.pkl"
            scaler_path = self.models_dir / "salary_scaler.pkl"
            encoders_path = self.models_dir / "salary_encoders.pkl"
            feature_cols_path = self.models_dir / "salary_feature_cols.pkl"

            if all(p.exists() for p in [model_path, scaler_path, encoders_path, feature_cols_path]):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                self.encoders = joblib.load(encoders_path)
                self.feature_cols = joblib.load(feature_cols_path)
                logger.info("Loaded trained salary model for scenario simulation")
            else:
                logger.warning("Trained model not found — run `python -m ml.train_pipeline`")
        except Exception as e:
            logger.warning(f"Error loading model: {e}")

    def _load_feature_stats(self):
        """Load feature statistics for realistic bounds."""
        try:
            features_path = self.features_dir / "salary_features_enhanced.csv"
            if features_path.exists():
                df = pd.read_csv(features_path)
                self.feature_stats = {
                    "salary": {
                        "mean": df["salary"].mean(),
                        "std": df["salary"].std(),
                        "min": df["salary"].min(),
                        "max": df["salary"].max(),
                    },
                }
                logger.info(
                    f"Loaded feature stats: salary mean=${self.feature_stats['salary']['mean']:,.0f}, "
                    f"std=${self.feature_stats['salary']['std']:,.0f}"
                )
                return
        except Exception as e:
            logger.warning(f"Error loading feature stats: {e}")

        self.feature_stats = {
            "salary": {"mean": 100000, "std": 50000, "min": 20000, "max": 2000000},
        }

    # ------------------------------------------------------------------
    # Model-based salary prediction
    # ------------------------------------------------------------------

    def _predict_salary(
        self,
        profession: str,
        career_field: str,
        position_level: str,
        education: str,
        location_type: str,
        age: int,
        years_experience: float,
        has_remote: bool = False,
        is_career_change: bool = False,
        industry_growth_rate: float = 0.03,
    ) -> Optional[float]:
        """Predict salary using trained XGBoost model."""
        if self.model is None:
            return None

        is_training_career = int(profession in TRAINING_CAREERS) if profession else 0
        in_training = 0
        if is_training_career and profession:
            tc = TRAINING_CAREERS[profession]
            in_training = int(years_experience < tc["training_years"])

        row = {
            "profession": profession or "other",
            "career_field": career_field,
            "position_level": position_level,
            "education_level": education,
            "location_type": location_type,
            "age": age,
            "years_experience": round(years_experience, 1),
            "has_remote": int(has_remote),
            "is_career_change": int(is_career_change),
            "is_training_career": is_training_career,
            "in_training": in_training,
            "industry_growth_rate": round(industry_growth_rate, 4),
        }

        for col in ["career_field", "position_level", "education_level", "location_type", "profession"]:
            le = self.encoders[col]
            val = row[col]
            if val in le.classes_:
                row[col + "_enc"] = le.transform([val])[0]
            else:
                row[col + "_enc"] = int(np.median(le.transform(le.classes_)))

        features = pd.DataFrame([{c: row[c] for c in self.feature_cols}])
        features_scaled = pd.DataFrame(
            self.scaler.transform(features), columns=self.feature_cols,
        )
        return max(20000, float(self.model.predict(features_scaled)[0]))

    # ------------------------------------------------------------------
    # Scenario generation
    # ------------------------------------------------------------------

    def generate_scenarios(
        self, user_profile: Dict, years: int = 10, num_variations: int = 3,
    ) -> Dict[str, List[Dict]]:
        """Generate optimistic, realistic, and pessimistic scenario timelines."""
        variations = {
            "optimistic":  {"growth": 1.3, "stability": 1.2, "satisfaction": 1.15, "events": "positive"},
            "realistic":   {"growth": 1.0, "stability": 1.0, "satisfaction": 1.0,  "events": "mixed"},
            "pessimistic": {"growth": 0.7, "stability": 0.85, "satisfaction": 0.9, "events": "negative"},
        }
        return {
            name: self._generate_timeline(user_profile, years, mult)
            for name, mult in variations.items()
        }

    def _generate_timeline(
        self, user_profile: Dict, years: int, multipliers: Dict,
    ) -> List[Dict]:
        current_age = user_profile.get("age", 25)
        current_experience = user_profile.get("experience_years", 0)
        field = user_profile.get("field", "business")
        education = user_profile.get("education", "bachelors")
        job_title = user_profile.get("job_title") or user_profile.get("title", "")
        location = user_profile.get("location_type", "suburb")

        # Map location names
        location_map = {"urban": "major_city", "suburban": "suburb"}
        location = location_map.get(location, location)

        has_remote = user_profile.get("remote_work", "none") in ("full", "hybrid")

        detected_profession = detect_profession(job_title, "") if job_title else None

        current_salary = user_profile.get("current_salary") or self._estimate_base_salary(
            field, education, current_experience, job_title, location, has_remote,
        )

        career_state = {
            "salary": current_salary,
            "position_level": self._infer_position_level(current_experience, current_salary),
            "years_in_position": 0,
            "total_experience": current_experience,
            "field": field,
            "education": education,
            "location": location,
            "has_remote": has_remote,
            "stability_score": 0.8,
            "satisfaction_score": 7.0,
            "detected_profession": detected_profession,
            "job_title": job_title,
        }

        timeline = []
        for year in range(years):
            year_data = self._simulate_year(career_state, current_age + year, multipliers, year)
            timeline.append(year_data)
            self._update_career_state(career_state, year_data, multipliers)

        return timeline

    def _simulate_year(
        self, career_state: Dict, age: int, multipliers: Dict, year_index: int,
    ) -> Dict:
        detected_profession = career_state.get("detected_profession")
        pos_str = POSITION_LEVELS_INT.get(career_state["position_level"], "mid")

        # --- Salary: model prediction first, fallback to formula ---
        model_salary = self._predict_salary(
            profession=detected_profession,
            career_field=career_state["field"],
            position_level=pos_str,
            education=career_state["education"],
            location_type=career_state["location"],
            age=age,
            years_experience=career_state["total_experience"] + year_index,
            has_remote=career_state.get("has_remote", False),
            is_career_change=False,
            industry_growth_rate=0.03,
        )

        if model_salary is not None:
            new_salary = model_salary * multipliers["growth"]
        else:
            # Fallback: check training career, then formula
            training_result = None
            if detected_profession:
                training_result = calculate_training_salary(detected_profession, year_index)
            if training_result:
                new_salary, _ = training_result
                new_salary *= multipliers["growth"]
            else:
                base_growth = self._fallback_growth_rate(career_state)
                new_salary = career_state["salary"] * (1 + base_growth * multipliers["growth"])

        # --- Promotion ---
        promotion_prob = self._calculate_promotion_probability(career_state, year_index)
        is_promoted = np.random.random() < (promotion_prob * multipliers["growth"])

        if is_promoted:
            # Re-predict at new level
            new_level = min(career_state["position_level"] + 1, 5)
            new_pos_str = POSITION_LEVELS_INT.get(new_level, pos_str)
            promoted_salary = self._predict_salary(
                profession=detected_profession,
                career_field=career_state["field"],
                position_level=new_pos_str,
                education=career_state["education"],
                location_type=career_state["location"],
                age=age,
                years_experience=career_state["total_experience"] + year_index,
                has_remote=career_state.get("has_remote", False),
            )
            if promoted_salary and promoted_salary > new_salary:
                new_salary = promoted_salary * multipliers["growth"]
            else:
                new_salary *= 1.15  # fallback promotion bump
            career_state["position_level"] = new_level
            career_state["years_in_position"] = 0

        # --- Other metrics ---
        work_life_balance = self._calculate_work_life_balance(
            career_state["position_level"], career_state["field"]
        )
        life_satisfaction = self._calculate_life_satisfaction(
            career_state, new_salary, age, multipliers,
        )
        financial_security = self._calculate_financial_security(new_salary, age)
        life_events = self._generate_life_events(
            age, year_index, multipliers["events"], is_promoted, detected_profession,
        )

        # Training completion event
        if detected_profession:
            tc = get_training_config(detected_profession)
            if tc and year_index == tc["training_years"]:
                life_events.insert(0, f"Completed {detected_profession.title()} training/residency!")

        return {
            "year": year_index + 1,
            "age": age,
            "salary": round(new_salary, 2),
            "position_level": career_state["position_level"],
            "career_growth_index": round(self._calculate_career_growth_index(career_state, new_salary), 2),
            "life_satisfaction": round(life_satisfaction, 2),
            "financial_security": round(financial_security, 2),
            "work_life_balance": round(work_life_balance, 2),
            "stability_score": round(career_state["stability_score"] * 100, 2),
            "is_promoted": is_promoted,
            "life_events": life_events,
            "happiness_score": round(life_satisfaction * 1.2, 2),
            "stress_level": round((10 - work_life_balance) * 0.8, 2),
            "health_score": round(self._calculate_health_score(age, work_life_balance), 2),
        }

    # ------------------------------------------------------------------
    # Helper: base salary estimation (model-first)
    # ------------------------------------------------------------------

    def _estimate_base_salary(
        self, field: str, education: str, experience: int,
        job_title: str = None, location: str = "suburb", has_remote: bool = False,
    ) -> float:
        detected = detect_profession(job_title, "") if job_title else None

        model_salary = self._predict_salary(
            profession=detected,
            career_field=field,
            position_level=self._infer_position_str(experience),
            education=education,
            location_type=location,
            age=22 + experience,
            years_experience=experience,
            has_remote=has_remote,
        )
        if model_salary:
            return model_salary

        # Fallback to lookup tables
        if detected and detected in PROFESSION_SALARIES:
            pos = self._infer_position_str(experience)
            tc = get_training_config(detected)
            if tc and experience < tc["training_years"]:
                return tc["training_salary"]
            base = get_profession_salary(detected, pos) or 50000
            edu_mult = {"high_school": 0.7, "associates": 0.85, "bachelors": 1.0, "masters": 1.25, "phd": 1.4}
            return base * edu_mult.get(education.lower(), 1.0)

        field_base = {
            "technology": 75000, "finance": 70000, "healthcare": 65000,
            "engineering": 70000, "education": 45000, "business": 60000,
            "creative": 50000, "service": 35000, "other": 50000,
        }
        edu_mult = {"high_school": 0.7, "associates": 0.85, "bachelors": 1.0, "masters": 1.25, "phd": 1.4}
        base = field_base.get(field.lower(), 50000)
        return base * edu_mult.get(education.lower(), 1.0) * (1 + min(experience * 0.03, 0.6))

    def _infer_position_str(self, experience: int) -> str:
        if experience < 3: return "entry"
        elif experience < 7: return "mid"
        elif experience < 12: return "senior"
        elif experience < 18: return "lead"
        else: return "executive"

    def _infer_position_level(self, experience: int, salary: float) -> int:
        if experience < 2: return 1
        elif experience < 5: return 2
        elif experience < 10: return 3
        elif experience < 15: return 4
        else: return 5

    def _fallback_growth_rate(self, career_state: Dict) -> float:
        rates = {1: 0.06, 2: 0.05, 3: 0.04, 4: 0.03, 5: 0.025}
        base = rates.get(career_state["position_level"], 0.04)
        return base * career_state["stability_score"] + np.random.uniform(-0.01, 0.02)

    # ------------------------------------------------------------------
    # Metrics calculations
    # ------------------------------------------------------------------

    def _calculate_promotion_probability(self, career_state: Dict, year_index: int) -> float:
        if career_state["years_in_position"] < 2: base = 0.05
        elif career_state["years_in_position"] < 4: base = 0.20
        else: base = 0.35
        level_factor = {1: 1.0, 2: 0.9, 3: 0.7, 4: 0.5, 5: 0.2}
        base *= level_factor.get(career_state["position_level"], 0.5)
        return min(base * career_state["satisfaction_score"] / 7.0, 0.5)

    def _calculate_career_growth_index(self, career_state: Dict, new_salary: float) -> float:
        stats = self.feature_stats["salary"]
        salary_pct = min((new_salary - stats["min"]) / (stats["max"] - stats["min"]) * 40, 40)
        exp_pts = min(career_state["total_experience"] * 1.5, 30)
        pos_pts = career_state["position_level"] * 4
        stab_pts = career_state["stability_score"] * 10
        return min(salary_pct + exp_pts + pos_pts + stab_pts, 100)

    def _calculate_life_satisfaction(
        self, career_state: Dict, salary: float, age: int, multipliers: Dict,
    ) -> float:
        stats = self.feature_stats["salary"]
        financial = min((salary / stats["mean"]) * 1.75, 3.5)
        career = career_state["satisfaction_score"] / 7.0 * 2.5
        wlb = self._calculate_work_life_balance(career_state["position_level"], career_state["field"]) / 10 * 2
        stab = career_state["stability_score"] * 2
        base = financial + career + wlb + stab
        age_factor = 1.0 if age < 30 else 1.1 if age < 50 else 0.95
        return min(base * multipliers["satisfaction"] * age_factor, 10)

    def _calculate_financial_security(self, salary: float, age: int) -> float:
        expected = {25: 50000, 30: 70000, 35: 90000, 40: 110000, 45: 120000, 50: 130000, 55: 135000, 60: 140000}
        nearest_age = min(expected.keys(), key=lambda x: abs(x - age))
        return min(salary / expected[nearest_age] * 5, 10)

    def _calculate_work_life_balance(self, position_level: int, field: str) -> float:
        level_impact = {1: 8.5, 2: 8.0, 3: 7.0, 4: 6.0, 5: 5.5}
        base = level_impact.get(position_level, 7.0)
        adj = {"technology": -0.5, "finance": -1.0, "healthcare": -0.8, "engineering": -0.3,
               "education": 0.5, "business": -0.5, "creative": 0.3, "service": 0.0}
        return max(min(base + adj.get(field.lower(), 0) + np.random.uniform(-0.5, 0.5), 10), 3)

    def _calculate_health_score(self, age: int, work_life_balance: float) -> float:
        if age < 30: base = 9.0
        elif age < 40: base = 8.5
        elif age < 50: base = 8.0
        elif age < 60: base = 7.5
        else: base = 7.0
        return max(min(base + (work_life_balance - 5) * 0.2 + np.random.uniform(-0.3, 0.3), 10), 4)

    def _generate_life_events(
        self, age: int, year_index: int, event_tone: str,
        is_promoted: bool, detected_profession: str = None,
    ) -> List[str]:
        events = []
        if is_promoted:
            events.append("Received promotion to higher position")
        if age == 30 and year_index < 3:
            events.append("Considering major life decisions")
        if 28 <= age <= 35 and np.random.random() < 0.15:
            events.append("Purchased first home" if event_tone != "negative" else "Dealing with housing market challenges")
        if 25 <= age <= 40 and np.random.random() < 0.1:
            events.append("Started family" if event_tone == "positive" else "Considering family planning")
        if year_index > 2 and np.random.random() < 0.12:
            if event_tone == "positive": events.append("Received recognition award or bonus")
            elif event_tone == "negative": events.append("Faced workplace challenges")
            else: events.append("Completed professional development course")
        if np.random.random() < 0.08:
            if event_tone == "positive":
                events.append(np.random.choice([
                    "Started successful side project", "Made valuable professional connections",
                    "Achieved personal milestone", "Improved health and fitness",
                ]))
            elif event_tone == "negative":
                events.append(np.random.choice([
                    "Dealt with unexpected expenses", "Faced industry challenges",
                    "Navigated organizational changes",
                ]))
        return events if events else ["Steady progress in career and life"]

    def _update_career_state(self, career_state: Dict, year_data: Dict, multipliers: Dict):
        career_state["salary"] = year_data["salary"]
        career_state["position_level"] = year_data["position_level"]
        career_state["years_in_position"] += 0 if year_data["is_promoted"] else 1
        career_state["total_experience"] += 1
        stab_change = np.random.uniform(-0.05, 0.05) * multipliers["stability"]
        career_state["stability_score"] = max(min(career_state["stability_score"] + stab_change, 1.0), 0.6)
        sat_change = 0.1 if year_data["is_promoted"] else np.random.uniform(-0.2, 0.2)
        career_state["satisfaction_score"] = max(min(career_state["satisfaction_score"] + sat_change, 10), 4)

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def compare_scenarios(self, scenarios: Dict[str, List[Dict]]) -> Dict:
        comparison = {}
        for name, timeline in scenarios.items():
            final = timeline[-1]
            comparison[name] = {
                "final_salary": final["salary"],
                "salary_growth": ((final["salary"] - timeline[0]["salary"]) / timeline[0]["salary"]) * 100,
                "final_position_level": final["position_level"],
                "avg_life_satisfaction": round(np.mean([y["life_satisfaction"] for y in timeline]), 2),
                "avg_career_growth_index": round(np.mean([y["career_growth_index"] for y in timeline]), 2),
                "total_promotions": sum(1 for y in timeline if y["is_promoted"]),
                "final_financial_security": final["financial_security"],
                "avg_work_life_balance": round(np.mean([y["work_life_balance"] for y in timeline]), 2),
                "total_life_events": sum(len(y["life_events"]) for y in timeline),
            }
        return comparison
