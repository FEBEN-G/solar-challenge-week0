# src/data_utils.py
import pandas as pd
import numpy as np
from scipy import stats

def load_country_data(filepath):
    """Load country solar data"""
    df = pd.read_csv(filepath)
    print(f"Loaded data: {df.shape}")
    return df

def detect_outliers_zscore(df, columns, threshold=3):
    """Detect outliers using Z-score method"""
    outliers = {}
    for col in columns:
        if col in df.columns:
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            outliers[col] = (z_scores > threshold).sum()
    return outliers

def generate_missing_report(df):
    """Generate missing value report"""
    missing_count = df.isna().sum()
    missing_percent = (missing_count / len(df)) * 100
    return pd.DataFrame({
        'missing_count': missing_count,
        'missing_percent': missing_percent
    })