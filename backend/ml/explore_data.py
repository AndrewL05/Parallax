"""
Data Exploration Script for ML Pipeline

Loads and inspects all CSV datasets, generates reports on:
- Dataset shapes and schemas
- Missing values and data quality
- Summary statistics
- Outliers and distributions
- Key features for modeling

"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from ml.data_loader import MLDataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataExplorer:
    """Explore and analyze ML datasets"""

    def __init__(self, data_dir: str = "backend/ml/data"):
        self.loader = MLDataLoader(data_dir)
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.reports: Dict[str, Dict] = {}

    def load_all_datasets(self):
        """Load all CSV files from data directory"""
        logger.info("=" * 80)
        logger.info("LOADING DATASETS")
        logger.info("=" * 80)

        csv_files = self.loader.list_csv_files()
        logger.info(f"Found {len(csv_files)} CSV files")

        for filename in csv_files:
            try:
                df = self.loader.load_csv(filename)
                if df is not None:
                    self.datasets[filename] = df
                    logger.info(f"✓ Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            except Exception as e:
                logger.error(f"✗ Failed to load {filename}: {e}")

        logger.info(f"\nSuccessfully loaded {len(self.datasets)}/{len(csv_files)} datasets\n")

    def inspect_dataset(self, name: str, df: pd.DataFrame) -> Dict:
        """Generate comprehensive inspection report for a dataset"""

        report = {
            "filename": name,
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "missing_values": {},
            "duplicates": df.duplicated().sum(),
            "numeric_summary": {},
            "categorical_summary": {}
        }

        # Missing values analysis
        missing = df.isnull().sum()
        if missing.sum() > 0:
            report["missing_values"] = {
                col: {
                    "count": int(count),
                    "percentage": round(count / len(df) * 100, 2)
                }
                for col, count in missing.items() if count > 0
            }

        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                report["numeric_summary"][col] = {
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "median": float(df[col].median()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None,
                    "25%": float(df[col].quantile(0.25)) if not df[col].isnull().all() else None,
                    "75%": float(df[col].quantile(0.75)) if not df[col].isnull().all() else None,
                }

        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                unique_count = df[col].nunique()
                # Only show value counts for columns with < 20 unique values
                if unique_count < 20:
                    value_counts = df[col].value_counts().head(10).to_dict()
                else:
                    value_counts = f"{unique_count} unique values (too many to list)"

                report["categorical_summary"][col] = {
                    "unique_count": int(unique_count),
                    "top_values": value_counts
                }

        return report

    def detect_outliers(self, df: pd.DataFrame, column: str) -> Tuple[int, float, float]:
        """Detect outliers using IQR method"""
        if column not in df.columns or df[column].dtype not in [np.int64, np.float64]:
            return 0, 0, 0

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

        return len(outliers), lower_bound, upper_bound

    def print_report(self, name: str, report: Dict):
        """Print formatted report for a dataset"""

        logger.info("=" * 80)
        logger.info(f"DATASET: {name}")
        logger.info("=" * 80)

        logger.info(f"\n📊 Shape: {report['shape'][0]} rows × {report['shape'][1]} columns")
        logger.info(f"💾 Memory: {report['memory_usage_mb']:.2f} MB")
        logger.info(f"🔄 Duplicates: {report['duplicates']}")

        # Columns
        logger.info(f"\n📋 Columns ({len(report['columns'])}):")
        for col in report['columns']:
            dtype = str(report['dtypes'][col])
            logger.info(f"  - {col} ({dtype})")

        # Missing values
        if report['missing_values']:
            logger.info(f"\n⚠️  Missing Values:")
            for col, info in report['missing_values'].items():
                logger.info(f"  - {col}: {info['count']} ({info['percentage']}%)")
        else:
            logger.info(f"\n✓ No missing values")

        # Numeric summary
        if report['numeric_summary']:
            logger.info(f"\n🔢 Numeric Columns Summary:")
            for col, stats in report['numeric_summary'].items():
                logger.info(f"\n  {col}:")
                if stats['mean'] is not None:
                    logger.info(f"    Mean: {stats['mean']:.2f}")
                    logger.info(f"    Median: {stats['median']:.2f}")
                    logger.info(f"    Std: {stats['std']:.2f}")
                    logger.info(f"    Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
                    logger.info(f"    IQR: [{stats['25%']:.2f}, {stats['75%']:.2f}]")

        # Categorical summary
        if report['categorical_summary']:
            logger.info(f"\n📝 Categorical Columns Summary:")
            for col, info in report['categorical_summary'].items():
                logger.info(f"\n  {col}: {info['unique_count']} unique values")
                if isinstance(info['top_values'], dict):
                    logger.info(f"    Top values:")
                    for val, count in list(info['top_values'].items())[:5]:
                        logger.info(f"      - {val}: {count}")

        logger.info("\n")

    def identify_key_features(self):
        """Identify key features for different use cases"""

        logger.info("=" * 80)
        logger.info("KEY FEATURES IDENTIFICATION")
        logger.info("=" * 80)

        # Salary-related columns
        salary_keywords = ['salary', 'wage', 'income', 'compensation', 'pay']
        # Location-related columns
        location_keywords = ['location', 'city', 'country', 'region', 'state']
        # Experience-related columns
        experience_keywords = ['experience', 'years', 'level', 'seniority']
        # Happiness/satisfaction columns
        happiness_keywords = ['happiness', 'satisfaction', 'quality', 'score']
        # Cost of living columns
        col_keywords = ['cost', 'living', 'index', 'price']

        feature_mapping = {
            "Salary Features": [],
            "Location Features": [],
            "Experience Features": [],
            "Happiness Features": [],
            "Cost of Living Features": []
        }

        for name, df in self.datasets.items():
            for col in df.columns:
                col_lower = col.lower()

                if any(kw in col_lower for kw in salary_keywords):
                    feature_mapping["Salary Features"].append(f"{name}: {col}")

                if any(kw in col_lower for kw in location_keywords):
                    feature_mapping["Location Features"].append(f"{name}: {col}")

                if any(kw in col_lower for kw in experience_keywords):
                    feature_mapping["Experience Features"].append(f"{name}: {col}")

                if any(kw in col_lower for kw in happiness_keywords):
                    feature_mapping["Happiness Features"].append(f"{name}: {col}")

                if any(kw in col_lower for kw in col_keywords):
                    feature_mapping["Cost of Living Features"].append(f"{name}: {col}")

        for category, features in feature_mapping.items():
            if features:
                logger.info(f"\n{category}:")
                for feature in features:
                    logger.info(f"  - {feature}")

        logger.info("\n")
        return feature_mapping

    def run_full_exploration(self):
        """Run complete data exploration pipeline"""

        # Step 1: Load all datasets
        self.load_all_datasets()

        if not self.datasets:
            logger.error("No datasets loaded. Exiting.")
            return

        # Step 2: Inspect each dataset
        for name, df in self.datasets.items():
            report = self.inspect_dataset(name, df)
            self.reports[name] = report
            self.print_report(name, report)

        # Step 3: Identify key features
        feature_mapping = self.identify_key_features()

        # Step 4: Summary
        logger.info("=" * 80)
        logger.info("EXPLORATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"\n✓ Total datasets: {len(self.datasets)}")
        logger.info(f"✓ Total rows: {sum(df.shape[0] for df in self.datasets.values()):,}")
        logger.info(f"✓ Total columns: {sum(df.shape[1] for df in self.datasets.values())}")
        logger.info(f"✓ Total memory: {sum(r['memory_usage_mb'] for r in self.reports.values()):.2f} MB")

        datasets_with_missing = sum(1 for r in self.reports.values() if r['missing_values'])
        logger.info(f"\n⚠️  Datasets with missing values: {datasets_with_missing}/{len(self.datasets)}")

        logger.info("\n" + "=" * 80)
        logger.info("Exploration complete! Next steps:")
        logger.info("1. Clean datasets with missing values")
        logger.info("2. Map features to ML models")
        logger.info("3. Create preprocessing pipeline")
        logger.info("4. Train initial models")
        logger.info("=" * 80 + "\n")

if __name__ == "__main__":
    explorer = DataExplorer()
    explorer.run_full_exploration()
