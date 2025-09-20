import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
# Set the page title, icon, and layout. This should be the first Streamlit command.
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DATA LOADING AND PREPARATION ---
# Use a cache decorator to prevent reloading data on every interaction, which improves performance.
@st.cache_data
def load_data(path: str):
    """Loads and prepares the sales data from a local CSV file."""
    try:
        # Load the CSV using pandas. The encoding is specified to prevent common errors.
        df = pd.read_csv(path, encoding="ISO-8859-1")
        # Convert 'Order Date' column to a proper datetime format for time-series analysis.
        # The format string '%m/%d/%Y' matches the date format in the new CSV file.
        df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y', errors='coerce')
        # Drop any rows where the date conversion might have failed to ensure data quality.
        df.dropna(subset=['Order Date'], inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{path}' was not found. Please make sure it is in the same folder as the script.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

# Load the data from the specified CSV file.
df = load_data("superstore_sales.csv")

# If the data loading fails, stop the app to prevent further errors.
if df is None:
    st.stop()

# --- STYLING ---
# Inject custom CSS to give the dashboard a polished, dark-mode look.
st.markdown("""
<style>
    .main {
        background-color: #0E1117; /* Dark background for the main content area */
    }
    .st-sidebar {
        background-color: #1E1E1E; /* Darker background for the sidebar */
    }
    h1, h2 {
        color: #1DB954; /* Green accent color for titles */
    }
    .stMetric {
        background-color: #1E1E1E; /* Dark background for metric cards */
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #222;
    }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")

# Create a multiselect widget for Region, pre-selecting all available regions.
region = st.sidebar.multiselect(
    "Select Region:",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Create a multiselect widget for Category, pre-selecting all available categories.
category = st.sidebar.multiselect(
    "Select Category:",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Filter the main dataframe based on the user's selections from the sidebar.
df_selection = df.query(
    "Region == @region & Category == @category"
)

# If the filtered dataframe is empty, show a warning and stop.
if df_selection.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()


# --- MAIN PAGE LAYOUT ---
st.title("🛒 Superstore Sales Dashboard")
st.markdown("##") # Adds a small space below the title.

# --- KEY METRICS ---
# Calculate key performance indicators (KPIs) from the filtered data.
total_sales = int(df_selection['Sales'].sum())
total_profit = int(df_selection['Profit'].sum())
average_sale = round(df_selection['Sales'].mean(), 2)

# Display the KPIs in three columns for a clean layout.
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Sales", value=f"${total_sales:,.0f}")
with col2:
    st.metric(label="Total Profit", value=f"${total_profit:,.0f}")
with col3:
    st.metric(label="Average Sale Value", value=f"${average_sale:,.2f}")

st.markdown("---") # A horizontal line to separate sections.


# --- VISUALIZATIONS ---
st.header("Charts & Analysis")

# Bar Chart: Sales by Product Sub-Category
# Group data by sub-category and sum the sales, then sort for better visualization.
sales_by_subcategory = df_selection.groupby(by=['Sub-Category'])['Sales'].sum().sort_values(ascending=True)
fig_sales_by_subcategory = px.bar(
    sales_by_subcategory,
    x=sales_by_subcategory.values,
    y=sales_by_subcategory.index,
    orientation='h', # Horizontal bar chart
    title="<b>Sales by Product Sub-Category</b>",
    color_discrete_sequence=["#1DB954"],
    template="plotly_dark",
    labels={'x': 'Total Sales', 'y': 'Sub-Category'}
)
fig_sales_by_subcategory.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", # Transparent background
    yaxis=dict(showgrid=False),
    xaxis=dict(showgrid=True, gridcolor='#222')
)

# Pie Chart: Sales by Region
sales_by_region = df_selection.groupby(by=['Region'])['Sales'].sum()
fig_sales_by_region = px.pie(
    sales_by_region,
    values=sales_by_region.values,
    names=sales_by_region.index,
    title="<b>Sales by Region</b>",
    color_discrete_sequence=px.colors.sequential.Greens_r,
    template="plotly_dark"
)
fig_sales_by_region.update_traces(
    textposition='inside', 
    textinfo='percent+label',
    pull=[0.05] * len(sales_by_region) # Dynamic pull for a slight 3D effect
)

# Display the charts side-by-side in two columns.
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_sales_by_subcategory, use_container_width=True)
right_column.plotly_chart(fig_sales_by_region, use_container_width=True)

# --- RAW DATA TABLE ---
# Show the filtered data in an expandable table at the bottom.
with st.expander("View Raw Data Table"):
    st.dataframe(df_selection)

