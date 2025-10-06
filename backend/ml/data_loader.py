"""
Data Loader for ML Pipeline

Loads and preprocesses datasets for model training.
optional - the prediction service works with feature engineering.
"""

import logging
from typing import Optional, List
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

class MLDataLoader:
    """Load and preprocess ML training datasets from CSV files"""

    def __init__(self, data_dir: str = "ml/data"):
        """
        Initialize data loader

        Args:
            data_dir: Directory containing CSV datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ML Data Loader initialized with data directory: {self.data_dir}")

    def load_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load a CSV file from the data directory

        Args:
            filename: Name of the CSV file 

        Returns:
            DataFrame or None if file not found
        """
        file_path = self.data_dir / filename

        if not file_path.exists():
            logger.error(f"CSV file not found: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} records from {filename}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV {filename}: {e}")
            return None

    def load_salary_data(self, filename: str = "salaries.csv") -> Optional[pd.DataFrame]:
        """
        Load and preprocess salary dataset

        Args:
            filename: CSV filename in data directory

        Returns:
            Preprocessed DataFrame or None
        """
        df = self.load_csv(filename)
        if df is None:
            return None

        # Basic preprocessing
        df = self._preprocess_salary_data(df)
        return df

    def load_happiness_data(self, filename: str = "happiness.csv") -> Optional[pd.DataFrame]:
        """
        Load happiness dataset

        Args:
            filename: CSV filename in data directory

        Returns:
            DataFrame or None
        """
        return self.load_csv(filename)

    def _preprocess_salary_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess salary dataset"""
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Remove missing values in salary columns
        salary_cols = [col for col in df.columns if 'salary' in col.lower()]
        if salary_cols:
            df = df.dropna(subset=[salary_cols[0]])

            # Remove outliers (salary beyond reasonable range)
            if 'salary_in_usd' in df.columns or 'salary' in df.columns:
                salary_col = 'salary_in_usd' if 'salary_in_usd' in df.columns else 'salary'
                df = df[
                    (df[salary_col] > 10000) &
                    (df[salary_col] < 1000000)
                ]

        logger.info(f"Preprocessed salary data: {len(df)} records")
        return df

    def list_csv_files(self) -> List[str]:
        """List all CSV files in the data directory"""
        return [f.name for f in self.data_dir.glob("*.csv")]

