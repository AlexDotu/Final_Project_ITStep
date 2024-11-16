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

excel_path = "Supporting_files/CzechRepublicLocations.xlsx"
locations_df = pd.read_excel(excel_path)


def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

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
    time.sleep(0.5)
    odkud_input.send_keys(Keys.ENTER)
    time.sleep(1)

    try:
        suggestion_list = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".idos-autosuggest__suggestions-container"))
        )
        if suggestion_list:
            first_suggestion = suggestion_list.find_element(By.CSS_SELECTOR, ".idos-autosuggest__suggestion")
            time.sleep(0.5)
            first_suggestion.click()
            print(
                f"For \"{address_from}\" address clarification needed ! Selected the first suggestion from dropdown list.")
        else:
            pass
    except Exception as e:
        print(f"No address clarification needed for \"{address_from}\" or an error occurred: {e}")

    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(address_to)
    time.sleep(1)
    kam_input.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    kam_input.send_keys(Keys.ARROW_DOWN)
    kam_input.send_keys(Keys.ENTER)

    try:
        suggestion_list = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".idos-autosuggest__suggestions-container"))
        )
        if suggestion_list:
            first_suggestion = suggestion_list.find_element(By.CSS_SELECTOR, ".idos-autosuggest__suggestion")
            first_suggestion.click()
            print(
                f"For \"{address_to}\" address clarification needed! Selected the first suggestion from dropdown list.")
        else:
            pass
    except Exception:
        print(f"For \"{address_to}\" address clarification needed! Selected the first suggestion from dropdown list.")

    random_date, random_time = random_datetime_generator()
    print(f"Generated random date: {random_date}, time: {random_time}")

    date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
    time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))

    driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
    driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)

    date_input.send_keys(Keys.ESCAPE)
    date_input.send_keys(Keys.TAB)
    time_input.send_keys(Keys.TAB)

    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", route_results)
    time.sleep(1)

    connections = route_results.find_elements(By.CLASS_NAME, "connection")
    if connections:
        print("Routes found successfully.")
    else:
        print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
