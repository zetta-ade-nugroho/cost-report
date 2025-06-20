import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import re
import pycountry
import ast

# Page configuration
st.set_page_config(
    page_title="Job Analytics Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_salary_data(df):
    """Clean and extract salary information"""
    if 'job_salary' in df.columns:
        # Extract numeric values from salary strings
        def extract_salary_range(salary_str):
            if pd.isna(salary_str) or salary_str == '':
                return None, None
# def clean_salary_data(df):
#     """Clean and extract salary information"""
#     if 'job_salary' in df.columns:
#         # Extract numeric values from salary strings
#         def extract_salary_range(salary_str):
#             if pd.isna(salary_str) or salary_str == '':
#                 return None, None
            
            # Remove common currency symbols and text
            clean_str = str(salary_str).replace('$', '').replace(',', '').replace('K', '000').replace('k', '000')
            numbers = re.findall(r'\d+', clean_str)
#             # Remove common currency symbols and text
#             clean_str = str(salary_str).replace('$', '').replace(',', '').replace('K', '000').replace('k', '000')
#             numbers = re.findall(r'\d+', clean_str)
            
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                return int(numbers[0]), int(numbers[0])
            return None, None
#             if len(numbers) >= 2:
#                 return int(numbers[0]), int(numbers[1])
#             elif len(numbers) == 1:
#                 return int(numbers[0]), int(numbers[0])
#             return None, None
        
        df['salary_min'], df['salary_max'] = zip(*df['job_salary'].apply(extract_salary_range))
        df['salary_avg'] = df[['salary_min', 'salary_max']].mean(axis=1)
#         df['salary_min'], df['salary_max'] = zip(*df['job_salary'].apply(extract_salary_range))
#         df['salary_avg'] = df[['salary_min', 'salary_max']].mean(axis=1)
    
    return df
#     return df

def load_and_process_data(uploaded_file):
    """Load and process the CSV data"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Process dates
        date_columns = ['scrapped_on_date', 'publication_date', 'date_of_publication', 'start_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean salary data
        df = clean_salary_data(df)
        # # Clean salary data
        # df = clean_salary_data(df)
        
        # Clean company size data
        if 'company_size' in df.columns:
            df['company_size_clean'] = df['company_size'].fillna('Unknown')
        
        # Clean remote working data
        if 'remote_working' in df.columns:
            def clean_remote_working(value):
                if pd.isna(value):
                    return False
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    return value_lower in ['true', '1', 'yes', 'remote', 'y']
                if isinstance(value, (int, float)):
                    return bool(value)
                return False
            
            df['remote_working'] = df['remote_working'].apply(clean_remote_working)
        
        # Clean company rating data
        if 'company_rating' in df.columns:
            df['company_rating'] = pd.to_numeric(df['company_rating'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def show_overview_metrics(df):
    """Display key metrics overview"""
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Jobs", f"{len(df):,}")
    
    with col2:
        unique_companies = df['company'].nunique() if 'company' in df.columns else 0
        st.metric("Companies", f"{unique_companies:,}")
    
    with col3:
        unique_locations = df['location'].nunique() if 'location' in df.columns else 0
        st.metric("Locations", f"{unique_locations:,}")
    
    with col4:
        remote_jobs = len(df[df['remote_working'] == True]) if 'remote_working' in df.columns else 0
        st.metric("Remote Jobs", f"{remote_jobs:,}")
    
    with col5:
        avg_salary = df['salary_avg'].mean() if 'salary_avg' in df.columns else 0
        if avg_salary > 0:
            st.metric("Avg Salary", f"${avg_salary:,.0f}")
        else:
            st.metric("Avg Salary", "N/A")
    # with col5:
    #     avg_salary = df['salary_avg'].mean() if 'salary_avg' in df.columns else 0
    #     if avg_salary > 0:
    #         st.metric("Avg Salary", f"${avg_salary:,.0f}")
    #     else:
    #         st.metric("Avg Salary", "N/A")

def show_job_trends(df):
    """Show job posting trends over time"""
    st.subheader("📈 Job Posting Trends")
    
    # Use the most appropriate date column
    date_col = None
    for col in ['publication_date', 'date_of_publication', 'scrapped_on_date']:
        if col in df.columns and not df[col].isna().all():
            date_col = col
            break
    
    if date_col:
        # Create daily job postings chart
        daily_jobs = df[df[date_col].notna()].groupby(df[date_col].dt.date).size().reset_index()
        daily_jobs.columns = ['date', 'job_count']
        
        fig = px.line(daily_jobs, x='date', y='job_count', 
                     title="Daily Job Postings",
                     labels={'job_count': 'Number of Jobs', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid date information found for trend analysis")

import streamlit as st
import plotly.express as px
import pycountry

# ------------------------------
# 🌍 ISO Code Mapper
# ------------------------------
def get_iso3(country_name):
    """Map country name to ISO Alpha-3 code using pycountry"""
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

# ------------------------------
# 📊 Location-Based Analysis
# ------------------------------

# ------------------------------
# 🌍 Location Analysis Function
# ------------------------------
def show_location_analysis(df):
    """Display location-based insights including pie charts and a choropleth map."""
    st.subheader("🌍 Location Analysis")

    # ------------------------------
    # 🔍 Step 1: Extract 'city' and 'country'
    # ------------------------------
    if 'location' in df.columns:
        df['city'] = df['location'].apply(lambda x: str(x).split(',')[0].strip() if ',' in str(x) else str(x).strip())
        df['country'] = df['location'].apply(lambda x: str(x).split(',')[-1].strip() if ',' in str(x) else str(x).strip())

    # ------------------------------
    # 🥧 Step 2: Top 5 Pie Charts
    # ------------------------------
    col1, col2 = st.columns(2)

    with col1:
        top_countries = df['country'].value_counts().head(5)
        fig_country = px.pie(
            values=top_countries.values,
            names=top_countries.index,
            title="Top 5 Countries by Job Count"
        )
        st.plotly_chart(fig_country, use_container_width=True)

    with col2:
        top_cities = df['city'].value_counts().head(5)
        fig_city = px.pie(
            values=top_cities.values,
            names=top_cities.index,
            title="Top 5 Cities by Job Count"
        )
        st.plotly_chart(fig_city, use_container_width=True)

    # ------------------------------
    # 🗺️ Step 3: Choropleth Map (Global Distribution)
    # ------------------------------
    st.subheader("🗺️ Global Job Distribution")

    # Prepare country distribution data with ISO mapping
    # Step 1: Prepare the data
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts['iso_alpha'] = country_counts['country'].apply(get_iso3)
    country_counts = country_counts.dropna(subset=['iso_alpha'])

    # Step 2: Log-transform the job counts for coloring
    country_counts['log_count'] = country_counts['count'].apply(lambda x: np.log1p(x))  # log(1 + x)

    # Step 3: Create the choropleth
    fig_map = px.choropleth(
        country_counts,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="log_count",  # Use log-transformed value for coloring
        hover_name="country",
        hover_data={
            "count": True,        # Show actual job count
            "log_count": False,   # Hide log-transformed value from hover
            "iso_alpha": False    # Hide ISO code
        },
        color_continuous_scale="YlOrRd",  # Or "Blues", "OrRd", etc.
        title="📍 Jobs by Country (Log Scaled Color)"
    )

    # Step 4: Customize the map style
    fig_map.update_geos(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        showland=True,
        landcolor='White',
        oceancolor='LightBlue',
    )

    # Step 5: Show actual count in color bar
    # Add tickvals/ticktext if you want fixed steps too
    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar={
            'title': 'Job Count (log-scaled color)',
            'tickvals': [np.log1p(x) for x in [1, 10, 100, 1000, 10000]],
            'ticktext': ['1', '10', '100', '1,000', '10,000'],
            'ticksuffix': ' jobs'
        }
    )

    # Step 6: Display in Streamlit
    st.plotly_chart(fig_map, use_container_width=True)

    # ------------------------------
    # 📍 Step 4: GPS-Based Scatter Map
    # ------------------------------
    st.subheader("📌 Exact Location Map (GPS Points)")

    def extract_valid_coords(row):
        job_id = row.name
        try:
            coords_list = ast.literal_eval(row['location_detail'])
            valid_coords = [c for c in coords_list if c and None not in c]
            return [(job_id, c[0], c[1], row.get('location', None), row.get('country', None)) for c in valid_coords]
        except:
            return []

    # Flatten coordinates into a new DataFrame
    all_coords = []
    for _, row in df.iterrows():
        all_coords.extend(extract_valid_coords(row))

    if all_coords:
        geo_df = pd.DataFrame(all_coords, columns=['job_id', 'latitude', 'longitude', 'location', 'country'])

        fig_gps = px.scatter_mapbox(
            geo_df,
            lat="latitude",
            lon="longitude",
            hover_name="location",
            hover_data=["country"],
            zoom=1,
            height=600,
            color_discrete_sequence=["#636EFA"]
        )

        fig_gps.update_layout(
            mapbox_style="open-street-map",
            title="📍 Jobs with Precise GPS (Mapbox)",
            margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )

        st.plotly_chart(fig_gps, use_container_width=True)
    else:
        st.info("No valid GPS coordinates found in `location_detail`.")

def show_company_analysis(df):
    """Show company-based analysis"""
    st.subheader("🏢 Company Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'company' in df.columns:
            # Top hiring companies
            top_companies = df['company'].value_counts().head(10)
            fig = px.bar(x=top_companies.values, y=top_companies.index,
                        orientation='h', title="Top 10 Hiring Companies",
                        labels={'x': 'Number of Jobs', 'y': 'Company'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'company_size_clean' in df.columns:
            # Company size distribution
            size_dist = df['company_size_clean'].value_counts()
            fig = px.pie(values=size_dist.values, names=size_dist.index,
                        title="Distribution by Company Size")
            st.plotly_chart(fig, use_container_width=True)

def show_salary_analysis(df):
    """Show salary analysis"""
    st.subheader("💰 Salary Analysis")
    
    if 'salary_avg' in df.columns and not df['salary_avg'].isna().all():
        col1, col2 = st.columns(2)
        
        with col1:
            # Salary distribution
            salary_data = df[df['salary_avg'].notna() & (df['salary_avg'] > 0)]
            if len(salary_data) > 0:
                fig = px.histogram(salary_data, x='salary_avg', nbins=30,
                                 title="Salary Distribution",
                                 labels={'salary_avg': 'Average Salary ($)', 'count': 'Number of Jobs'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Salary by job role
            if 'job_role' in df.columns:
                salary_by_role = df[df['salary_avg'].notna() & (df['salary_avg'] > 0)].groupby('job_role')['salary_avg'].mean().sort_values(ascending=False).head(10)
                if len(salary_by_role) > 0:
                    fig = px.bar(x=salary_by_role.values, y=salary_by_role.index,
                               orientation='h', title="Average Salary by Job Role (Top 10)",
                               labels={'x': 'Average Salary ($)', 'y': 'Job Role'})
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No salary data available for analysis")

def show_skills_analysis(df):
    """Show skills analysis"""
    st.subheader("🛠️ Skills Analysis")
    
    if 'skills_needed' in df.columns:
        # Extract and count skills
        all_skills = []
        for skills_str in df['skills_needed'].dropna():
            if isinstance(skills_str, str):
                # Split by common delimiters
                skills = re.split(r'[,;|\n]', skills_str)
                all_skills.extend([skill.strip().lower() for skill in skills if skill.strip()])
        
        if all_skills:
            from collections import Counter
            skill_counts = Counter(all_skills)
            top_skills = dict(skill_counts.most_common(20))
# def show_salary_analysis(df):
#     """Show salary analysis"""
#     st.subheader("💰 Salary Analysis")
    
#     if 'salary_avg' in df.columns and not df['salary_avg'].isna().all():
#         col1, col2 = st.columns(2)
        
#         with col1:
#             # Salary distribution
#             salary_data = df[df['salary_avg'].notna() & (df['salary_avg'] > 0)]
#             if len(salary_data) > 0:
#                 fig = px.histogram(salary_data, x='salary_avg', nbins=30,
#                                  title="Salary Distribution",
#                                  labels={'salary_avg': 'Average Salary ($)', 'count': 'Number of Jobs'})
#                 st.plotly_chart(fig, use_container_width=True)
        
#         with col2:
#             # Salary by job role
#             if 'job_role' in df.columns:
#                 salary_by_role = df[df['salary_avg'].notna() & (df['salary_avg'] > 0)].groupby('job_role')['salary_avg'].mean().sort_values(ascending=False).head(10)
#                 if len(salary_by_role) > 0:
#                     fig = px.bar(x=salary_by_role.values, y=salary_by_role.index,
#                                orientation='h', title="Average Salary by Job Role (Top 10)",
#                                labels={'x': 'Average Salary ($)', 'y': 'Job Role'})
#                     fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#                     st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info("No salary data available for analysis")

# def show_skills_analysis(df):
#     """Show skills analysis"""
#     st.subheader("🛠️ Skills Analysis")
    
#     if 'skills_needed' in df.columns:
#         # Extract and count skills
#         all_skills = []
#         for skills_str in df['skills_needed'].dropna():
#             if isinstance(skills_str, str):
#                 # Split by common delimiters
#                 skills = re.split(r'[,;|\n]', skills_str)
#                 all_skills.extend([skill.strip().lower() for skill in skills if skill.strip()])
        
#         if all_skills:
#             from collections import Counter
#             skill_counts = Counter(all_skills)
#             top_skills = dict(skill_counts.most_common(20))
            
            fig = px.bar(x=list(top_skills.values()), y=list(top_skills.keys()),
                        orientation='h', title="Top 20 Required Skills",
                        labels={'x': 'Frequency', 'y': 'Skill'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skills data available for analysis")
    else:
        st.info("Skills column not found in the dataset")
#             fig = px.bar(x=list(top_skills.values()), y=list(top_skills.keys()),
#                         orientation='h', title="Top 20 Required Skills",
#                         labels={'x': 'Frequency', 'y': 'Skill'})
#             fig.update_layout(yaxis={'categoryorder': 'total ascending'})
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("No skills data available for analysis")
#     else:
#         st.info("Skills column not found in the dataset")

def show_source_comparison(df):
    """Show comprehensive job source comparison analysis"""
    st.subheader("🔄 Job Source Comparison")
    
    if 'source' not in df.columns:
        st.warning("No 'source' column found in the dataset")
        return
    
    # Source overview metrics
    st.markdown("### 📊 Source Overview")
    source_counts = df['source'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sources", len(source_counts))
    with col2:
        st.metric("Most Active Source", source_counts.index[0] if len(source_counts) > 0 else "N/A")
    with col3:
        st.metric("Jobs from Top Source", f"{source_counts.iloc[0]:,}" if len(source_counts) > 0 else "0")
    with col4:
        top_source_pct = (source_counts.iloc[0] / len(df) * 100) if len(source_counts) > 0 else 0
        st.metric("Top Source Share", f"{top_source_pct:.1f}%")
    
    # Source distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of source distribution
        fig = px.pie(values=source_counts.values, names=source_counts.index,
                    title="Job Distribution by Source")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart of top sources
        top_sources = source_counts.head(10)
        fig = px.bar(x=top_sources.values, y=top_sources.index,
                    orientation='h', title="Top 10 Job Sources",
                    labels={'x': 'Number of Jobs', 'y': 'Source'})
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Source trends over time
    st.markdown("### 📈 Source Trends Over Time")
    date_col = None
    for col in ['publication_date', 'date_of_publication', 'scrapped_on_date']:
        if col in df.columns and not df[col].isna().all():
            date_col = col
            break
    
    if date_col:
        # Create timeline chart for top sources
        top_5_sources = source_counts.head(5).index.tolist()
        df_filtered = df[df['source'].isin(top_5_sources) & df[date_col].notna()]
        
        if len(df_filtered) > 0:
            timeline_data = df_filtered.groupby([df_filtered[date_col].dt.date, 'source']).size().reset_index()
            timeline_data.columns = ['date', 'source', 'job_count']
            
            fig = px.line(timeline_data, x='date', y='job_count', color='source',
                         title="Job Posting Trends by Source (Top 5 Sources)",
                         labels={'job_count': 'Number of Jobs', 'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Source quality comparison
    st.markdown("### 🏆 Source Quality Comparison")
    
    # Calculate metrics by source
    source_metrics = []
    for source in source_counts.index:
        source_df = df[df['source'] == source]
        
        # Safe calculation for remote working percentage
        remote_pct = 0
        if 'remote_working' in df.columns:
            try:
                remote_count = source_df['remote_working'].sum()
                remote_pct = (remote_count / len(source_df) * 100) if len(source_df) > 0 else 0
            except (TypeError, ValueError):
                remote_pct = 0
        
        # Safe calculation for salary info percentage
        salary_info_pct = 0
        if 'job_salary' in df.columns:
            try:
                has_salary = (~source_df['job_salary'].isna()).sum()
                salary_info_pct = (has_salary / len(source_df) * 100) if len(source_df) > 0 else 0
            except (TypeError, ValueError):
                salary_info_pct = 0
        
        # Safe calculation for skills info percentage
        skills_info_pct = 0
        if 'skills_needed' in df.columns:
            try:
                has_skills = (~source_df['skills_needed'].isna()).sum()
                skills_info_pct = (has_skills / len(source_df) * 100) if len(source_df) > 0 else 0
            except (TypeError, ValueError):
                skills_info_pct = 0
        # # Safe calculation for salary info percentage
        # salary_info_pct = 0
        # if 'job_salary' in df.columns:
        #     try:
        #         has_salary = (~source_df['job_salary'].isna()).sum()
        #         salary_info_pct = (has_salary / len(source_df) * 100) if len(source_df) > 0 else 0
        #     except (TypeError, ValueError):
        #         salary_info_pct = 0
        
        # # Safe calculation for skills info percentage
        # skills_info_pct = 0
        # if 'skills_needed' in df.columns:
        #     try:
        #         has_skills = (~source_df['skills_needed'].isna()).sum()
        #         skills_info_pct = (has_skills / len(source_df) * 100) if len(source_df) > 0 else 0
        #     except (TypeError, ValueError):
        #         skills_info_pct = 0
        
        # Safe calculation for average salary
        avg_salary = None
        if 'salary_avg' in source_df.columns:
            try:
                avg_salary = source_df['salary_avg'].mean()
                if pd.isna(avg_salary):
                    avg_salary = None
            except (TypeError, ValueError):
                avg_salary = None
        
        # Safe calculation for company rating
        avg_rating = None
        if 'company_rating' in df.columns:
            try:
                avg_rating = source_df['company_rating'].mean()
                if pd.isna(avg_rating):
                    avg_rating = None
            except (TypeError, ValueError):
                avg_rating = None
        
        metrics = {
            'Source': source,
            'Total Jobs': len(source_df),
            'Unique Companies': source_df['company'].nunique() if 'company' in df.columns else 0,
            'Avg Company Rating': avg_rating,
            'Remote Jobs %': round(remote_pct, 1),
            'Has Salary Info %': round(salary_info_pct, 1),
            'Has Skills Info %': round(skills_info_pct, 1),
            # 'Has Salary Info %': round(salary_info_pct, 1),
            # 'Has Skills Info %': round(skills_info_pct, 1),
            'Avg Salary': avg_salary
        }
        source_metrics.append(metrics)
    
    metrics_df = pd.DataFrame(source_metrics)
    metrics_df = metrics_df.sort_values('Total Jobs', ascending=False)
    
    # Display metrics table
    st.dataframe(metrics_df, use_container_width=True)
    
    # Comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Remote work percentage by source
        if 'remote_working' in df.columns:
            remote_by_source = df.groupby('source')['remote_working'].apply(lambda x: x.sum() / len(x) * 100).sort_values(ascending=False).head(10)
            fig = px.bar(x=remote_by_source.values, y=remote_by_source.index,
                        orientation='h', title="Remote Work % by Source (Top 10)",
                        labels={'x': 'Remote Jobs (%)', 'y': 'Source'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Salary information completeness by source
        if 'job_salary' in df.columns:
            salary_completeness = df.groupby('source')['job_salary'].apply(lambda x: (~x.isna()).sum() / len(x) * 100).sort_values(ascending=False).head(10)
            fig = px.bar(x=salary_completeness.values, y=salary_completeness.index,
                        orientation='h', title="Salary Info Completeness % by Source",
                        labels={'x': 'Has Salary Info (%)', 'y': 'Source'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Source-specific analysis selector
    st.markdown("### 🔍 Detailed Source Analysis")
    selected_sources = st.multiselect(
        "Select sources to compare in detail:",
        options=source_counts.index.tolist(),
        default=source_counts.head(3).index.tolist()
    )
    
    if selected_sources:
        # Location comparison
        st.markdown("#### 🌍 Location Distribution by Source")
        location_source_data = []
        for source in selected_sources:
            source_df = df[df['source'] == source]
            if 'location' in df.columns:
                top_locations = source_df['location'].value_counts().head(5)
                for location, count in top_locations.items():
                    location_source_data.append({
                        'Source': source,
                        'Location': location,
                        'Job Count': count
                    })
        
        if location_source_data:
            location_df = pd.DataFrame(location_source_data)
            fig = px.bar(location_df, x='Location', y='Job Count', color='Source',
                        title="Top Locations by Selected Sources",
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # Company comparison
        st.markdown("#### 🏢 Top Companies by Source")
        company_source_data = []
        for source in selected_sources:
            source_df = df[df['source'] == source]
            if 'company' in df.columns:
                top_companies = source_df['company'].value_counts().head(5)
                for company, count in top_companies.items():
                    company_source_data.append({
                        'Source': source,
                        'Company': company,
                        'Job Count': count
                    })
        
        if company_source_data:
            company_df = pd.DataFrame(company_source_data)
            fig = px.bar(company_df, x='Company', y='Job Count', color='Source',
                        title="Top Companies by Selected Sources",
                        barmode='group')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Salary comparison by source
        if 'salary_avg' in df.columns:
            st.markdown("#### 💰 Salary Comparison by Source")
            salary_comparison = []
            for source in selected_sources:
                source_df = df[(df['source'] == source) & (df['salary_avg'].notna()) & (df['salary_avg'] > 0)]
                if len(source_df) > 0:
                    salary_comparison.extend([{
                        'Source': source,
                        'Salary': salary
                    } for salary in source_df['salary_avg'].tolist()])
        # # Salary comparison by source
        # if 'salary_avg' in df.columns:
        #     st.markdown("#### 💰 Salary Comparison by Source")
        #     salary_comparison = []
        #     for source in selected_sources:
        #         source_df = df[(df['source'] == source) & (df['salary_avg'].notna()) & (df['salary_avg'] > 0)]
        #         if len(source_df) > 0:
        #             salary_comparison.extend([{
        #                 'Source': source,
        #                 'Salary': salary
        #             } for salary in source_df['salary_avg'].tolist()])
            
            if salary_comparison:
                salary_comp_df = pd.DataFrame(salary_comparison)
                fig = px.box(salary_comp_df, x='Source', y='Salary',
                           title="Salary Distribution by Source")
                st.plotly_chart(fig, use_container_width=True)
        #     if salary_comparison:
        #         salary_comp_df = pd.DataFrame(salary_comparison)
        #         fig = px.box(salary_comp_df, x='Source', y='Salary',
        #                    title="Salary Distribution by Source")
        #         st.plotly_chart(fig, use_container_width=True)

def show_job_type_analysis(df):
    """Show job type and contract analysis"""
    st.subheader("📋 Job Type & Contract Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'job_type' in df.columns:
            job_type_dist = df['job_type'].value_counts()
            fig = px.pie(values=job_type_dist.values, names=job_type_dist.index,
                        title="Job Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'job_contract' in df.columns:
            contract_dist = df['job_contract'].value_counts()
            fig = px.pie(values=contract_dist.values, names=contract_dist.index,
                        title="Contract Type Distribution")
            st.plotly_chart(fig, use_container_width=True)

def show_data_quality_report(df):
    """Show data quality metrics"""
    st.subheader("🔍 Data Quality Report")
    
    # Missing data analysis
    missing_data = df.isnull().sum()
    missing_percentage = (missing_data / len(df)) * 100
    
    quality_df = pd.DataFrame({
        'Column': missing_data.index,
        'Missing Count': missing_data.values,
        'Missing Percentage': missing_percentage.values
    }).sort_values('Missing Percentage', ascending=False)
    
    # Only show columns with missing data
    quality_df = quality_df[quality_df['Missing Count'] > 0]
    
    if len(quality_df) > 0:
        fig = px.bar(quality_df.head(15), x='Missing Percentage', y='Column',
                    orientation='h', title="Missing Data by Column (Top 15)",
                    labels={'Missing Percentage': 'Percentage Missing (%)', 'Column': 'Column Name'})
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Show the data quality table
        st.dataframe(quality_df)
    else:
        st.success("🎉 No missing data found in the dataset!")

def main():
    st.title("💼 Job Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar for file upload and filters
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader("Upload your job CSV file", type=['csv'])
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            
            # Load data
            df = load_and_process_data(uploaded_file)
            
            if df is not None:
                st.header("🔧 Filters")
                
                # Date range filter
                if any(col in df.columns for col in ['publication_date', 'date_of_publication', 'scrapped_on_date']):
                    use_date_filter = st.checkbox("Filter by date range")
                    if use_date_filter:
                        date_col = None
                        for col in ['publication_date', 'date_of_publication', 'scrapped_on_date']:
                            if col in df.columns and not df[col].isna().all():
                                date_col = col
                                break
                        
                        if date_col:
                            min_date = df[date_col].min().date()
                            max_date = df[date_col].max().date()
                            selected_dates = st.date_input(
                                "Select date range",
                                value=(min_date, max_date),
                                min_value=min_date,
                                max_value=max_date
                            )
                            
                            if len(selected_dates) == 2:
                                df = df[(df[date_col].dt.date >= selected_dates[0]) & 
                                       (df[date_col].dt.date <= selected_dates[1])]
                
                # Location filter
                if 'location' in df.columns:
                    locations = ['All'] + list(df['location'].dropna().unique())
                    selected_location = st.selectbox("Filter by location", locations)
                    if selected_location != 'All':
                        df = df[df['location'] == selected_location]
                
                # Company filter
                if 'company' in df.columns:
                    companies = ['All'] + list(df['company'].dropna().unique())
                    selected_company = st.selectbox("Filter by company", companies)
                    if selected_company != 'All':
                        df = df[df['company'] == selected_company]
                
                # Source filter
                if 'source' in df.columns:
                    sources = ['All'] + list(df['source'].dropna().unique())
                    selected_source = st.selectbox("Filter by source", sources)
                    if selected_source != 'All':
                        df = df[df['source'] == selected_source]
                
                # Remote work filter
                if 'remote_working' in df.columns:
                    remote_filter = st.selectbox("Remote work", ['All', 'Remote Only', 'Non-Remote Only'])
                    if remote_filter == 'Remote Only':
                        df = df[df['remote_working'] == True]
                    elif remote_filter == 'Non-Remote Only':
                        df = df[df['remote_working'] == False]
    
    if uploaded_file is not None and df is not None:
        # Main dashboard content
        show_overview_metrics(df)
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Trends", "🔄 Source Comparison", "🌍 Locations", "🏢 Companies", "📋 Job Types", "🔍 Data Quality"
        ])
        
        with tab1:
            show_job_trends(df)
        
        with tab2:
            show_source_comparison(df)
        
        with tab3:
            show_location_analysis(df)
        
        with tab4:
            show_company_analysis(df)
        
        # with tab5:
        #     show_salary_analysis(df)
        
        # with tab6:
        #     show_skills_analysis(df)
        
        with tab5:
            show_job_type_analysis(df)
        
        with tab6:
            show_data_quality_report(df)
        
        # Raw data view
        st.markdown("---")
        st.subheader("📋 Raw Data")
        
        # Search functionality
        search_term = st.text_input("Search in data (searches job title, company, location)")
        if search_term:
            search_mask = (
                df['summary'].str.contains(search_term, case=False, na=False) |
                df['company'].str.contains(search_term, case=False, na=False) |
                df['location'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = df[search_mask]
            st.write(f"Found {len(filtered_df)} matching records")
            st.dataframe(filtered_df)
        else:
            st.dataframe(df)
        
        # Download filtered data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name="filtered_job_data.csv",
            mime="text/csv"
        )
    
    else:
        st.info("👆 Please upload a CSV file to get started with your job analytics dashboard!")
        
        # Show sample of expected format
        st.subheader("📋 Expected CSV Format")
        st.write("Your CSV should contain job posting data with columns like:")
        st.code("""
        id, summary, job_category, standardized_level, location, company, 
        job_salary, skills_needed, remote_working, publication_date, 
        job_role, company_size, country, experience, etc.
        """)

if __name__ == "__main__":
    main()