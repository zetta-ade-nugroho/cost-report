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
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts['iso_alpha'] = country_counts['country'].apply(get_iso3)
    country_counts = country_counts.dropna(subset=['iso_alpha'])

    # Plot choropleth map
    fig_map = px.choropleth(
    country_counts,
    locations="iso_alpha",
    locationmode="ISO-3",
    color="count",
    hover_name="country",
    color_continuous_scale="Turbo",  # ← CHANGE THIS FOR STRONGER COLORS
    title="📍 Jobs by Country (ISO Choropleth)",
)

    fig_map.update_geos(
    showframe=False,
    showcoastlines=True,
    projection_type='natural earth',
    showland=True,
    landcolor='White',     # better contrast with colored countries
    oceancolor='LightBlue',
)

    fig_map.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    coloraxis_colorbar={
        'title': 'Job Count',
        'tickprefix': '',
        'ticksuffix': ' jobs',
    }
)

    st.plotly_chart(fig_map, use_container_width=True)


