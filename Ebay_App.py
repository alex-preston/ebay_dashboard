import pandas as pd
import streamlit as st
import plotly.express as px

df = pd.read_csv("pc_df_final.csv")

st.set_page_config(page_title='eBay Laptop Data Dashboard', layout='wide')

# Professional header: polished title + full-width divider
st.markdown(
        """
        <style>
        .app-header { width: 100%; display: block; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid #e9ecef;}
        .app-title {font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial; font-size:48px; font-weight:700; letter-spacing:0.4px; margin:0;}
        .app-sub {color: #6c757d; margin-top:6px; margin-bottom:0; font-size:0.95rem;}
        .app-header-row { display:flex; justify-content:space-between; align-items:center; gap:12px }
        @media (prefers-color-scheme: dark) {
                .app-header { border-bottom: 1px solid #353940; }
                .app-sub { color: #bfc4c9; }
        }
        </style>
        <div class="app-header">
            <div class="app-header-row">
                <div>
                    <div class="app-title">eBay Laptop Data Dashboard</div>
                    <div class="app-sub">Interactive overview</div>
                </div>
                <div style="font-size:0.9rem; color:#6c757d;">&nbsp;</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
)

# Small CSS to make metrics and containers look like professional cards (light + dark mode)
st.markdown(
    """
    <style>
    /* Light mode metrics and containers */
    @media (prefers-color-scheme: light) {
        div[data-testid="stMetric"] {
            border: 1px solid #e6e6e6 !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06) !important;
            background-color: #ffffff !important;
            color: #111 !important;
        }
        div[data-testid="stMetric"] * {
            color: #111 !important;
        }
        .stDataFrame, .stDataFrame > div {
            border: 1px solid #f0f0f0 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03) !important;
            background: #ffffff !important;
            color: #111 !important;
        }
        .top5-card, .top5-card * {
            color: #111 !important;
        }
    }

    /* Dark mode metrics and containers */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            border: 1px solid #444444 !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
            background-color: #262730 !important;
            color: #f1f1f1 !important;
        }
        div[data-testid="stMetric"] * {
            color: #f1f1f1 !important;
        }
        .stDataFrame, .stDataFrame > div {
            border: 1px solid #404040 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
            background: #262730 !important;
            color: #f1f1f1 !important;
        }
        .top5-card, .top5-card * {
            color: #f1f1f1 !important;
        }
    }

    /* Make captions slightly muted (works in both modes) */
    .small-caption {
        font-size: 0.9rem;
        margin-top: 4px;
        margin-bottom: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header('Filters')

# Filter 1: Price range (slider)
price_min, price_max = st.sidebar.slider(
    'Select Price Range ($)',
    min_value=int(df['Price'].min()),
    max_value=int(df['Price'].max()),
    value=(int(df['Price'].min()), int(df['Price'].max()))
)

# Filter 2: Condition (multiselect)
conditions = sorted(df['Condition Clean'].dropna().unique())
selected_conditions = st.sidebar.multiselect(
    'Select Condition',
    options=conditions,
    default=conditions
)

# Filter 3: Brand selection (multiselect)
brands = sorted(df['Brand'].unique())
selected_brands = st.sidebar.multiselect(
    'Select Brand(s)',
    options=brands,
    default=brands
)

# Apply all filters to the dataframe
filtered_df = df[
    (df['Brand'].isin(selected_brands)) &
    (df['Price'] >= price_min) &
    (df['Price'] <= price_max) &
    (df['Condition Clean'].isin(selected_conditions))
]

# Display filter summary
st.sidebar.markdown('---')
st.sidebar.info(f'Showing {len(filtered_df)} of {len(df)} records')

# Display the filtered dataframe
st.subheader('Laptop Data')
st.caption('Table reflects the currently selected filters. Click headers to sort. Metrics above reflect the filtered dataset.')
# Compact metrics summary (small widgets placed side-by-side)
metrics_df = filtered_df.copy()
metrics_df['Price'] = pd.to_numeric(metrics_df['Price'], errors='coerce')

def safe_numeric_mean(df, col):
    if col in df.columns:
        nums = pd.to_numeric(df[col], errors='coerce')
        if nums.notna().any():
            return nums.mean()
        # try extracting digits from strings (e.g., '8GB')
        extracted = df[col].astype(str).str.extract(r"(\d+)")
        if extracted.shape[1] >= 1:
            vals = pd.to_numeric(extracted[0], errors='coerce')
            if vals.notna().any():
                return vals.mean()
    return None

avg_price = metrics_df['Price'].mean() if not metrics_df['Price'].dropna().empty else None
min_price = metrics_df['Price'].min() if not metrics_df['Price'].dropna().empty else None
max_price = metrics_df['Price'].max() if not metrics_df['Price'].dropna().empty else None
top5 = metrics_df['Brand'].value_counts().head(5)
top5_str = ', '.join([f"{b} ({c})" for b, c in top5.items()]) if not top5.empty else 'N/A'
avg_ram = safe_numeric_mean(metrics_df, 'Ram Size Clean')
avg_screen = safe_numeric_mean(metrics_df, 'Screen Size Clean')

# Row 1: price metrics + top brands
col1, col2, col3, col4 = st.columns([1,1,1,2])
with col1:
    st.metric('Average Price', f"${avg_price:,.2f}" if pd.notna(avg_price) else 'N/A')
with col2:
    st.metric('Min Price', f"${min_price:,.0f}" if pd.notna(min_price) else 'N/A')
with col3:
    st.metric('Max Price', f"${max_price:,.0f}" if pd.notna(max_price) else 'N/A')
with col4:
    st.markdown(
        f"""
        <style>
        .top5-card {{
            border-radius: 10px;
            padding: 10px 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 50px;
        }}
        @media (prefers-color-scheme: light) {{
            .top5-card {{
                border: 1px solid #e6e6e6;
                background-color: #ffffff;
                box-shadow: 0 4px 10px rgba(0,0,0,0.06);
            }}
        }}
        @media (prefers-color-scheme: dark) {{
            .top5-card {{
                border: 1px solid #444444;
                background-color: #262730;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }}
        }}
        .top5-title {{
            margin: 0 0 2px 0;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            opacity: 0.7;
        }}
        .top5-brands {{
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        </style>
        <div class="top5-card">
            <p class="top5-title">Top 5 Brands</p>
            <p class="top5-brands">{top5_str}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Row 2: memory / ram metrics
col5, col6, col7 = st.columns([1,1,3])
with col5:
    st.metric('Avg RAM (GB)', f"{avg_ram:.1f} GB" if pd.notna(avg_ram) else 'N/A')
with col6:
    st.metric('Avg Screen Size', f"{avg_screen:.1f}\"" if pd.notna(avg_screen) else 'N/A')
with col7:
    st.caption('Notes')
    st.write('Metrics reflect the currently selected filters. Top brands show listing counts.')
st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)

# Visualization: Price distribution by Brand
st.subheader('Average Price by Brand')

# Prepare data for the chart
price_by_brand = filtered_df.groupby('Brand')['Price'].mean().sort_values(ascending=False)

# Display bar chart
st.bar_chart(price_by_brand)
st.caption('Average price by brand for the selected filters. Bars are sorted descending by average price.')

# Business Analysis
st.markdown('---')
st.subheader('Market Analysis')

analysis_text = """
**Executive Summary:**

This view summarizes average listing price by brand, showing clear price tiers that reflect brand positioning and typical buyer willingness-to-pay.

**Key Takeaways:**
- Premium brands sit in higher price tiers and are potential margin drivers.
- Mass-market brands cluster in lower price tiers and contribute bulk volume.
- Low-count, high-price brands should be treated as potential outliers and reviewed for listing quality.

**Recommendations:**
- Prioritize sourcing and promotions for brands with strong price performance and sufficient volume.
- Run a margin-by-brand analysis before making major inventory shifts.
- Review and clean low-count, high-price listings to remove outliers or improve listing detail.

**Streamlit-only visualization note:**
- Streamlit built-ins like `st.bar_chart` are fast for exploration but offer limited hover detail and styling. As you can see, there is no option for axis titles which is why the above chart has none. For richer stakeholder-facing interaction and annotations, external libraries (e.g., Plotly) are preferable, though Streamlit alone is sufficient for quick internal analyses.
"""

st.markdown(analysis_text)

# Second Visualization: Screen Size vs Average Price (column chart)
st.markdown('---')
st.subheader('Screen Size vs Average Price')

# Prepare data: coerce numeric and group by screen size (rounded for grouping)
screen_df = filtered_df.copy()
screen_df['Price'] = pd.to_numeric(screen_df['Price'], errors='coerce')
screen_df['Screen Size Clean'] = pd.to_numeric(screen_df['Screen Size Clean'], errors='coerce')
screen_df = screen_df.dropna(subset=['Price', 'Screen Size Clean'])

# Round screen sizes to one decimal to group similar sizes (e.g., 13.3 -> 13.3)
screen_df['Screen Size Clean'] = screen_df['Screen Size Clean'].round(1)

# Aggregate average price and count per screen size
screen_stats = (
        screen_df.groupby('Screen Size Clean')
        .agg(Average_Price=('Price', 'mean'), Count=('Price', 'count'))
        .reset_index()
)

# For readability sort by screen size
screen_stats = screen_stats.sort_values('Screen Size Clean')

if not screen_stats.empty:
        fig_screen = px.bar(
                screen_stats,
                x='Screen Size Clean',
                y='Average_Price',
                hover_data=['Count'],
                title='Average Price by Screen Size (inches)',
                labels={'Screen Size Clean': 'Screen Size (inches)', 'Average_Price': 'Average Price ($)'}
        )
        fig_screen.update_traces(marker_color='indianred')
        fig_screen.update_layout(height=500)
        st.plotly_chart(fig_screen, use_container_width=True)
else:
        st.info('No screen-size data available for the selected filters.')

# Business Analysis for Second Chart
st.markdown('---')
st.subheader('Screen Size Pricing Insights')

analysis_text_second = """
**Executive Summary:**

This column chart shows average listing price by rounded screen size (inches). Screen size is a tangible product attribute that often correlates
with form factor and intended use (ultraportable vs desktop replacement) and therefore impacts buyer willingness-to-pay.

Key takeaways for management:
- **Clear price tiers:** Larger screens (15.6" and above) generally carry higher average prices, reflecting premium positioning for performance and
    multimedia use-cases.
- **Sweet spots:** Mid-size screens (13"–14") can show competitive average prices, representing high-volume, mainstream demand where small price
    improvements can meaningfully affect revenue.
- **Volume context:** Hovering the chart reveals listing counts—screen sizes with low counts should be interpreted cautiously.

Recommendations:
- Prioritize promotions and premium bundles for 15.6"+ categories where average price is higher and margin potential exists.
- For 13"–14" segments, optimize SKU assortments for value and conversion (competitive pricing + accessories bundles).
- Monitor low-count screen-size buckets and consider consolidating similar SKUs or improving listing quality to increase conversion.

**Plotly Express vs Streamlit Efficiency:**
- Plotly Express lets us produce a labeled, interactive column chart with hover counts and easy styling in a single call. Streamlit's `bar_chart()` 
    can render a static bar quickly but lacks hover detail and styling flexibility.
- For stakeholder-facing dashboards where exploration and clarity matter, Plotly offers a better trade-off despite slightly higher render cost.
"""

st.markdown(analysis_text_second)

# Third Visualization: Average Price by Release Year for Selected Brands and Year Range
st.markdown('---')
st.subheader('Average Price by Release Year — Select Brands & Year Range')

# Prepare data for multi-brand trend
trend_all = filtered_df.copy()
trend_all['Price'] = pd.to_numeric(trend_all['Price'], errors='coerce')
trend_all['Release Year'] = pd.to_numeric(trend_all['Release Year'], errors='coerce')
trend_all = trend_all.dropna(subset=['Price', 'Release Year'])

# Brand selector (multiselect) and year range slider
available_brands = sorted(trend_all['Brand'].dropna().unique())
selected_brands_for_trend = st.multiselect('Select brands to display (leave empty for all)', options=available_brands, default=available_brands)

min_year = int(trend_all['Release Year'].min()) if not trend_all['Release Year'].empty else 0
max_year = int(trend_all['Release Year'].max()) if not trend_all['Release Year'].empty else 0
year_range = st.slider('Select release year range', min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filter by selected brands and year range
if selected_brands_for_trend:
    trend_filtered = trend_all[trend_all['Brand'].isin(selected_brands_for_trend)]
else:
    trend_filtered = trend_all.copy()

trend_filtered = trend_filtered[(trend_filtered['Release Year'] >= year_range[0]) & (trend_filtered['Release Year'] <= year_range[1])]

# Aggregate: average price by year and brand
trend_df_full = trend_filtered.groupby(['Release Year', 'Brand'], as_index=False).agg({'Price': 'mean'})

if trend_df_full.empty:
    st.info('No data available for the selected brands/year range. Adjust filters.')
else:
    fig_trend = px.line(
        trend_df_full,
        x='Release Year',
        y='Price',
        color='Brand',
        markers=True,
        title='Average Price by Release Year (selected brands)',
        labels={'Price': 'Average Price ($)'}
    )
    fig_trend.update_layout(height=500)
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown('---')
st.subheader('Trend Analysis (Brands & Years)')
trend_analysis = """
**Executive Summary:**

This view shows average price by release year for the brands and year range you choose. Use it to compare brand pricing trajectories across product generations.

Recommendations:
- Focus sourcing and promotions on brands with upward price momentum in recent release years.
- If you see inconsistent brand trajectories, investigate listing quality or mismatched model categorizations.
"""

st.markdown(trend_analysis)