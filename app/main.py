# app/main.py - UPDATED TO USE ACTUAL CSV DATA
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Solar Potential Dashboard",
    page_icon="☀️",
    layout="wide"
)

# Title and description
st.title("🌍 West Africa Solar Potential Analysis")
st.markdown("Compare solar irradiance metrics across Benin, Sierra Leone, and Togo")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")

# Country selection
selected_countries = st.sidebar.multiselect(
    "Select Countries:",
    ["Benin", "Sierra Leone", "Togo"],
    default=["Benin", "Sierra Leone", "Togo"]
)

# Metric selection
metric = st.sidebar.selectbox(
    "Select Solar Metric:",
    ["GHI", "DNI", "DHI", "Tamb", "WS", "RH"]
)

# Data loading function
@st.cache_data
def load_country_data(country_name):
    """Load data for a specific country - tries processed first, then raw"""
    try:
        # First try processed/cleaned data
        processed_files = {
            "Benin": "data/processed/benin_clean.csv",
            "Sierra Leone": "data/processed/sierra_leone_clean.csv", 
            "Togo": "data/processed/togo_clean.csv"
        }
        
        # Then try raw data files
        raw_files = {
            "Benin": "data/raw/benin-malanville.csv",
            "Sierra Leone": "data/raw/sierraleone-bumbuna.csv",
            "Togo": "data/raw/togo-dapaong_qc.csv"
        }
        
        # Try processed data first
        processed_file = processed_files.get(country_name)
        if processed_file and os.path.exists(processed_file):
            df = pd.read_csv(processed_file)
            df['country'] = country_name
            st.sidebar.success(f"✓ Loaded processed data for {country_name}")
            return df
        
        # Fall back to raw data
        raw_file = raw_files.get(country_name)
        if raw_file and os.path.exists(raw_file):
            df = pd.read_csv(raw_file)
            df['country'] = country_name
            st.sidebar.info(f"📁 Loaded raw data for {country_name}")
            return df
        
        st.sidebar.warning(f"⚠ No data file found for {country_name}")
        return None
        
    except Exception as e:
        st.sidebar.error(f"❌ Error loading {country_name}: {str(e)}")
        return None

@st.cache_data
def load_all_data():
    """Load all country data"""
    countries_data = []
    loaded_countries = []
    data_sources = []
    
    for country in ["Benin", "Sierra Leone", "Togo"]:
        country_data = load_country_data(country)
        if country_data is not None:
            # Standardize column names if needed
            country_data = standardize_columns(country_data)
            countries_data.append(country_data)
            loaded_countries.append(country)
            
            # Track data source
            if "clean" in str(country_data.attrs.get('source', '')):
                data_sources.append("processed")
            else:
                data_sources.append("raw")
    
    if countries_data:
        combined_data = pd.concat(countries_data, ignore_index=True)
        source_info = " + ".join([f"{country} ({src})" for country, src in zip(loaded_countries, data_sources)])
        st.sidebar.success(f"✅ Loaded: {source_info}")
        return combined_data
    else:
        # Fallback to sample data only if no files found
        st.sidebar.error("❌ No data files found. Please check data/ directory.")
        return None

def standardize_columns(df):
    """Standardize column names across different datasets"""
    column_mapping = {
        # Temperature columns
        'T_ModA': 'ModA', 'TModA': 'ModA', 'Module_A_Temp': 'ModA',
        'T_ModB': 'ModB', 'TModB': 'ModB', 'Module_B_Temp': 'ModB',
        'T_Amb': 'Tamb', 'T_amb': 'Tamb', 'Ambient_Temp': 'Tamb',
        
        # Wind columns
        'WS': 'WS', 'Wind_Speed': 'WS',
        'WSgust': 'WSgust', 'Gust_Speed': 'WSgust',
        'WD': 'WD', 'Wind_Direction': 'WD',
        
        # Solar columns
        'GHI': 'GHI', 'Global_Irradiance': 'GHI',
        'DNI': 'DNI', 'Direct_Irradiance': 'DNI', 
        'DHI': 'DHI', 'Diffuse_Irradiance': 'DHI',
        
        # Other environmental
        'RH': 'RH', 'Relative_Humidity': 'RH',
        'BP': 'BP', 'Barometric_Pressure': 'BP'
    }
    
    # Rename columns if they exist in mapping
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    return df

def create_sample_data():
    """Create minimal sample data as last resort"""
    st.sidebar.warning("🔄 Using sample data for demonstration")
    sample_data = []
    for country in ["Benin", "Sierra Leone", "Togo"]:
        n_samples = 200
        sample_df = pd.DataFrame({
            'GHI': np.random.normal(500, 100, n_samples),
            'DNI': np.random.normal(400, 80, n_samples),
            'DHI': np.random.normal(150, 40, n_samples),
            'Tamb': np.random.normal(28, 5, n_samples),
            'WS': np.random.normal(3, 1.5, n_samples),
            'RH': np.random.normal(65, 15, n_samples),
            'country': country
        })
        sample_data.append(sample_df)
    return pd.concat(sample_data, ignore_index=True)

# Load the data
data = load_all_data()

# If no data loaded, use sample as last resort
if data is None:
    data = create_sample_data()

# Display data info
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Records:** {len(data):,}")
st.sidebar.markdown(f"**Countries:** {', '.join(data['country'].unique())}")
st.sidebar.markdown(f"**Available Metrics:** {', '.join([col for col in ['GHI', 'DNI', 'DHI', 'Tamb', 'WS', 'RH'] if col in data.columns])}")

