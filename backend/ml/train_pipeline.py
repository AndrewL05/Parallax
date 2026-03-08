"""
ML Training Pipeline

Generates realistic training data from profession_data.py and trains
XGBoost models for salary prediction with full feature set.

Run: python -m ml.train_pipeline
"""

import numpy as np
import pandas as pd
import joblib
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor

from ml.profession_data import (
    PROFESSION_SALARIES,
    TRAINING_CAREERS,
    PROFESSION_TO_FIELD,
)
from config import LOCATION_MULTIPLIERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. Synthetic Data Generation
# ---------------------------------------------------------------------------

EDUCATION_LEVELS = ["high_school", "associates", "bachelors", "masters", "phd", "bootcamp", "self_taught"]
POSITION_LEVELS = ["entry", "mid", "senior", "lead", "executive"]
LOCATION_TYPES = list(LOCATION_MULTIPLIERS.keys())

EDUCATION_SALARY_MULT = {
    "high_school": 0.70,
    "associates": 0.85,
    "bootcamp": 0.90,
    "self_taught": 0.85,
    "bachelors": 1.00,
    "masters": 1.25,
    "phd": 1.40,
}

EDUCATION_YEARS = {
    "high_school": 0,
    "associates": 2,
    "bootcamp": 0.5,
    "self_taught": 0,
    "bachelors": 4,
    "masters": 6,
    "phd": 9,
}

FIELD_GROWTH_RATES = {
    "technology": 0.08,
    "healthcare": 0.06,
    "finance": 0.04,
    "engineering": 0.05,
    "education": 0.02,
    "business": 0.04,
    "creative": 0.03,
    "service": 0.03,
    "other": 0.03,
}


def _experience_for_position(position: str) -> tuple[int, int]:
    """Typical experience range for a position level."""
    return {
        "entry": (0, 3),
        "mid": (2, 7),
        "senior": (5, 15),
        "lead": (10, 25),
        "executive": (15, 40),
    }[position]


def _age_for_experience(exp: float, education: str) -> int:
    edu_years = EDUCATION_YEARS.get(education, 4)
    base_age = 18 + edu_years
    return int(base_age + exp + np.random.uniform(-1, 1))


