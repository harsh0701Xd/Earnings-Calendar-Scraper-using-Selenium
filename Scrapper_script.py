from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

def filter_countries(driver, countries):

    # Wait for the filter button to be clickable
    filter_button = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.ID, "filterStateAnchor")))

    # Click the filter button
    filter_button.click()
    
    # Locate all country labels
    country_labels = driver.find_elements(By.XPATH, "//label[contains(@for, 'country')]")
    
    # Check if the default country filter is selected and deselect it if necessary
    default_country_checkbox = None
    for label in country_labels:
        country_name = label.text.strip()
        if country_name == "United States":
            default_country_checkbox = label.find_element(By.XPATH, "./preceding-sibling::input[@type='checkbox']")
            break

    if default_country_checkbox and default_country_checkbox.is_selected():
        default_country_checkbox.click()

    # Iterate over each label and check if it matches the user-provided country names
    for label in country_labels:
        country_name = label.text.strip()
        if country_name in countries:
            # If there's a match, find the associated checkbox and click it
            checkbox_id = label.get_attribute('for')
            checkbox = driver.find_element(By.ID, checkbox_id)
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", checkbox)
    

    apply_filter_button = driver.find_element(By.ID, "ecSubmitButton")
    apply_filter_button.click()


def select_date(driver, date_option, start_date=None, end_date=None, max_attempts=10):
    date_option_map = {
        "Yesterday": "timeFrame_yesterday",
        "Today": "timeFrame_today",
        "Tomorrow": "timeFrame_tomorrow",
        "This Week": "timeFrame_thisWeek",
        "Next Week": "timeFrame_nextWeek",
        "Custom Date": "datePickerToggleBtn"
    }

    attempt = 0
    while attempt < max_attempts:
        try:
            attempt += 1
            print(f"Attempt {attempt} to select dates...")

            # Click on the selected date option
            date_option_id = date_option_map.get(date_option, None)
            if date_option_id is not None:
                date_option_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, date_option_id))
                )
                date_option_element.click()
                
                # If "Custom Date" is selected, fill in start and end dates
                if date_option == "Custom Date" and start_date and end_date:
                    # Wait for the date picker to be visible
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "ui-datepicker-div"))
                    )

                    start_date_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "startDate"))
                    )
                    start_date_input.clear()
                    start_date_input.send_keys(start_date)

                    end_date_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "endDate"))
                    )
                    end_date_input.clear()
                    end_date_input.send_keys(end_date)

                    apply_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "applyBtn")))
                    apply_button.click()

                    # Check if the startDate element is found
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "startDate"))
                    )
                    print("Dates selected successfully.")
                    return
                else:
                    print(f"Date option '{date_option}' found.")
                    return
            else:
                print(f"Date option '{date_option}' not found.")
                return

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")
        
        print("Retrying...")

    print(f"Failed to select dates after {max_attempts} attempts.")
    raise Exception("Failed to select dates after multiple attempts.")


def fetch_earnings_calendar_table(driver):
    try:
        get_source = driver.page_source
        soup = BeautifulSoup(get_source, 'html.parser')
        table_id = 'earningsCalendarData'
        
        table = soup.find('table', {'id': table_id})
        # Check if the table was found
        if table:
            # Extract the table data into a pandas DataFrame
            df = pd.read_html(str(table))[0]
            return df
        else:
            print(f"Table with id '{table_id}' not found.")
            return None
    
    finally:
        # Ensure the WebDriver is closed regardless of success or failure
        pass


def preprocess_dataframe_for_aggregation(temp):
    # Create new columns based on the given logic
    temp["Company_Name"] = temp.iloc[:, 1]
    temp["EPS_Forecast"] = temp.iloc[:, 2].astype(str).str.cat(temp.iloc[:, 3].astype(str), sep=' ', na_rep='')
    temp["Revenue_Forecast_1"] = temp.iloc[:, 4].astype(str).str.cat(temp.iloc[:, 5].astype(str), sep=' ', na_rep='')
    temp["Market_Cap"] = temp.iloc[:, 6].astype(str)

    # Filter the DataFrame to keep only relevant columns and rows
    filter_df = temp[['Company_Name', 'EPS_Forecast', 'Revenue_Forecast_1', 'Market_Cap']]

    # Identify rows with dates
    date_rows = filter_df['Company_Name'].str.contains('day, ')

    # Extract dates and convert to datetime format
    filter_df.loc[date_rows, 'Date'] = pd.to_datetime(filter_df.loc[date_rows, 'Company_Name'])

    # Forward fill the dates
    filter_df['Date'] = filter_df['Date'].fillna(method='ffill')

    # Remove the date rows from the DataFrame
    filter_df = filter_df[~date_rows]

    # Reset the index
    filter_df.reset_index(drop=True, inplace=True)

    # Set the multi-index with Date and original index
    filter_df.set_index(['Date', filter_df.index], inplace=True)

    return filter_df

def setup_driver():
    firefox_options = Options()
    firefox_options.add_argument("--start-fullscreen")  # Open in full screen mode
    firefox_options.add_argument("--ignore-certificate-errors")  # This option is not typically used in Firefox; might need to handle differently
    firefox_options.add_argument("--disable-popup-blocking")
    firefox_options.add_argument("--disable-notifications")
    firefox_options.add_argument("--disable-extensions")
    firefox_options.add_argument("--disable-infobars")  # This option is not available in Firefox; it's specific to Chrome

    driver = webdriver.Firefox(options=firefox_options)
    return driver    



def filter_and_fetch_earnings_calendar(url, country_filter_list, date_option, start_date=None, end_date=None):
    driver = setup_driver()
    try:
        driver.get(url)
        
        filter_countries(driver, country_filter_list)

        time.sleep(5)

        select_date(driver, date_option, start_date, end_date)

        print("Retrieving Final Table.....")

        time.sleep(45)

        df = fetch_earnings_calendar_table(driver)
        final_df = preprocess_dataframe_for_aggregation(df)
        
        # Generate unique filename using current timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"earnings_calendar_{timestamp}.csv"
        
        # Save DataFrame to CSV file
        final_df.to_csv(filename, index=True)
        
        print(f"Data saved to '{filename}'")
    finally:
        driver.quit()

# Example usage
url = input("Enter the URL for the earnings calendar: ")
country_filter_str = input("Enter the countries to filter (comma-separated list): ")
country_filter_list = [country.strip().title() for country in country_filter_str.split(",")]
date_options = ["Yesterday", "Today", "Tomorrow", "This Week", "Next Week", "Custom Date"]

while True:
    date_option = input("Enter the date option (e.g., 'This Week', 'Custom Date'): ").title()

    if date_option in date_options:
        break
    else:
        print("Error: Please enter a valid date option.")


if date_option == "Custom Date":
    while True:
        try:
            start_date = input("Enter the start date (MM/DD/YYYY): ")
            datetime.strptime(start_date, "%m/%d/%Y")
            break
        except ValueError:
            print("Error: Please enter a valid start date in the format MM/DD/YYYY.")
            
    while True:
        try:
            end_date = input("Enter the end date (MM/DD/YYYY): ")
            datetime.strptime(end_date, "%m/%d/%Y")
            break
        except ValueError:
            print("Error: Please enter a valid end date in the format MM/DD/YYYY.")
else:
    start_date = None
    end_date = None

filter_and_fetch_earnings_calendar(url, country_filter_list, date_option, start_date, end_date)
