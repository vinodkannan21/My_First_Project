from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import re
import pymysql
from db_operations import insert_data_as_dataframe

# Function Definitions


def get_bus_details(driver, bus_routes_list):
    
    for route in bus_routes_list: #Iterate Over the Routes.Loops through each route in bus_routes_list.
        bus_routes_link = route[0]  # Access the route link directly
        bus_routes_name = route[1]  # Access the route name directly
        
        
        driver.get(bus_routes_link) #Navigate to Each Route Page. Navigates the browser to the bus route URL (bus_routes_link) using driver.get().
        time.sleep(3)

        click_clear_all_filters_button(driver)
        time.sleep(3)

        click_view_buses(driver) #to load the buses.
        time.sleep(3)

        scroll(driver) #to ensure all bus items are visible.

        try:
            bus_items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "clearfix.bus-item-details")) 
            ) #Waits until the bus elements (identified by their class name) are loaded on the page.
            time.sleep(3)

            
            for bus in bus_items: # Iterates through all bus items found on the page.
                
                bus_name = bus_type = departing_time = duration = reaching_time = star_rating = Price = seat_availability = None # Initialize variables for each bus

                try:
                    # Extracting bus details
                    bus_name = bus.find_element(By.XPATH, ".//div[@class='travels lh-24 f-bold d-color']").text
                    print(bus_name)

                    bus_type = bus.find_element(By.XPATH, ".//div[@class='bus-type f-12 m-top-16 l-color evBus']").text
                    print(bus_type)

                    departing_time = bus.find_element(By.XPATH, ".//div[@class='dp-time f-19 d-color f-bold']").text
                    print(departing_time)

                    duration = bus.find_element(By.XPATH, ".//div[@class='dur l-color lh-24']").text
                    print(duration)

                    reaching_time = bus.find_element(By.XPATH, ".//div[@class='bp-time f-19 d-color disp-Inline']").text
                    print(reaching_time)

                    rating = bus.find_element(By.XPATH, ".//div[@class='rating-sec lh-24']").text
                    star_rating = float(rating) if rating else None  # Safely convert to float
                    print(star_rating)

                    price = bus.find_element(By.XPATH, ".//div[@class='fare d-block']").text
                    price_text = re.findall(r'\d+', price) # extracted using regular expressions to find numeric values in the text.
                    Price = int(price_text[0]) if price_text else None  # Check if the price text is found
                    print(Price)

                    seat_availability = bus.find_element(By.XPATH, ".//div[@class='seat-left m-top-30']").text
                    seat_available = bus.find_element(By.XPATH, ".//div[@class='seat-left m-top-30']").text
                    seats_text = re.findall(r'\d+', seat_available) # extracted using regular expressions to find numeric values in the text.
                    seat_availability = int(seats_text[0]) if seats_text else None
                    print(seat_availability)

                    
                    bus_details = (
                        bus_routes_name,
                        bus_routes_link,
                        bus_name,
                        bus_type,
                        departing_time,
                        duration,
                        reaching_time,
                        star_rating,
                        Price,
                        seat_availability
                    )

                    bus_details_list.append(bus_details) #Appends a tuple of all extracted details for the current bus to the bus_details_list.

                except Exception as e:
                    #print(f"Error extracting details for bus: {e}")
                    pass

        except Exception as e:
            #print(f"Error finding bus items: {e}")
            pass

    return bus_details_list # Returns the list of tuples containing all bus details.



def scroll(driver):
    
    previous_page_height = driver.execute_script("return document.body.scrollHeight") # Get the initial page height
    
    while True:
        
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') # Scroll to the bottom of the page
        time.sleep(1)  # Wait to allow content to load (adjust time as needed)

        
        new_page_height = driver.execute_script("return document.body.scrollHeight") # Get the new page height after scrolling

        
        if new_page_height == previous_page_height: # Check if the page height has stopped changing (end of page)
            break

        
        previous_page_height = new_page_height # Update the previous page height for the next iteration

def click_view_buses(driver):
    try:
       
        container=WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH,"//div[contains(@class, 'button') and contains(text(), 'View Buses')]")))  #fetching the container
        
        for i in range(len(container))[::-1]: #checking the number of view buses and clicking
            container[i].click()
            time.sleep(2)
        time.sleep(2)    
    except:
        pass  
def click_clear_all_filters_button(driver):
        """
        Finds and clicks the 'CLEAR ALL FILTERS' button on a webpage using Selenium.

        Args:
            driver (webdriver): An instance of Selenium WebDriver.
        """
        try:
            
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='btn' and text()='CLEAR ALL FILTERS']"))
            ) # Wait until the button is visible and clickable
            
            button.click() # Click the button
            print("Filters cleared successfully!")
        except Exception as e:
            print("No filters")

def route(driver): # Function to extract route details from the current page
    bus_routes_details = driver.find_elements(By.CSS_SELECTOR, "a.route")  # Adjust the selector
    for i in bus_routes_details:
        bus_routes_link = i.get_attribute("href")
        bus_routes_name = i.get_attribute("title")            
            
       
        bus_routes_list.append((bus_routes_link, bus_routes_name))  # Append the details as a tuple
    print("list length:",len(bus_routes_list))
    return bus_routes_list

