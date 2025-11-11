# app/main.py - COMPLETE STANDALONE VERSION
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
    ["GHI", "DNI", "DHI", "Tamb"]
)

# Data loading function
@st.cache_data
def load_country_data(country_name):
    """Load cleaned data for a specific country"""
    try:
        # Try different filename patterns
        filename_patterns = [
            f'data/processed/{country_name.lower().replace(" ", "_")}_clean.csv',
            f'data/processed/{country_name.lower()}_clean.csv',
            f'data/processed/{country_name}_clean.csv'
        ]
        
        for filepath in filename_patterns:
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['country'] = country_name
                st.sidebar.success(f"✓ Loaded {country_name} data")
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
    
    for country in ["Benin", "Sierra Leone", "Togo"]:
        country_data = load_country_data(country)
        if country_data is not None:
            countries_data.append(country_data)
            loaded_countries.append(country)
    
    if countries_data:
        combined_data = pd.concat(countries_data, ignore_index=True)
        st.sidebar.success(f"✅ Loaded data for {', '.join(loaded_countries)}")
        return combined_data
    else:
        # Return sample data if no files found
        st.sidebar.warning("📊 Using sample data for demonstration")
        sample_data = []
        for country in ["Benin", "Sierra Leone", "Togo"]:
            n_samples = 500
            sample_df = pd.DataFrame({
                'GHI': np.random.normal(500 + np.random.randint(-50, 50), 100, n_samples),
                'DNI': np.random.normal(600 + np.random.randint(-50, 50), 150, n_samples),
                'DHI': np.random.normal(300 + np.random.randint(-50, 50), 80, n_samples),
                'Tamb': np.random.normal(25 + np.random.randint(-5, 5), 5, n_samples),
                'WS': np.random.normal(3, 1, n_samples),
                'RH': np.random.normal(60, 15, n_samples),
                'country': country
            })
            sample_data.append(sample_df)
        return pd.concat(sample_data, ignore_index=True)

# Load the data
data = load_all_data()

# Display data info
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Records:** {len(data):,}")
st.sidebar.markdown(f"**Countries:** {', '.join(data['country'].unique())}")

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
                ax.set_ylabel(f'{metric} (W/m²)' if metric != 'Tamb' else 'Temperature (°C)')
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
            else:
                st.warning(f"Metric '{metric}' not found in data")
        
        # Additional visualizations
        if metric in filtered_data.columns:
            st.subheader("Detailed Analysis")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Histogram comparison
                st.markdown("**Distribution Comparison**")
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                for i, country in enumerate(selected_countries):
                    country_data = filtered_data[filtered_data['country'] == country][metric]
                    ax.hist(country_data.dropna(), alpha=0.7, label=country, 
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
            
            # Key insights section
            st.subheader("📊 Key Insights")
            
            # Calculate insights dynamically
            if len(selected_countries) > 0:
                country_stats = filtered_data.groupby('country')[metric].agg(['mean', 'std', 'count']).round(2)
                best_country = country_stats['mean'].idxmax()
                best_value = country_stats['mean'].max()
                worst_country = country_stats['mean'].idxmin()
                worst_value = country_stats['mean'].min()
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

# Footer
st.markdown("---")
st.markdown("**Solar Challenge Dashboard** • Built with Streamlit • Data: Cleaned meteorological data")

# Data status in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Files Status")
data_files = {
    'Benin': 'data/processed/benin_clean.csv',
    'Sierra Leone': 'data/processed/sierra_leone_clean.csv', 
    'Togo': 'data/processed/togo_clean.csv'
}

for country, filepath in data_files.items():
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath) / 1024  # Size in KB
        st.sidebar.success(f"✓ {country} ({file_size:.1f} KB)")
    else:
        st.sidebar.error(f"✗ {country} (file missing)")