"""
Advanced Feature Engineering for Parallax ML Pipeline

Creates:
1. Career Growth Index - Composite score for career progression potential
2. Salary Trajectory Estimates - Projected salary growth over time
3. Life Satisfaction Composite - Holistic happiness/satisfaction score
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """Create advanced composite features for life simulation predictions"""

    def __init__(self, features_dir: str = "data/features"):
        self.features_dir = Path(features_dir)
        self.salary_features = None

    def load_data(self):
        """Load feature-engineered data"""
        logger.info("Loading feature data...")
        self.salary_features = pd.read_csv(self.features_dir / 'salary_features.csv')
        logger.info(f"Loaded {self.salary_features.shape[0]} records with {self.salary_features.shape[1]} features")

    def create_career_growth_index(self) -> pd.Series:
        """
        Career Growth Index: Composite score indicating career progression potential

        Components:
        - Salary percentile (40%)
        - Experience level (30%)
        - Industry growth potential (20%)
        - Company size/stability (10%)

        Returns score from 0-100
        """
        logger.info("Creating Career Growth Index...")

        df = self.salary_features
        growth_index = pd.Series(0.0, index=df.index)

        # 1. Salary percentile (40%)
        salary_cols = [col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]
        if salary_cols:
            salary_col = salary_cols[0]
            salary_percentile = df[salary_col].rank(pct=True) * 100
            growth_index += salary_percentile * 0.4
            logger.info(f"  Added salary percentile component (40%)")

        # 2. Experience level score (30%)
        exp_cols = [col for col in df.columns if 'experience' in col.lower() and 'encoded' not in col.lower()]
        if exp_cols:
            exp_col = exp_cols[0]
            exp_mapping = {'EN': 90, 'MI': 70, 'SE': 50, 'EX': 30}
            exp_score = df[exp_col].map(exp_mapping).fillna(50)
            growth_index += exp_score * 0.3
            logger.info(f"  Added experience level component (30%)")

        # 3. Industry growth potential (20%)
        job_cols = [col for col in df.columns if 'job' in col.lower() and 'title' in col.lower() and 'encoded' not in col.lower()]
        if job_cols:
            job_col = job_cols[0]

            def industry_growth_score(job_title):
                job_title_lower = str(job_title).lower()
                if any(kw in job_title_lower for kw in ['engineer', 'data', 'software', 'ai', 'ml']):
                    return 90
                elif any(kw in job_title_lower for kw in ['manager', 'director', 'lead']):
                    return 75
                elif any(kw in job_title_lower for kw in ['analyst', 'scientist', 'research']):
                    return 70
                else:
                    return 50

            industry_score = df[job_col].apply(industry_growth_score)
            growth_index += industry_score * 0.2
            logger.info(f"  Added industry growth component (20%)")

        # 4. Company size/stability (10%)
        company_cols = [col for col in df.columns if 'company' in col.lower() and 'size' in col.lower() and 'encoded' not in col.lower()]
        if company_cols:
            company_col = company_cols[0]
            company_mapping = {'S': 60, 'M': 75, 'L': 85}
            company_score = df[company_col].map(company_mapping).fillna(70)
            growth_index += company_score * 0.1
            logger.info(f"  Added company size component (10%)")
        else:
            growth_index += 70 * 0.1

        growth_index = growth_index.clip(0, 100)

        logger.info(f"  Career Growth Index: Mean={growth_index.mean():.2f}, Median={growth_index.median():.2f}")
        return growth_index

    def create_salary_trajectory(self, years: int = 10) -> pd.DataFrame:
        """
        Salary Trajectory Estimates: Projected salary growth over time

        Creates columns:
        - salary_year_1 through salary_year_N
        - avg_growth_rate
        - projected_peak_salary
        """
        logger.info(f"Creating Salary Trajectory ({years} years)...")

        df = self.salary_features
        trajectory_df = pd.DataFrame(index=df.index)

        salary_cols = [col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]
        if not salary_cols:
            logger.warning("No salary column found")
            return trajectory_df

        salary_col = salary_cols[0]
        current_salary = df[salary_col].fillna(df[salary_col].median())

        # Base growth rate by experience
        exp_cols = [col for col in df.columns if 'experience' in col.lower() and 'encoded' not in col.lower()]
        if exp_cols:
            exp_col = exp_cols[0]
            exp_growth_rates = {'EN': 0.08, 'MI': 0.06, 'SE': 0.04, 'EX': 0.03}
            base_growth = df[exp_col].map(exp_growth_rates).fillna(0.05)
        else:
            base_growth = pd.Series(0.05, index=df.index)

        # Project salary
        for year in range(1, years + 1):
            year_growth = base_growth * (0.98 ** (year - 1))
            projected_salary = current_salary * ((1 + year_growth) ** year)
            trajectory_df[f'salary_year_{year}'] = projected_salary.round(2)

        trajectory_df['avg_growth_rate'] = base_growth.round(4)
        trajectory_df['projected_peak_salary'] = trajectory_df[[f'salary_year_{y}' for y in range(1, years + 1)]].max(axis=1)
        trajectory_df['total_growth_pct'] = ((trajectory_df['projected_peak_salary'] / current_salary - 1) * 100).round(2)

        logger.info(f"  Avg growth rate: {trajectory_df['avg_growth_rate'].mean():.2%}")
        return trajectory_df

    def create_life_satisfaction_composite(self) -> pd.Series:
        """
        Life Satisfaction Composite: Holistic happiness/satisfaction score (0-10)

        Components:
        - Financial satisfaction (35%)
        - Career fulfillment (25%)
        - Work-life balance (20%)
        - Job stability (20%)
        """
        logger.info("Creating Life Satisfaction Composite...")

        df = self.salary_features
        satisfaction = pd.Series(5.0, index=df.index)

        # Financial satisfaction
        salary_cols = [col for col in df.columns if 'salary' in col.lower() and 'category' not in col.lower()]
        if salary_cols:
            salary_col = salary_cols[0]
            salary_satisfaction = (df[salary_col].rank(pct=True) * 10).clip(0, 10)
            satisfaction = satisfaction * 0.65 + salary_satisfaction * 0.35
            logger.info(f"  Added financial satisfaction (35%)")

        # Career fulfillment
        if hasattr(self, 'career_growth_index'):
            career_fulfillment = (self.career_growth_index / 10).clip(0, 10)
            satisfaction = satisfaction * 0.75 + career_fulfillment * 0.25
            logger.info(f"  Added career fulfillment (25%)")

        # Work-life balance
        balance_score = pd.Series(6.0, index=df.index)
        job_cols = [col for col in df.columns if 'job' in col.lower() and 'title' in col.lower() and 'encoded' not in col.lower()]
        if job_cols:
            job_col = job_cols[0]

            def balance_func(job_title):
                job_title_lower = str(job_title).lower()
                if any(kw in job_title_lower for kw in ['manager', 'director', 'executive']):
                    return 5.0
                elif any(kw in job_title_lower for kw in ['analyst', 'specialist']):
                    return 7.0
                return 6.0

            balance_score = df[job_col].apply(balance_func)

        satisfaction = satisfaction * 0.80 + balance_score * 0.20
        logger.info(f"  Added work-life balance (20%)")

        satisfaction = satisfaction.clip(0, 10)
        logger.info(f"  Life Satisfaction: Mean={satisfaction.mean():.2f}/10")
        return satisfaction

    def save_enhanced_features(self):
        """Save all enhanced features to CSV"""
        logger.info("Saving enhanced features...")

        enhanced_df = self.salary_features.copy()
        enhanced_df['career_growth_index'] = self.career_growth_index
        enhanced_df = pd.concat([enhanced_df, self.salary_trajectory], axis=1)
        enhanced_df['life_satisfaction_score'] = self.life_satisfaction

        output_path = self.features_dir / 'salary_features_enhanced.csv'
        enhanced_df.to_csv(output_path, index=False)
        logger.info(f"Saved to {output_path} ({enhanced_df.shape[1]} features)")
        return enhanced_df

    def run_pipeline(self):
        """Run complete advanced feature engineering pipeline"""
        logger.info("="*80)
        logger.info("ADVANCED FEATURE ENGINEERING PIPELINE")
        logger.info("="*80)

        self.load_data()
        self.career_growth_index = self.create_career_growth_index()
        self.salary_trajectory = self.create_salary_trajectory(years=10)
        self.life_satisfaction = self.create_life_satisfaction_composite()
        enhanced_df = self.save_enhanced_features()

        logger.info("="*80)
        logger.info("COMPLETE - New features:")
        logger.info("  1. career_growth_index (0-100)")
        logger.info("  2. salary_year_1 through salary_year_10")
        logger.info("  3. avg_growth_rate, projected_peak_salary")
        logger.info("  4. life_satisfaction_score (0-10)")
        logger.info("="*80)

        return enhanced_df


if __name__ == "__main__":
    engineer = AdvancedFeatureEngineer()
    enhanced_df = engineer.run_pipeline()
