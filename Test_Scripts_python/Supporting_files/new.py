import random
import time
from datetime import datetime, timedelta

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

excel_path = "CzechRepublicLocations.xls"
locations_df = pd.read_excel(excel_path)

def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time


try:
    driver.get("https://www.idos.cz/")

    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()

    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    address_from = locations_df["Locality"].sample(1).values[0]
    address_to = locations_df["Locality"].sample(1).values[0]

    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(address_from)
    odkud_input.send_keys(Keys.TAB)

    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(address_to)
    kam_input.send_keys(Keys.TAB)

    random_date, random_time = random_datetime_generator()
    print(f"Generated random date: {random_date}, time: {random_time}")

    date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
    time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))

    driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
    driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)
    time.sleep(1)

    date_input.send_keys(Keys.ESCAPE)
    time.sleep(0.5)

    date_input.send_keys(Keys.TAB)
    time_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    odjezd_radioBox = driver.find_element(By.ID, "byArrival-departure")
    odjezd_radioBox.send_keys(Keys.TAB)
    time.sleep(1)

    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    connections = route_results.find_elements(By.CLASS_NAME, "connection")

    if connections:
        print(f"Found {len(connections)} routes. Processing each route...")

        for index, connection in enumerate(connections):

            try:
                map_icon = connection.find_element(By.CSS_SELECTOR, ".ico-map")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", map_icon)
                time.sleep(1)
                map_icon.click()
                print(f"Opened map for route {index + 1}.")

                close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".popup-close.popup-close-map")))
                time.sleep(1.5)
                close_button.click()
                print(f"Closed map for route {index + 1}.")
                time.sleep(1)

            except Exception as e:
                print(f"Failed to process map for route {index + 1}: {e}")

    else:
        print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