def generate_training_data(n_samples: int = 15000, seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic salary training data using profession_data.py as ground truth.

    For each sample we:
    1. Pick a profession (or generic field) randomly
    2. Pick a position level and generate matching experience
    3. Look up the base salary from PROFESSION_SALARIES
    4. Apply education, location, experience, and remote multipliers
    5. Add realistic noise (log-normal, ±15%)
    """
    rng = np.random.default_rng(seed)
    rows = []

    professions = list(PROFESSION_SALARIES.keys())
    fields = list(set(
        f.value if hasattr(f, "value") else str(f)
        for f in PROFESSION_TO_FIELD.values()
    ))

    for _ in range(n_samples):
        # --- Pick profession + field ---
        profession = rng.choice(professions)
        field_enum = PROFESSION_TO_FIELD.get(profession)
        field = field_enum.value if hasattr(field_enum, "value") else str(field_enum)

        # --- Pick position level with realistic distribution ---
        pos_weights = [0.30, 0.28, 0.22, 0.13, 0.07]  # more juniors than execs
        position = rng.choice(POSITION_LEVELS, p=pos_weights)

        # --- Experience matching position ---
        exp_lo, exp_hi = _experience_for_position(position)
        experience = rng.uniform(exp_lo, exp_hi)

        # --- Education (weighted, field-aware) ---
        if field in ("technology", "engineering", "finance"):
            edu_weights = [0.03, 0.05, 0.45, 0.30, 0.10, 0.05, 0.02]
        elif field == "healthcare":
            edu_weights = [0.02, 0.05, 0.30, 0.30, 0.30, 0.02, 0.01]
        elif field == "education":
            edu_weights = [0.05, 0.10, 0.35, 0.35, 0.12, 0.02, 0.01]
        elif field in ("creative", "service"):
            edu_weights = [0.10, 0.10, 0.35, 0.15, 0.03, 0.15, 0.12]
        else:
            edu_weights = [0.08, 0.08, 0.40, 0.25, 0.08, 0.06, 0.05]
        education = rng.choice(EDUCATION_LEVELS, p=edu_weights)

        # --- Location ---
        location = rng.choice(LOCATION_TYPES)

        # --- Remote work ---
        if field in ("technology", "finance", "business"):
            has_remote = bool(rng.random() < 0.55)
        elif field in ("healthcare", "service"):
            has_remote = bool(rng.random() < 0.10)
        else:
            has_remote = bool(rng.random() < 0.25)

        # --- Career change flag ---
        is_career_change = bool(rng.random() < 0.15)

        # --- Age ---
        age = _age_for_experience(experience, education)
        age = max(18, min(70, age))

        # --- Industry growth rate ---
        base_growth = FIELD_GROWTH_RATES.get(field, 0.03)
        industry_growth = base_growth + rng.normal(0, 0.01)
        industry_growth = max(-0.05, min(0.15, industry_growth))

        # --- Base salary from profession data ---
        profession_salaries = PROFESSION_SALARIES[profession]
        base_salary = profession_salaries.get(position, profession_salaries.get("entry", 50000))

        # --- Check training career ---
        is_training_career = profession in TRAINING_CAREERS
        in_training = False
        if is_training_career:
            tc = TRAINING_CAREERS[profession]
            if experience < tc["training_years"]:
                # In training (residency etc.) — override base salary
                annual_raise = tc.get("annual_training_raise", 0.03)
                base_salary = tc["training_salary"] * ((1 + annual_raise) ** experience)
                in_training = True
            else:
                years_post = experience - tc["training_years"]
                base_salary = tc["post_training_salary"] * ((1.05) ** years_post)

        # --- Apply multipliers ---
        edu_mult = EDUCATION_SALARY_MULT.get(education, 1.0)
        loc_mult = LOCATION_MULTIPLIERS.get(location, 1.0)
        exp_mult = 1 + min(0.5, experience * 0.02)
        remote_mult = 1.10 if has_remote and field in ("technology", "finance", "business") else 1.0
        change_mult = 0.90 if is_career_change else 1.0

        # For training careers, education/experience multipliers are already baked in
        if in_training:
            salary = base_salary * loc_mult * remote_mult
        else:
            salary = base_salary * edu_mult * loc_mult * exp_mult * remote_mult * change_mult

        # --- Add realistic noise (log-normal, ~15% std) ---
        noise = rng.lognormal(0, 0.12)
        salary *= noise

        salary = max(20000, salary)

        rows.append({
            "profession": profession,
            "career_field": field,
            "position_level": position,
            "education_level": education,
            "location_type": location,
            "age": age,
            "years_experience": round(experience, 1),
            "has_remote": int(has_remote),
            "is_career_change": int(is_career_change),
            "is_training_career": int(is_training_career),
            "in_training": int(in_training),
            "industry_growth_rate": round(industry_growth, 4),
            "salary": round(salary, 2),
        })

    df = pd.DataFrame(rows)
    logger.info(f"Generated {len(df)} training samples across {df['profession'].nunique()} professions")
    logger.info(f"Salary range: ${df['salary'].min():,.0f} - ${df['salary'].max():,.0f}")
    logger.info(f"Median salary: ${df['salary'].median():,.0f}")
    return df


# ---------------------------------------------------------------------------
# 2. Feature Encoding
# ---------------------------------------------------------------------------

def encode_features(df: pd.DataFrame, encoders: dict = None, fit: bool = True):
    """
    Encode categorical features for XGBoost.

    Returns (X dataframe, y series, encoders dict).
    """
    if encoders is None:
        encoders = {}

    df = df.copy()

    categorical_cols = ["career_field", "position_level", "education_level", "location_type", "profession"]

    for col in categorical_cols:
        if fit:
            le = LabelEncoder()
            df[col + "_enc"] = le.fit_transform(df[col])
            encoders[col] = le
        else:
            le = encoders[col]
            # Handle unseen labels
            known = set(le.classes_)
            df[col + "_enc"] = df[col].apply(
                lambda x: le.transform([x])[0] if x in known else -1
            )

    feature_cols = [
        "age",
        "years_experience",
        "has_remote",
        "is_career_change",
        "is_training_career",
        "in_training",
        "industry_growth_rate",
        "career_field_enc",
        "position_level_enc",
        "education_level_enc",
        "location_type_enc",
        "profession_enc",
    ]

    X = df[feature_cols]
    y = df["salary"]

    return X, y, encoders, feature_cols


# ---------------------------------------------------------------------------
# 3. Training
# ---------------------------------------------------------------------------

def train_model(X_train, y_train, X_val, y_val):
    """Train XGBoost regressor with tuned hyperparameters."""
    model = XGBRegressor(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    return model


def evaluate_model(model, X_val, y_val):
    """Evaluate and log model metrics."""
    preds = model.predict(X_val)
    mae = mean_absolute_error(y_val, preds)
    r2 = r2_score(y_val, preds)

    # Percentage error
    mape = np.mean(np.abs(y_val - preds) / y_val) * 100

    logger.info(f"Validation MAE:  ${mae:,.0f}")
    logger.info(f"Validation R²:   {r2:.4f}")
    logger.info(f"Validation MAPE: {mape:.1f}%")

    return {"mae": mae, "r2": r2, "mape": mape}


# ---------------------------------------------------------------------------
# 4. Main Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(output_dir: str = "ml/models", n_samples: int = 15000):
    """Run the full training pipeline."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate data
    logger.info("=" * 60)
    logger.info("Step 1: Generating training data...")
    df = generate_training_data(n_samples=n_samples)

    # Save training data for reference
    data_dir = Path("ml/data/features")
    data_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_dir / "salary_features_enhanced.csv", index=False)
    logger.info(f"Saved training data to {data_dir / 'salary_features_enhanced.csv'}")

    # Encode features
    logger.info("=" * 60)
    logger.info("Step 2: Encoding features...")
    X, y, encoders, feature_cols = encode_features(df, fit=True)

    # Split
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"Train: {len(X_train)}, Validation: {len(X_val)}")

    # Scale
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train), columns=feature_cols, index=X_train.index
    )
    X_val_scaled = pd.DataFrame(
        scaler.transform(X_val), columns=feature_cols, index=X_val.index
    )

    # Train
    logger.info("=" * 60)
    logger.info("Step 3: Training XGBoost model...")
    model = train_model(X_train_scaled, y_train, X_val_scaled, y_val)

    # Evaluate
    logger.info("=" * 60)
    logger.info("Step 4: Evaluating model...")
    metrics = evaluate_model(model, X_val_scaled, y_val)

    # Save artifacts
    logger.info("=" * 60)
    logger.info("Step 5: Saving model artifacts...")

    joblib.dump(model, output_path / "salary_model.pkl")
    joblib.dump(scaler, output_path / "salary_scaler.pkl")
    joblib.dump(encoders, output_path / "salary_encoders.pkl")
    joblib.dump(feature_cols, output_path / "salary_feature_cols.pkl")

    logger.info(f"Saved: salary_model.pkl, salary_scaler.pkl, salary_encoders.pkl, salary_feature_cols.pkl")

    # Feature importance
    logger.info("=" * 60)
    logger.info("Feature Importance:")
    importance = dict(zip(feature_cols, model.feature_importances_))
    for feat, imp in sorted(importance.items(), key=lambda x: -x[1]):
        logger.info(f"  {feat:30s} {imp:.4f}")

    logger.info("=" * 60)
    logger.info("Training pipeline complete!")
    logger.info(f"Model R²: {metrics['r2']:.4f}, MAE: ${metrics['mae']:,.0f}, MAPE: {metrics['mape']:.1f}%")

    return model, scaler, encoders, feature_cols, metrics


if __name__ == "__main__":
    run_pipeline()
