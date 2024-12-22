import sys
import time

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
wait = WebDriverWait(driver, 15)

try:
    driver.get("https://www.idos.cz/")

    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
        print("Accepted cookies")
    except Exception as e:
        print("Cookie consent button not found or not clickable")

    odkud_input = wait.until(EC.presence_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(route_data.address_from)
    time.sleep(1)

    kam_input = driver.find_element(By.ID, "To")
    kam_input.clear()
    kam_input.send_keys(route_data.address_to)
    time.sleep(1)

    kam_input.send_keys(Keys.ENTER)

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