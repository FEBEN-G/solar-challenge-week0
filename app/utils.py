# app/utils.py
import pandas as pd
import numpy as np

def load_country_data(country_name):
    """Load cleaned data for a specific country"""
    try:
        df = pd.read_csv(f'data/processed/{country_name.lower()}_clean.csv')
        df['country'] = country_name
        return df
    except FileNotFoundError:
        print(f"Data for {country_name} not found")
        return None

def calculate_statistics(df, metric):
    """Calculate summary statistics for a given metric"""
    if metric not in df.columns:
        return None
    
    return {
        'mean': df[metric].mean(),
        'median': df[metric].median(),
        'std': df[metric].std(),
        'min': df[metric].min(),
        'max': df[metric].max()
    }

def generate_insights(df, metric):
    """Generate automated insights based on data"""
    stats = calculate_statistics(df, metric)
    if not stats:
        return "No data available"
    
    return f"""
    Average {metric}: {stats['mean']:.2f}
    Variability (std): {stats['std']:.2f}
    Range: {stats['min']:.2f} - {stats['max']:.2f}
    """