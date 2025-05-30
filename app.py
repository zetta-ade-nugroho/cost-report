import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import os

# Page configuration
st.set_page_config(
    page_title="Usage & Cost Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("📊 Analytics Dashboard")
page = st.sidebar.selectbox(
    "Select Report",
    ["🤖 OpenAI Report", "☁️ AstraDB Report"]
)

# Configuration section for file paths
st.sidebar.header("⚙️ Configuration")
with st.sidebar.expander("File Paths", expanded=False):
    openai_cost_path = st.text_input(
        "OpenAI Cost CSV Path", 
        value="cost-2025-05-01-2025-06-01.csv",
        help="Path to your OpenAI cost CSV file"
    )
    openai_activity_path = st.text_input(
        "OpenAI Activity CSV Path", 
        value="activity-2025-05-01-2025-06-01.csv",
        help="Path to your OpenAI activity CSV file"
    )
    astradb_path = st.text_input(
        "AstraDB CSV Path", 
        value="report-2025_05_29.csv",
        help="Path to your AstraDB usage CSV file"
    )

# Helper functions for loading data
@st.cache_data
def load_openai_cost_data(file_path):
    """Load and process OpenAI cost data"""
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['date'] = df['datetime'].dt.date
            df['hour'] = df['datetime'].dt.hour
        
        # Clean and process data
        if 'cost' in df.columns:
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
        
        if 'cost_in_major' in df.columns:
            df['cost_in_major'] = pd.to_numeric(df['cost_in_major'], errors='coerce')
            
        return df, None
    except Exception as e:
        return None, f"Error loading cost data: {str(e)}"

@st.cache_data
def load_openai_activity_data(file_path):
    """Load and process OpenAI activity data"""
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df['date'] = df['datetime'].dt.date
            df['hour'] = df['datetime'].dt.hour
        
        # Convert numeric columns
        numeric_columns = ['n_context_tokens_total', 'n_generated_tokens_total', 
                          'n_cached_context_tokens_total', 'n_context_audio_tokens_total',
                          'n_generated_audio_tokens_total', 'num_requests']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate total tokens
        if 'n_context_tokens_total' in df.columns and 'n_generated_tokens_total' in df.columns:
            df['total_tokens'] = df['n_context_tokens_total'].fillna(0) + df['n_generated_tokens_total'].fillna(0)
            
        return df, None
    except Exception as e:
        return None, f"Error loading activity data: {str(e)}"

@st.cache_data
def load_astradb_data(file_path):
    """Load and process AstraDB data"""
    try:
        if not os.path.exists(file_path):
            return None, f"File not found: {file_path}"
        
        df = pd.read_csv(file_path)
        
        # Convert timestamp columns if they exist
        timestamp_cols = ['BREAKDOWN_START_TIMESTAMP', 'BREAKDOWN_END_TIMESTAMP']
        for col in timestamp_cols:
            if col in df.columns:
                df[f'{col}_DATE'] = pd.to_datetime(df[col]).dt.date
        
        # Convert numeric columns
        if 'CALCULATED_COST' in df.columns:
            df['CALCULATED_COST'] = pd.to_numeric(df['CALCULATED_COST'], errors='coerce')
        if 'USAGE' in df.columns:
            df['USAGE'] = pd.to_numeric(df['USAGE'], errors='coerce')
        if 'UNIT_PRICE' in df.columns:
            df['UNIT_PRICE'] = pd.to_numeric(df['UNIT_PRICE'], errors='coerce')
            
        return df, None
    except Exception as e:
        return None, f"Error loading AstraDB data: {str(e)}"

# OpenAI Report Functions
def generate_openai_stakeholder_summary(cost_df, activity_df):
    """Generate executive summary for OpenAI usage"""
    st.header("📋 OpenAI Executive Summary")
    
    with st.container():
        st.subheader("🎯 Key Findings")
        
        # Calculate key metrics
        insights = []
        
        if cost_df is not None:
            total_cost = cost_df['cost_in_major'].sum()
            daily_avg_cost = cost_df.groupby('date')['cost_in_major'].sum().mean()
            peak_cost_day = cost_df.groupby('date')['cost_in_major'].sum().idxmax()
            peak_cost_amount = cost_df.groupby('date')['cost_in_major'].sum().max()
            
            insights.extend([
                f"💰 **Total OpenAI spend**: ${total_cost:.2f} for the analyzed period",
                f"📊 **Daily average cost**: ${daily_avg_cost:.2f}",
                f"📈 **Peak cost day**: {peak_cost_day} with ${peak_cost_amount:.2f}"
            ])
            
            if 'name' in cost_df.columns:
                top_service = cost_df.groupby('name')['cost_in_major'].sum().idxmax()
                top_service_cost = cost_df.groupby('name')['cost_in_major'].sum().max()
                top_service_pct = (top_service_cost / total_cost) * 100
                insights.append(f"🔧 **Most expensive service**: {top_service} ({top_service_pct:.1f}% of total cost)")
        
        if activity_df is not None:
            total_requests = activity_df['num_requests'].sum()
            total_tokens = activity_df['total_tokens'].sum()
            daily_avg_requests = activity_df.groupby('date')['num_requests'].sum().mean()
            
            insights.extend([
                f"🔄 **Total API requests**: {total_requests:,}",
                f"🔤 **Total tokens processed**: {total_tokens:,}",
                f"📊 **Daily average requests**: {daily_avg_requests:.0f}"
            ])
        
        if cost_df is not None and activity_df is not None:
            cost_per_request = total_cost / total_requests
            cost_per_1k_tokens = (total_cost / total_tokens) * 1000
            insights.extend([
                f"💡 **Cost per request**: ${cost_per_request:.4f}",
                f"💡 **Cost per 1,000 tokens**: ${cost_per_1k_tokens:.4f}"
            ])
        
        for insight in insights:
            st.markdown(insight)
        
        st.markdown("---")
        
        # Recommendations
        st.subheader("💡 Recommendations")
        recommendations = [
            "🎯 **Cost Optimization**: Monitor high-cost operations and implement batching where possible",
            "📊 **Regular Monitoring**: Set up automated reports to track usage trends",
            "💰 **Budget Planning**: Use historical data to forecast future OpenAI spending",
            "🔍 **Usage Audit**: Review API usage patterns to ensure optimal efficiency"
        ]
        
        for rec in recommendations:
            st.markdown(rec)

def create_openai_cost_analysis(cost_df):
    """Create OpenAI cost analysis visualizations"""
    st.header("💰 OpenAI Cost Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_cost = cost_df['cost_in_major'].sum()
        st.metric("Total Cost", f"${total_cost:.4f}")
    
    with col2:
        avg_cost = cost_df['cost_in_major'].mean()
        st.metric("Average Cost per Request", f"${avg_cost:.6f}")
    
    with col3:
        total_requests = len(cost_df)
        st.metric("Total Requests", f"{total_requests:,}")
    
    with col4:
        date_range = cost_df['date'].nunique()
        st.metric("Days Analyzed", date_range)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily cost trend
        daily_cost = cost_df.groupby('date')['cost_in_major'].sum().reset_index()
        fig_daily = px.line(daily_cost, x='date', y='cost_in_major', 
                           title='Daily Cost Trend',
                           labels={'cost_in_major': 'Cost (USD)', 'date': 'Date'})
        fig_daily.update_traces(line_color='#FF6B6B')
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        # Cost by service/model
        if 'name' in cost_df.columns:
            service_cost = cost_df.groupby('name')['cost_in_major'].sum().reset_index()
            service_cost = service_cost.sort_values('cost_in_major', ascending=False).head(10)
            fig_service = px.bar(service_cost, x='cost_in_major', y='name',
                               orientation='h', title='Cost by Service (Top 10)',
                               labels={'cost_in_major': 'Cost (USD)', 'name': 'Service'})
            fig_service.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_service, use_container_width=True)

def create_openai_activity_analysis(activity_df):
    """Create OpenAI activity analysis visualizations"""
    st.header("🔄 OpenAI Activity Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = activity_df['num_requests'].sum()
        st.metric("Total API Requests", f"{total_requests:,}")
    
    with col2:
        total_tokens = activity_df['total_tokens'].sum()
        st.metric("Total Tokens", f"{total_tokens:,}")
    
    with col3:
        avg_tokens_per_request = total_tokens / total_requests
        st.metric("Avg Tokens/Request", f"{avg_tokens_per_request:.0f}")
    
    with col4:
        unique_users = activity_df['user'].nunique() if 'user' in activity_df.columns else 0
        st.metric("Unique Users", unique_users)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily requests
        daily_requests = activity_df.groupby('date')['num_requests'].sum().reset_index()
        fig_requests = px.line(daily_requests, x='date', y='num_requests',
                              title='Daily API Requests',
                              labels={'num_requests': 'Number of Requests', 'date': 'Date'})
        fig_requests.update_traces(line_color='#45B7D1')
        st.plotly_chart(fig_requests, use_container_width=True)
    
    with col2:
        # Model usage
        if 'model' in activity_df.columns:
            model_usage = activity_df.groupby('model')['num_requests'].sum().reset_index()
            model_usage = model_usage.sort_values('num_requests', ascending=False)
            fig_models = px.bar(model_usage, x='num_requests', y='model',
                               orientation='h', title='Usage by Model',
                               labels={'num_requests': 'Number of Requests'})
            fig_models.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_models, use_container_width=True)

# AstraDB Report Functions
def generate_astradb_stakeholder_summary(df):
    """Generate executive summary for AstraDB usage"""
    st.header("📋 AstraDB Executive Summary")
    
    with st.container():
        st.subheader("🎯 Key Findings")
        
        total_cost = df['CALCULATED_COST'].sum()
        unique_resources = df['RESOURCE_NAME'].nunique()
        unique_orgs = df['ORG_NAME'].nunique()
        
        # Most expensive usage type
        top_usage_type = df.groupby('USAGE_TYPE')['CALCULATED_COST'].sum().idxmax()
        top_usage_cost = df.groupby('USAGE_TYPE')['CALCULATED_COST'].sum().max()
        top_usage_pct = (top_usage_cost / total_cost) * 100
        
        # Most expensive region
        top_region = df.groupby('REGION')['CALCULATED_COST'].sum().idxmax()
        top_region_cost = df.groupby('REGION')['CALCULATED_COST'].sum().max()
        top_region_pct = (top_region_cost / total_cost) * 100
        
        insights = [
            f"💰 **Total AstraDB spend**: ${total_cost:.2f}",
            f"🏢 **Organizations**: {unique_orgs}",
            f"🛠️ **Unique resources**: {unique_resources}",
            f"📊 **Most expensive usage type**: {top_usage_type} ({top_usage_pct:.1f}% of total)",
            f"🌍 **Most expensive region**: {top_region} ({top_region_pct:.1f}% of total)"
        ]
        
        for insight in insights:
            st.markdown(insight)
        
        st.markdown("---")
        
        st.subheader("💡 Recommendations")
        recommendations = [
            "🎯 **Resource Optimization**: Review underutilized resources in expensive regions",
            "💰 **Cost Control**: Implement budget alerts for high-cost usage types",
            "🌍 **Regional Strategy**: Consider resource distribution across cost-effective regions",
            "📊 **Usage Monitoring**: Set up regular reports to track resource consumption patterns"
        ]
        
        for rec in recommendations:
            st.markdown(rec)

def create_astradb_analysis(df):
    """Create AstraDB analysis visualizations"""
    st.header("☁️ AstraDB Usage & Cost Analysis")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        total_cost = df['CALCULATED_COST'].sum()
        st.metric("Total Cost", f"${total_cost:.4f}")
    
    with col3:
        unique_resources = df['RESOURCE_NAME'].nunique()
        st.metric("Unique Resources", unique_resources)
    
    with col4:
        unique_orgs = df['ORG_NAME'].nunique()
        st.metric("Organizations", unique_orgs)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Usage Type")
        cost_by_type = df.groupby('USAGE_TYPE')['CALCULATED_COST'].sum().reset_index()
        fig1 = px.bar(cost_by_type, x='USAGE_TYPE', y='CALCULATED_COST',
                     title="Cost Distribution by Usage Type",
                     labels={'CALCULATED_COST': 'Cost ($)', 'USAGE_TYPE': 'Usage Type'})
        fig1.update_traces(marker_color='lightblue')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Cost by Cloud Provider")
        if 'CLOUD_PROVIDER' in df.columns:
            cost_by_provider = df.groupby('CLOUD_PROVIDER')['CALCULATED_COST'].sum().reset_index()
            fig2 = px.pie(cost_by_provider, values='CALCULATED_COST', names='CLOUD_PROVIDER',
                         title="Cost Distribution by Cloud Provider")
            st.plotly_chart(fig2, use_container_width=True)
    
    # Resource breakdown
    st.subheader("Resource Breakdown")
    resource_stats = df.groupby('RESOURCE_NAME').agg({
        'CALCULATED_COST': 'sum',
        'USAGE': 'sum',
        'REGION': 'first',
        'CLOUD_PROVIDER': 'first' if 'CLOUD_PROVIDER' in df.columns else lambda x: 'N/A',
        'USAGE_TYPE': 'first'
    }).round(6)
    st.dataframe(resource_stats, use_container_width=True)
    
    # Time series analysis (if multiple time periods exist)
    if 'BREAKDOWN_START_TIMESTAMP_DATE' in df.columns and df['BREAKDOWN_START_TIMESTAMP_DATE'].nunique() > 1:
        st.subheader("Cost Over Time")
        time_series = df.groupby('BREAKDOWN_START_TIMESTAMP_DATE')['CALCULATED_COST'].sum().reset_index()
        fig3 = px.line(time_series, x='BREAKDOWN_START_TIMESTAMP_DATE', y='CALCULATED_COST',
                      title="Cost Trend Over Time",
                      labels={'CALCULATED_COST': 'Cost ($)', 'BREAKDOWN_START_TIMESTAMP_DATE': 'Date'})
        fig3.update_traces(line_color='orange')
        st.plotly_chart(fig3, use_container_width=True)

# Main application logic
def main():
    if page == "🤖 OpenAI Report":
        st.title("🤖 OpenAI Usage & Cost Analysis")
        st.markdown("---")
        
        # Load OpenAI data
        cost_df, cost_error = load_openai_cost_data(openai_cost_path)
        activity_df, activity_error = load_openai_activity_data(openai_activity_path)
        
        # Display loading status
        col1, col2 = st.columns(2)
        with col1:
            if cost_df is not None:
                st.success(f"✅ Cost data loaded: {len(cost_df)} records")
            else:
                st.error(f"❌ Cost data: {cost_error}")
        
        with col2:
            if activity_df is not None:
                st.success(f"✅ Activity data loaded: {len(activity_df)} records")
            else:
                st.error(f"❌ Activity data: {activity_error}")
        
        if cost_df is not None or activity_df is not None:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📊 Overview", "💰 Cost Analysis", "🔄 Activity Analysis", "📋 Executive Summary", "🗂️ Raw Data"]
            )
            
            with tab1:
                st.header("📊 Dashboard Overview")
                if cost_df is not None and activity_df is not None:
                    # Combined metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Cost", f"${cost_df['cost_in_major'].sum():.4f}")
                    with col2:
                        st.metric("Total Requests", f"{activity_df['num_requests'].sum():,}")
                    with col3:
                        st.metric("Total Tokens", f"{activity_df['total_tokens'].sum():,}")
                    with col4:
                        cost_per_request = cost_df['cost_in_major'].sum() / activity_df['num_requests'].sum()
                        st.metric("Cost per Request", f"${cost_per_request:.4f}")
                else:
                    st.info("Load both cost and activity data for combined analysis.")
            
            with tab2:
                if cost_df is not None:
                    create_openai_cost_analysis(cost_df)
                else:
                    st.info("Cost data not available. Check file path configuration.")
            
            with tab3:
                if activity_df is not None:
                    create_openai_activity_analysis(activity_df)
                else:
                    st.info("Activity data not available. Check file path configuration.")
            
            with tab4:
                if cost_df is not None or activity_df is not None:
                    generate_openai_stakeholder_summary(cost_df, activity_df)
                else:
                    st.info("No data available for executive summary.")
            
            with tab5:
                st.header("🗂️ Raw Data")
                if cost_df is not None:
                    st.subheader("Cost Data")
                    st.dataframe(cost_df.head(100), use_container_width=True)
                    csv_cost = cost_df.to_csv(index=False)
                    st.download_button("📥 Download Cost Data", csv_cost, "openai_cost_data.csv", "text/csv")
                
                if activity_df is not None:
                    st.subheader("Activity Data")
                    st.dataframe(activity_df.head(100), use_container_width=True)
                    csv_activity = activity_df.to_csv(index=False)
                    st.download_button("📥 Download Activity Data", csv_activity, "openai_activity_data.csv", "text/csv")
    
    else:  # AstraDB Report
        st.title("☁️ AstraDB Usage & Cost Analysis")
        st.markdown("---")
        
        # Load AstraDB data
        df, error = load_astradb_data(astradb_path)
        
        if df is not None:
            st.success(f"✅ AstraDB data loaded: {len(df)} records")
            
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📊 Overview", "📈 Detailed Analysis", "📋 Executive Summary", "🗂️ Raw Data"]
            )
            
            with tab1:
                create_astradb_analysis(df)
            
            with tab2:
                st.header("📈 Advanced Analysis")
                
                # Data explanation
                with st.expander("💡 Understanding Your AstraDB Data", expanded=True):
                    st.markdown("""
                    **🏢 Organization Details:** Account and billing information
                    **🛠️ Resource Information:** Database instances, regions, and configurations  
                    **💰 Usage & Billing:** Detailed cost breakdown by usage type
                    **📅 Time Period:** Billing periods and usage timestamps
                    **🏗️ Infrastructure:** Service tiers and deployment details
                    """)
                
                # Additional charts
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'REGION' in df.columns:
                        region_cost = df.groupby('REGION')['CALCULATED_COST'].sum().reset_index()
                        fig = px.bar(region_cost, x='REGION', y='CALCULATED_COST',
                                   title="Cost by Region")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'ORG_NAME' in df.columns:
                        org_cost = df.groupby('ORG_NAME')['CALCULATED_COST'].sum().reset_index()
                        fig = px.pie(org_cost, values='CALCULATED_COST', names='ORG_NAME',
                                   title="Cost by Organization")
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                generate_astradb_stakeholder_summary(df)
            
            with tab4:
                st.header("🗂️ Raw Data")
                st.dataframe(df, use_container_width=True)
                
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📥 Download AstraDB Data",
                    csv_data,
                    f"astradb_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
        else:
            st.error(f"❌ AstraDB data: {error}")
            st.info("Please check the file path in the configuration section.")

if __name__ == "__main__":
    main()