# Main dashboard content
if data is not None and not data.empty:
    # Filter data based on selection
    filtered_data = data[data['country'].isin(selected_countries)]
    
    if filtered_data.empty:
        st.warning("No data available for selected countries")
    else:
        # Create two columns for layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"{metric} Distribution")
            
            # Boxplot
            fig, ax = plt.subplots(figsize=(10, 6))
            if metric in filtered_data.columns:
                sns.boxplot(data=filtered_data, x='country', y=metric, ax=ax)
                ax.set_title(f'{metric} Distribution by Country')
                ax.set_ylabel(f'{metric} (W/m²)' if metric in ['GHI', 'DNI', 'DHI'] else 
                             f'{metric} (°C)' if metric == 'Tamb' else
                             f'{metric} (m/s)' if metric == 'WS' else
                             f'{metric} (%)' if metric == 'RH' else metric)
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning(f"Metric '{metric}' not found in data")
        
        with col2:
            st.subheader("Country Comparison")
            
            # Summary statistics table
            if metric in filtered_data.columns:
                stats_table = filtered_data.groupby('country')[metric].agg(['mean', 'median', 'std', 'count']).round(2)
                st.dataframe(stats_table.style.background_gradient(cmap='Blues'))
                
                # Data quality indicator
                total_records = stats_table['count'].sum()
                missing_percent = ((len(filtered_data) - total_records) / len(filtered_data)) * 100
                if missing_percent > 10:
                    st.info(f"ℹ️ Data quality: {missing_percent:.1f}% missing values for {metric}")
            else:
                st.warning(f"Metric '{metric}' not found in data")
        
        # Additional visualizations
        if metric in filtered_data.columns and len(filtered_data[metric].dropna()) > 0:
            st.subheader("Detailed Analysis")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Histogram comparison
                st.markdown("**Distribution Comparison**")
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                for i, country in enumerate(selected_countries):
                    country_data = filtered_data[filtered_data['country'] == country][metric].dropna()
                    if len(country_data) > 0:
                        ax.hist(country_data, alpha=0.7, label=country, 
                               bins=30, color=colors[i % len(colors)])
                ax.set_xlabel(metric)
                ax.set_ylabel('Frequency')
                ax.legend()
                ax.set_title(f'{metric} Distribution by Country')
                st.pyplot(fig)
            
            with col4:
                # Ranking chart
                st.markdown("**Country Ranking**")
                ranking_data = filtered_data.groupby('country')[metric].mean().sort_values(ascending=True)
                if len(ranking_data) > 0:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(ranking_data)]
                    bars = ax.barh(range(len(ranking_data)), ranking_data.values, color=colors)
                    ax.set_yticks(range(len(ranking_data)))
                    ax.set_yticklabels(ranking_data.index)
                    ax.set_xlabel(f'Average {metric}')
                    ax.set_title(f'Country Ranking by {metric}')
                    
                    # Add value labels on bars
                    for i, (bar, value) in enumerate(zip(bars, ranking_data.values)):
                        ax.text(value + (ranking_data.max() * 0.01), i, 
                               f'{value:.1f}', va='center', fontweight='bold')
                    
                    st.pyplot(fig)
                else:
                    st.warning("No data available for ranking")
            
            # Key insights section
            st.subheader("📊 Key Insights")
            
            # Calculate insights dynamically
            if len(selected_countries) > 0:
                country_stats = filtered_data.groupby('country')[metric].agg(['mean', 'std', 'count']).round(2)
                if len(country_stats) > 0:
                    best_country = country_stats['mean'].idxmax()
                    best_value = country_stats['mean'].max()
                    worst_country = country_stats['mean'].idxmin()
                    worst_value = country_stats['mean'].min()
                    
                    if len(country_stats) > 1:
                        most_consistent = country_stats['std'].idxmin()
                        most_variable = country_stats['std'].idxmax()
                        
                        st.markdown(f"""
                        **Performance Summary:**
                        
                        • 🥇 **{best_country}** has the highest average {metric} (**{best_value:.1f}**)
                        • 📊 **{most_consistent}** shows the most consistent {metric} values
                        • 🔍 **{most_variable}** has the most variable {metric} readings
                        • 📈 Consider **{best_country}** for solar projects requiring high {metric}
                        • 🎯 **{most_consistent}** may be better for predictable energy output
                        """)
                    else:
                        st.markdown(f"""
                        **Single Country Analysis:**
                        
                        • 📊 **{best_country}** has average {metric} of **{best_value:.1f}**
                        • 📈 Standard deviation: **{country_stats['std'].iloc[0]:.1f}**
                        • 📋 Total records: **{country_stats['count'].iloc[0]:,}**
                        """)
                else:
                    st.warning("Insufficient data for insights")

# Footer
st.markdown("---")
st.markdown("**Solar Challenge Dashboard** • Built with Streamlit • Using actual meteorological data from Benin, Sierra Leone, and Togo")

# Data status in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Files Status")

# Check both raw and processed files
data_files = {
    'Benin (Raw)': 'data/raw/benin-malanville.csv',
    'Benin (Processed)': 'data/processed/benin_clean.csv',
    'Sierra Leone (Raw)': 'data/raw/sierraleone-bumbuna.csv',
    'Sierra Leone (Processed)': 'data/processed/sierra_leone_clean.csv',
    'Togo (Raw)': 'data/raw/togo-dapaong_qc.csv',
    'Togo (Processed)': 'data/processed/togo_clean.csv'
}

for file_desc, filepath in data_files.items():
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        st.sidebar.success(f"✓ {file_desc} ({file_size:.1f} KB)")
    else:
        st.sidebar.error(f"✗ {file_desc}")