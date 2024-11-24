import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie #pip
import requests #pip 
from db_operations import get_db_connection, fetch_data

# Database connection
try:
    connection = get_db_connection()
    cursor = connection.cursor()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()


st.sidebar.header("Filter Options")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
      st.title(" :orange[Jet BUS APP]")
      
    with col2:
         
         url=requests.get("https://lottie.host/98bdd86d-f9a9-4ee1-8e96-664edfe5c2b7/imm0NYuDQP.json")
         url_json=dict()
         if url.status_code==200:
            url_json= url.json()
         else:
            print('Error in the url')
         st_lottie(url_json,width=200,height=300)

# Fetch bus routes
try:
    cursor.execute("use redbus_project")
    cursor.execute("SELECT DISTINCT bus_routes_name FROM bus_routes;")
    route_name_fetcher = cursor.fetchall()
except Exception as e:
    st.error(f"Error fetching bus routes: {e}")
    st.stop()

if route_name_fetcher:
    df_bus_route_name = pd.DataFrame(route_name_fetcher, columns=["bus_routes_name"])
else:
    st.sidebar.error("No bus routes available.")
    st.stop()

bus_routes_name_input = st.sidebar.selectbox(
    ':orange[Select your travelling Route :]', 
    df_bus_route_name["bus_routes_name"], 
    index=None, 
    placeholder="Select the route name"
)

# Fetch bus types
if bus_routes_name_input:
    try:
        bus_type_query = f"""
        SELECT DISTINCT bus_type 
        FROM bus_routes 
        WHERE bus_routes_name = '{bus_routes_name_input}'
        """
        cursor.execute(bus_type_query)
        bus_type_fetcher = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching bus types: {e}")
        st.stop()

    if bus_type_fetcher:
        df_bus_type = pd.DataFrame(bus_type_fetcher, columns=["bus_type"])
        bus_type_input = st.sidebar.selectbox(
            ':orange[Select Bus Type :]', 
            df_bus_type["bus_type"], 
            index=None, 
            placeholder="Select your bus type"
        )
    else:
        st.sidebar.error("No bus types available for the selected route.")
        st.stop()
else:
    st.sidebar.warning("Please select a bus route.")
    st.stop()

# Additional filters
price_range = st.sidebar.slider(
    "Select Price Range:", 
    min_value=0, max_value=10000, value=(0, 10000)
)
star_rating_range = st.sidebar.slider(
    "Select Star Rating Range:", 
    min_value=1.0, max_value=5.0, value=(1.0, 5.0)
)

# Sorting options
sort_options = [
    "Price (Low to High)",
    "Price (High to Low)",
    "Star Rating (High to Low)",
    "Star Rating (Low to High)",
    "Seats Available (High to Low)",
    "Seats Available (Low to High)",
    "Departure Early First",
    "Departure Late First"
]
sort_choice = st.sidebar.selectbox("Sort By:", sort_options)

# Construct filters dictionary
filters = {
    "bus_routes_name": bus_routes_name_input,
    "bus_type": bus_type_input,
    "price": price_range,
    "star_rating": star_rating_range
}

# Fetch filtered data
try:
    filtered_data = fetch_data(filters)
except Exception as e:
    st.error(f"Error fetching filtered data: {e}")
    st.stop()

# Apply sorting
if filtered_data is None or filtered_data.empty:
    st.warning("No records found for the selected filters.")
else:
    if sort_choice == "Price (Low to High)":
        filtered_data = filtered_data.sort_values("price", ascending=True)
    elif sort_choice == "Price (High to Low)":
        filtered_data = filtered_data.sort_values("price", ascending=False)
    elif sort_choice == "Star Rating (High to Low)":
        filtered_data = filtered_data.sort_values("star_rating", ascending=False)
    elif sort_choice == "Star Rating (Low to High)":
        filtered_data = filtered_data.sort_values("star_rating", ascending=True)
    elif sort_choice == "Seats Available (High to Low)":
        filtered_data = filtered_data.sort_values("seats_available", ascending=False)
    elif sort_choice == "Seats Available (Low to High)":
        filtered_data = filtered_data.sort_values("seats_available", ascending=True)
    elif sort_choice == "Departure Early First":
        filtered_data = filtered_data.sort_values("departing_time", ascending=True)
    elif sort_choice == "Departure Late First":
        filtered_data = filtered_data.sort_values("departing_time", descending=True)

    # Display sorted results
    st.write(f"### Sorted Results ({sort_choice}): {filtered_data.shape[0]} records")
    st.dataframe(filtered_data)

    # Visualizations
    st.write("### Visualizations")

    # Price Distribution
    st.write("### Price Chart")
    price_chart = filtered_data.groupby("bus_name")["price"].mean()
    if not price_chart.empty:
        st.bar_chart(price_chart)

    # Star Ratings
    st.write("### Star Rating Chart")
    star_chart = filtered_data.groupby("bus_name")["star_rating"].mean()
    if not star_chart.empty:
        st.line_chart(star_chart)

    # Download filtered data
    st.write("### Download Filtered Data")
    st.download_button(
        label="Download as CSV",
        data=filtered_data.to_csv(index=False),
        file_name="filtered_bus_data.csv",
        mime="text/csv"
    )