def extract_route_details(driver, state_name, last_page_number):
    page_link = f"""https://www.redbus.in/online-booking/{state_name}/?utm_source=rtchometile"""
    driver.get(page_link)

   
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="DC_117_paginationTable"]')))  # Wait for elements to load
    
    
    current_page_number = int(driver.find_element(By.CLASS_NAME, 'DC_117_pageActive').text) # Initialize current page
    
  
    
    route(driver)    # Collect route data on the first page

    for _ in range(current_page_number, last_page_number + 1):
        try:
            
            pagination_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div[12]'))
            ) # Update pagination container
            
            
            next_page_button = pagination_container.find_element(
                By.XPATH, f'.//div[contains(@class, "DC_117_pageTabs") and text()="{current_page_number + 1}"]'
            ) # Locate the next page 
            
            # Scroll to and click the next page button
            actions = ActionChains(driver)
            actions.move_to_element(next_page_button).perform()   
            time.sleep(1)  # Wait after scrolling
            next_page_button.click()
            
            
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, '//div[contains(@class, "DC_117_pageTabs DC_117_pageActive")]'),
                    str(current_page_number + 1)
                )
            ) # Wait until the next page is active

            print(f"Current page#: {current_page_number}")
            
            current_page_number += 1 # Update current page number
            
            
            route(driver)  # Collect data from the new page
        
        except Exception as e:
            print(f"successfully moved to last page# {current_page_number}")
            break
    
    return bus_routes_list # Returns the list of tuples containing all route details.






try:
    
    #*************************************
    #       ******MAIN FUNCTION****
    #*************************************
    
    # Initialize the WebDriver with chrome browser
    driver = webdriver.Chrome()
            
    # Maximize the browser window
    driver.maximize_window()   

    #Initialize a List for Bus Details:
    bus_routes_list = []
    bus_details_list = []

    #1.KERALA KSRTC - 17 routes, 2 pages
    #kerala_bus_link= 'https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile'   
    state_name = 'ksrtc-kerala'
    last_page_number = 2
    print("Extracting KERALA State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))
    
    #2.TSRTC TELANGANA - 26 routes, 3 pages
    #telangana_bus_link= 'https://www.redbus.in/online-booking/tsrtc/?utm_source=rtchometile' 
    state_name = 'tsrtc'
    last_page_number = 3
    print("Extracting TELANGANA State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))


    #3.APSRTC Andhra - 50 routes, 5 pages
    #andhra_bus_link= 'https://www.redbus.in/online-booking/apsrtc/?utm_source=rtchometile'  
    state_name = 'apsrtc'
    last_page_number = 5
    print("Extracting ANDHRA State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #4.Kadamba Transport Corporation Limited (KTCL) 45 Routes & 5 pages
    #kadamba_bus_link= 'https://www.redbus.in/online-booking/ktcl/?utm_source=rtchometile'   
    state_name = 'ktcl'
    last_page_number = 5
    print("Extracting KADAMBA State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #5. RSRTC Rajastan  20 Routes & 2 pages
    #rajastan_bus_link= 'https://www.redbus.in/online-booking/rsrtc/?utm_source=rtchometile' 
    state_name = 'rsrtc'
    last_page_number = 2
    print("Extracting RAJASTAN State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #6. SBSTC SOUTH BENGAL 43 routs & 5 pages
    #south_bengal_bus_link= 'https://www.redbus.in/online-booking/south-bengal-state-transport-corporation-sbstc/?utm_source=rtchometile'    
    state_name = 'south-bengal-state-transport-corporation-sbstc'
    last_page_number = 5
    print("Extracting SOUTH BENGAL State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #7. HRTC Himachal 37 routes & 4 pages
    #_bus_link= 'https://www.redbus.in/online-booking/hrtc/?utm_source=rtchometile'   
    state_name = 'hrtc'
    last_page_number = 4
    print("Extracting HIMACHAL State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #8. UPSRTC Uttar Pradesh 48 routes & 5 pages
    #_bus_link= 'https://www.redbus.in/online-booking/uttar-pradesh-state-road-transport-corporation-upsrtc/?utm_source=rtchometile'    
    state_name = 'uttar-pradesh-state-road-transport-corporation-upsrtc'
    last_page_number = 5
    print("Extracting UTTAR PRADESH State Bus Routes and Links")
    bus_routes_list = extract_route_details(driver,state_name,last_page_number)
    print("current bus routes list length",len(bus_routes_list))

    #9. JKSRTC Jammu & Kashmir 3 routes 1 page
    #_bus_link= 'https://www.redbus.in/online-booking/jksrtc'    
    #last_page_number = 1
    print("Extracting JAMMU & KASHMIR State Bus Routes and Links")
    state_name = 'jksrtc'
    page_link = f"""https://www.redbus.in/online-booking/{state_name}/?utm_source=rtchometile"""
    driver.get(page_link)
    route(driver)
    print("current bus routes list length",len(bus_routes_list))

    #10. West Bengal 4 routes 1 page
    #_bus_link= 'https://www.redbus.in/online-booking/west-bengal-transport-corporation/?utm_source=rtchometile'    
    #last_page_number = 1
    print("Extracting West Bengal State Bus Routes and Links")
    state_name = 'west-bengal-transport-corporation'
    page_link = f"""https://www.redbus.in/online-booking/{state_name}/?utm_source=rtchometile"""
    driver.get(page_link)
    route(driver)
    print("current bus routes list length",len(bus_routes_list))
    
     
    bus_details_list = get_bus_details(driver,bus_routes_list) # Iterate over the route links to extract all bus details
    print(f"Total buses in the list: {len(bus_details_list)}")
        

    
    insert_data_as_dataframe(bus_details_list) # Insert the scraped data into the database

except Exception as e:
    print("***Exception***", str(e))
