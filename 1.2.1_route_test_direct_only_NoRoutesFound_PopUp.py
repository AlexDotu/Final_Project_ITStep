import random
import sys
import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

sys.path.append('/Users/Alex/ITStepAcademy/Final_Project/Test_Scripts_python/Supporting_files')
import route_data

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)


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

    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(route_data.address_from_2)
    odkud_input.send_keys(Keys.TAB)

    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(route_data.address_to_2)
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

    onlyDirectRoutes_CheckBox = driver.find_element(By.XPATH,
                                                    "//label[text()[normalize-space(.)='Pouze přímá spojení']]")
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                          onlyDirectRoutes_CheckBox)
    time.sleep(1)
    onlyDirectRoutes_CheckBox.click()
    time.sleep(1)

    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))

    driver.execute_script("arguments[0].click();", hledat_button)
    time.sleep(1)

    popUp_window = driver.find_elements(By.CLASS_NAME, "popup-in")
    if popUp_window:
        close_button = popUp_window[0].find_element(By.XPATH, ".//button[@class='swal-button swal-button--cancel']")
        print("No direct routes available. Closing popup and suggesting to adjust the route points...")
        close_button.click()
        time.sleep(1)

    else:
        spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", spojeni_results)
        time.sleep(1)

        spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")
        if spojeni_list:
            print("Routes found successfully.")
        else:
            print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
