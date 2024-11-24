import pymysql
import pandas as pd
from sqlalchemy import create_engine

def get_db_connection():
    """Establish a connection to the MySQL database."""
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='12345',
        database='redbus_project'
    )
    return connection

def creation_of_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    table_name = 'bus_routes'
    table_create_declaration = """id INT AUTO_INCREMENT PRIMARY KEY,
    bus_routes_name VARCHAR(255) NOT NULL,
    bus_routes_link VARCHAR(2083),
    bus_name VARCHAR(255) NOT NULL,
    bus_type VARCHAR(100),
    departing_time TIME NOT NULL,
    duration VARCHAR(50),
    reaching_time TIME NOT NULL,
    star_rating FLOAT(3,2),
    price DECIMAL(10,2) NOT NULL,
    seat_availability INT NOT NULL"""
    create_table_query = f"""create table {table_name}({table_create_declaration});"""
    print("create_table_query = ", create_table_query)
    cursor.execute(create_table_query)
    print("Table Created Successfully")
    connection.commit()


def fetch_data(filters=None):
    """Fetch filtered data from the database."""
    try:
        # Establish database connection
        connection = get_db_connection()
        query = "SELECT * FROM bus_routes"  # Base query

        # Add filters to the query if provided
        if filters:
            filter_clauses = []

            if filters.get('bus_routes_name'):
                filter_clauses.append(
                    f"bus_routes_name = {repr(filters['bus_routes_name'])}"
                )

            if filters.get('bus_type'):
                filter_clauses.append(
                    f"bus_type = {repr(filters['bus_type'])}"
                )

            if filters.get('price'):
                filter_clauses.append(
                    f"price BETWEEN {filters['price'][0]} AND {filters['price'][1]}"
                )

            if filters.get('star_rating'):
                filter_clauses.append(
                    f"star_rating BETWEEN {filters['star_rating'][0]} AND {filters['star_rating'][1]}"
                )

            # Combine filters into the query
            if filter_clauses:
                query += " WHERE " + " AND ".join(filter_clauses)

        # Debugging: Print or display the constructed query
        #print("Constructed Query:", query)
        #st.write("Constructed Query:", query)  # Debugging in Streamlit

        # Execute the query and fetch data
        df = pd.read_sql(query, connection)

        return df

    except Exception as e:
        print("Error fetching data")
        return pd.DataFrame()  # Return an empty DataFrame on error

    finally:
        if connection:
            connection.close()





def insert_data_as_dataframe(bus_details_list):
    """Convert the list of bus details to a DataFrame and insert it into the database."""
    # Define column names matching the database table structure
    columns = [
        "bus_routes_name", "bus_routes_link", "bus_name", "bus_type", 
        "departing_time", "duration", "reaching_time", "star_rating", 
        "price", "seat_availability"
    ]

    # Convert list of tuples to DataFrame
    df = pd.DataFrame(bus_details_list, columns=columns)

    # Establish a connection to MySQL using SQLAlchemy
    engine = create_engine('mysql+pymysql://root:12345@localhost/redbus_project')

    try:
        #table creation
        #creation_of_table()
        # Insert the DataFrame into the database table
        df.to_sql("bus_routes", con=engine, if_exists="append", index=False)
        print("Data inserted successfully!")
    except Exception as e:
        print("****Error inserting data", e)

try:
    print()
    #creation_of_table()
    #bus_details_list = [
        #('Route E', 'http://example.com', 'AAA Travels', 'A.C. Seater', '08:00', '5h 30m', '13:30', 2.5, 1000, 10),
        #('Route E', 'http://example.com', 'BBB Travels', 'SUPER LUXURY (NON-AC, 2 + 2 PUSH BACK)', '09:00', '6h 00m', '15:00', 4.7, 2000, 15),
    #]
    #insert_data_as_dataframe(bus_details_list)
except Exception as e:
    print("***Exception", e)