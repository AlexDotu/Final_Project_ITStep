import os
import random
import time
import pandas as pd  # Для работы с Excel
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# Загрузка списка локаций из Excel
excel_path = "./Supporting_files/Czech_Republic_Locations.xlsx"
locations_df = pd.read_excel(excel_path)

# Данные рандомно берутся из столбца "Locality", находящегося в файле CzechRepublicLocations.xlsx
locations = locations_df['Locality'].tolist()


# Папка для сохранения скриншотов
screenshot_folder = "./Supporting_files/Map_screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 3)

# Общий счётчик скриншотов
total_screenshots = 0

def close_help_page_if_open():
    try:
        tabs = driver.window_handles
        for tab in tabs:
            driver.switch_to.window(tab)
            if "napoveda" in driver.current_url:
                driver.close()
                print("Closed help page.")
                break
        driver.switch_to.window(tabs[0])
    except Exception as e:
        print(f"Failed to handle help page: {e}")

def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time

def clear_fields():
    for field_id in ["From", "To", "Date", "Time"]:
        input_field = driver.find_element(By.ID, field_id)
        input_field.clear()
        time.sleep(0.2)

def check_label_error():
    try:
        error_elements = driver.find_elements(By.CSS_SELECTOR, ".label-error span")
        for error_element in error_elements:
            error_text = error_element.text
            if "Takové místo neznáme" in error_text:
                print("Error: 'Takové místo neznáme' detected.")
                clear_fields()
                return True
            elif "Zadání není jednoznačné, vyberte prosím z nabízeného seznamu." in error_text:
                print("Error: 'Zadání není одноznačné...' detected.")
                clear_fields()
                return True
    except Exception as e:
        print(f"Error checking for label error: {e}")
    return False

def fill_odkud_with_random_location(field_id, field_name):
    while True:
        random_location = random.choice(locations)
        input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
        input_field.clear()
        input_field.send_keys(random_location)
        time.sleep(1)
        try:
            suggestion_list = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".idos-autosuggest__suggestions-container"))
            )
            suggestions = suggestion_list.find_elements(By.CSS_SELECTOR, ".idos-autosuggest__suggestion")
            if suggestions:
                random.choice(suggestions).click()
                print(f"Selected location '{random_location}' for '{field_name}'.")
                return
        except Exception:
            pass
        if check_label_error():
            continue

def fill_kam_with_random_location(field_id, field_name):
    while True:
        try:
            random_location = random.choice(locations)
            input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
            input_field.clear()
            input_field.send_keys(random_location)
            time.sleep(1)
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".label-error")
            if error_elements:
                error_texts = [error.text.strip() for error in error_elements if error.text.strip()]
                if "Takové místo neznáme." in error_texts:
                    print(f"Retrying input for '{field_name}' due to error: {error_texts}")
                    continue
            input_field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            input_field.send_keys(Keys.ENTER)
            print(f"Selected location '{random_location}' for '{field_name}'.")
            return
        except Exception as e:
            print(f"Error during '{field_name}' input: {e}")
            time.sleep(1)

 # Сохраняет скриншот карты с уникальным именем файла.
def take_screenshot(route_index, iteration_index):

    global total_screenshots
    screenshot_path = os.path.join(screenshot_folder, f"iteration_{iteration_index + 1}_route_{route_index + 1}.png")
    driver.save_screenshot(screenshot_path)
    total_screenshots += 1
    print(f"Screenshot saved: {screenshot_path}")


def process_route_maps(iteration_index):
    try:
        spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
        spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")
        if spojeni_list:
            print(f"Found {len(spojeni_list)} routes. Processing maps...")
            for index, connection in enumerate(spojeni_list):
                try:
                    map_icon = connection.find_element(By.CSS_SELECTOR, ".ico-map")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", map_icon)
                    time.sleep(1)
                    map_icon.click()
                    print(f"Opened map for route {index + 1}.")
                    time.sleep(1)
                    take_screenshot(index, iteration_index)  # Передаем номер итерации
                    close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".popup-close.popup-close-map")))
                    time.sleep(1)
                    close_button.click()
                    print(f"Closed map for route {index + 1}.")

                except Exception as e:
                    print(f"Failed to process map for route {index + 1}: {e}")
        else:
            print("No routes available to process maps.")
    except Exception as e:
        print(f"Error while processing route maps: {e}")


def search_spojeni(iteration_index):
    fill_odkud_with_random_location("From", "Odkud")
    fill_kam_with_random_location("To", "Kam")
    close_help_page_if_open()
    random_date, random_time = random_datetime_generator()
    print(f"Generated random date: {random_date}, time: {random_time}")
    date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
    time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))
    driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
    driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)
    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    driver.execute_script("arguments[0].click();", hledat_button)
    try:
        NoRoutesFound_ModalWindow = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-in.idos-modal__content--560")))
        close_button = NoRoutesFound_ModalWindow.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")
        if NoRoutesFound_ModalWindow:
            close_button.click()
            print("Error modal detected and closed. Retrying search...")
            clear_fields()
            search_spojeni(iteration_index)
            return
    except Exception:
        pass
    process_route_maps(iteration_index)  # Передаем номер итерации

try:
    driver.get("https://www.idos.cz/")
    close_help_page_if_open()
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)
    repeat_count = 1
    for i in range(repeat_count):
        print(f"Starting test iteration {i + 1}/{repeat_count}...")
        search_spojeni(i)  # Передаем индекс текущей итерации
        print(f"Completed iteration {i + 1}.")

    print(f"All test iterations completed. Total screenshots taken: {total_screenshots}.")
except Exception as e:
    print(f"Test failed due to exception: {e}")
finally:
    driver.quit()
