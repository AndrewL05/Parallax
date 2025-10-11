"""
Data Preprocessing and Cleaning Pipeline

Loads raw CSV files, cleans data, merges datasets, and saves processed data
ready for ML model training.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ml.data_loader import MLDataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess and clean ML datasets"""

    def __init__(self, data_dir: str = "backend/ml/data"):
        self.loader = MLDataLoader(data_dir)
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)

        self.datasets: Dict[str, pd.DataFrame] = {}
        self.processed_data: Dict[str, pd.DataFrame] = {}

    def load_all_datasets(self):
        """Load all available CSV files"""
        logger.info("=" * 80)
        logger.info("LOADING RAW DATASETS")
        logger.info("=" * 80)

        csv_files = self.loader.list_csv_files()
        logger.info(f"Found {len(csv_files)} CSV files\n")

        for filename in csv_files:
            try:
                # Skip already processed files
                if 'cleaned_' in filename:
                    continue

                df = self.loader.load_csv(filename)
                if df is not None and len(df) > 0:
                    self.datasets[filename] = df
                    logger.info(f"✓ {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
            except Exception as e:
                logger.error(f"✗ Failed to load {filename}: {e}")

        logger.info(f"\nLoaded {len(self.datasets)} datasets\n")

    def clean_salary_data(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Clean salary-related datasets"""
        logger.info(f"Cleaning salary data: {filename}")

        df_clean = df.copy()

        # Standardize column names
        df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

        # Find salary columns
        salary_cols = [col for col in df_clean.columns if 'salary' in col or 'wage' in col or 'income' in col]

        if salary_cols:
            salary_col = salary_cols[0]
            logger.info(f"  Found salary column: {salary_col}")

            # Convert to numeric
            if df_clean[salary_col].dtype == 'object':
                df_clean[salary_col] = pd.to_numeric(
                    df_clean[salary_col].str.replace('[^0-9.]', '', regex=True),
                    errors='coerce'
                )

            # Remove outliers (salary must be between $10k and $1M)
            before_count = len(df_clean)
            df_clean = df_clean[
                (df_clean[salary_col] >= 10000) &
                (df_clean[salary_col] <= 1000000)
            ]
            removed = before_count - len(df_clean)
            if removed > 0:
                logger.info(f"  Removed {removed} outliers from {salary_col}")

            # Rename to standard 'salary_usd'
            df_clean = df_clean.rename(columns={salary_col: 'salary_usd'})

        # Find and standardize experience columns
        exp_cols = [col for col in df_clean.columns if 'experience' in col or 'years' in col]
        if exp_cols:
            exp_col = exp_cols[0]
            # Convert to numeric years
            if df_clean[exp_col].dtype == 'object':
                df_clean[exp_col] = df_clean[exp_col].str.extract(r'(\d+)').astype(float)
            df_clean = df_clean.rename(columns={exp_col: 'years_experience'})

        # Find and standardize education columns
        edu_cols = [col for col in df_clean.columns if 'education' in col or 'degree' in col]
        if edu_cols:
            df_clean = df_clean.rename(columns={edu_cols[0]: 'education_level'})

        # Find and standardize location columns
        loc_cols = [col for col in df_clean.columns if 'location' in col or 'country' in col or 'city' in col]
        if loc_cols and 'location' not in df_clean.columns:
            df_clean = df_clean.rename(columns={loc_cols[0]: 'location'})

        # Find and standardize job title columns
        job_cols = [col for col in df_clean.columns if 'job' in col or 'title' in col or 'role' in col]
        if job_cols and 'job_title' not in df_clean.columns:
            df_clean = df_clean.rename(columns={job_cols[0]: 'job_title'})

        logger.info(f"  Result: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
        return df_clean

    def clean_happiness_data(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Clean happiness/satisfaction datasets"""
        logger.info(f"Cleaning happiness data: {filename}")

        df_clean = df.copy()

        # Standardize column names
        df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

        # Find happiness/satisfaction score
        score_cols = [col for col in df_clean.columns if 'happiness' in col or 'satisfaction' in col or 'score' in col]
        if score_cols:
            score_col = score_cols[0]

            # Convert to numeric (0-10 scale)
            if df_clean[score_col].dtype == 'object':
                df_clean[score_col] = pd.to_numeric(df_clean[score_col], errors='coerce')

            # Normalize to 0-10 scale if needed
            if df_clean[score_col].max() > 10:
                df_clean[score_col] = (df_clean[score_col] / df_clean[score_col].max()) * 10

            df_clean = df_clean.rename(columns={score_col: 'happiness_score'})
            logger.info(f"  Found happiness score: {score_col}")

        # Find location/country
        loc_cols = [col for col in df_clean.columns if 'country' in col or 'location' in col]
        if loc_cols and 'location' not in df_clean.columns:
            df_clean = df_clean.rename(columns={loc_cols[0]: 'location'})

        logger.info(f"  Result: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
        return df_clean

    def clean_cost_of_living_data(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Clean cost of living datasets"""
        logger.info(f"Cleaning cost of living data: {filename}")

        df_clean = df.copy()

        # Standardize column names
        df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

        # Find cost index
        cost_cols = [col for col in df_clean.columns if 'cost' in col or 'index' in col]
        if cost_cols:
            cost_col = cost_cols[0]

            # Convert to numeric
            if df_clean[cost_col].dtype == 'object':
                df_clean[cost_col] = pd.to_numeric(
                    df_clean[cost_col].str.replace('[^0-9.]', '', regex=True),
                    errors='coerce'
                )

            df_clean = df_clean.rename(columns={cost_col: 'cost_of_living_index'})
            logger.info(f"  Found cost index: {cost_col}")

        # Find location/country
        loc_cols = [col for col in df_clean.columns if 'country' in col or 'city' in col or 'location' in col]
        if loc_cols and 'location' not in df_clean.columns:
            df_clean = df_clean.rename(columns={loc_cols[0]: 'location'})

        logger.info(f"  Result: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
        return df_clean

    def clean_job_satisfaction_data(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Clean job satisfaction datasets"""
        logger.info(f"Cleaning job satisfaction data: {filename}")

        df_clean = df.copy()

        # Standardize column names
        df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')

        # Find satisfaction score
        satisfaction_cols = [col for col in df_clean.columns if 'satisfaction' in col]
        if satisfaction_cols:
            sat_col = satisfaction_cols[0]

            # Convert to numeric (0-10 scale)
            if df_clean[sat_col].dtype == 'object':
                df_clean[sat_col] = pd.to_numeric(df_clean[sat_col], errors='coerce')

            # Normalize to 0-10 if needed
            if df_clean[sat_col].max() > 10:
                df_clean[sat_col] = (df_clean[sat_col] / df_clean[sat_col].max()) * 10

            df_clean = df_clean.rename(columns={sat_col: 'job_satisfaction'})

        # Find profession/job
        job_cols = [col for col in df_clean.columns if 'profession' in col or 'job' in col or 'occupation' in col]
        if job_cols and 'job_title' not in df_clean.columns:
            df_clean = df_clean.rename(columns={job_cols[0]: 'job_title'})

        logger.info(f"  Result: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")
        return df_clean

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values appropriately"""

        # Drop rows with missing target variables
        target_cols = ['salary_usd', 'happiness_score', 'job_satisfaction']
        existing_targets = [col for col in target_cols if col in df.columns]

        if existing_targets:
            before = len(df)
            df = df.dropna(subset=existing_targets, how='all')
            dropped = before - len(df)
            if dropped > 0:
                logger.info(f"  Dropped {dropped} rows with missing target values")

        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)

        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df[col] = df[col].fillna(mode_val)

        return df

    def process_all_datasets(self):
        """Process all loaded datasets"""
        logger.info("=" * 80)
        logger.info("PROCESSING DATASETS")
        logger.info("=" * 80 + "\n")

        for filename, df in self.datasets.items():
            try:
                # Determine dataset type and clean accordingly
                if any(keyword in filename.lower() for keyword in ['salary', 'ai_job', 'income']):
                    df_processed = self.clean_salary_data(df, filename)
                elif any(keyword in filename.lower() for keyword in ['happiness', 'world']):
                    df_processed = self.clean_happiness_data(df, filename)
                elif any(keyword in filename.lower() for keyword in ['cost', 'living']):
                    df_processed = self.clean_cost_of_living_data(df, filename)
                elif 'satisfaction' in filename.lower():
                    df_processed = self.clean_job_satisfaction_data(df, filename)
                else:
                    # Generic cleaning
                    df_processed = df.copy()
                    df_processed.columns = df_processed.columns.str.lower().str.replace(' ', '_')
                    logger.info(f"Generic cleaning: {filename}")

                # Handle missing values
                df_processed = self.handle_missing_values(df_processed)

                # Store processed data
                self.processed_data[filename] = df_processed

                # Save to processed directory
                output_filename = f"cleaned_{filename}"
                output_path = self.processed_dir / output_filename
                df_processed.to_csv(output_path, index=False)
                logger.info(f"  ✓ Saved to {output_filename}\n")

            except Exception as e:
                logger.error(f"  ✗ Error processing {filename}: {e}\n")

    def create_merged_dataset(self) -> Optional[pd.DataFrame]:
        """Create a unified dataset for ML training"""
        logger.info("=" * 80)
        logger.info("CREATING MERGED DATASET")
        logger.info("=" * 80 + "\n")

        # Find datasets with salary data
        salary_datasets = []
        for name, df in self.processed_data.items():
            if 'salary_usd' in df.columns:
                logger.info(f"Found salary data in: {name}")
                salary_datasets.append(df)

        if not salary_datasets:
            logger.warning("No datasets with salary data found!")
            return None

        # Merge salary datasets
        logger.info("\nMerging salary datasets...")
        merged = pd.concat(salary_datasets, axis=0, ignore_index=True)

        # Select key columns for ML
        key_columns = [
            'salary_usd', 'years_experience', 'education_level',
            'location', 'job_title', 'job_satisfaction'
        ]

        available_columns = [col for col in key_columns if col in merged.columns]
        merged_ml = merged[available_columns].copy()

        # Remove duplicates
        before = len(merged_ml)
        merged_ml = merged_ml.drop_duplicates()
        removed = before - len(merged_ml)
        logger.info(f"Removed {removed} duplicate rows")

        # Final cleaning
        merged_ml = merged_ml.dropna(subset=['salary_usd'])

        logger.info(f"\nMerged dataset shape: {merged_ml.shape}")
        logger.info(f"Columns: {list(merged_ml.columns)}")

        # Save merged dataset
        merged_path = self.processed_dir / "merged_ml_dataset.csv"
        merged_ml.to_csv(merged_path, index=False)
        logger.info(f"✓ Saved merged dataset to {merged_path}\n")

        return merged_ml

    def generate_summary_report(self):
        """Generate summary statistics for processed data"""
        logger.info("=" * 80)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 80 + "\n")

        logger.info(f"Total datasets processed: {len(self.processed_data)}")
        logger.info(f"Output directory: {self.processed_dir}")

        total_rows = sum(len(df) for df in self.processed_data.values())
        logger.info(f"Total rows processed: {total_rows:,}")

        # Count datasets by type
        salary_count = sum(1 for df in self.processed_data.values() if 'salary_usd' in df.columns)
        happiness_count = sum(1 for df in self.processed_data.values() if 'happiness_score' in df.columns)
        satisfaction_count = sum(1 for df in self.processed_data.values() if 'job_satisfaction' in df.columns)

        logger.info(f"\nDataset breakdown:")
        logger.info(f"  - Salary datasets: {salary_count}")
        logger.info(f"  - Happiness datasets: {happiness_count}")
        logger.info(f"  - Job satisfaction datasets: {satisfaction_count}")

        logger.info("\n" + "=" * 80)
        logger.info("✓ Data preprocessing complete!")
        logger.info("Next steps:")
        logger.info("1. Run EDA and visualization (explore_data.py)")
        logger.info("2. Encode categorical variables")
        logger.info("3. Train ML models")
        logger.info("=" * 80 + "\n")

    def run_full_pipeline(self):
        """Run complete preprocessing pipeline"""
        self.load_all_datasets()

        if not self.datasets:
            logger.error("No datasets loaded. Exiting.")
            return

        self.process_all_datasets()
        self.create_merged_dataset()
        self.generate_summary_report()


if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.run_full_pipeline()
