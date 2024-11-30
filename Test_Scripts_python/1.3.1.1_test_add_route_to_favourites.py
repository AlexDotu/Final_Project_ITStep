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
from Test_Scripts_python.Supporting_files.All_Warnings_and_Errors_Avoid import (
    warnings_and_notifications_clear,
    close_help_page_if_open,
    close_survey_if_open,
)

# Загрузка данных из Excel
excel_path = "./Supporting_files/CzechRepublicLocations.xlsx"
locations_df = pd.read_excel(excel_path)

# Функция для генерации случайных даты и времени
def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time

# Настройки WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

try:
    driver.get("https://www.idos.cz/")

    # Согласие с куки
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    close_help_page_if_open()
    close_survey_if_open()
    # Выбор случайных адресов
    address_from = locations_df["Locality"].sample(1).values[0]
    address_to = locations_df["Locality"].sample(1).values[0]

    # Заполнение полей "Odkud" и "Kam"
    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(address_from)
    odkud_input.send_keys(Keys.TAB)

    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(address_to)
    kam_input.send_keys(Keys.TAB)

    # Генерация случайной даты и времени
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

    # Клик на кнопку "Hledat"
    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    # Ожидание появления результатов
    spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")

    if spojeni_list:
        print(f"Found {len(spojeni_list)} routes. Adding to favorites...")

        for index, connection in enumerate(spojeni_list):
            try:
                # Клик на иконку "Добавить в избранное"
                favorite_icon = connection.find_element(By.CSS_SELECTOR, ".ico-mc")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", favorite_icon)
                time.sleep(0.5)
                favorite_icon.click()
                print(f"Added route {index + 1} to favorites.")
                time.sleep(1)
            except Exception as e:
                print(f"Failed to add route {index + 1} to favorites: {e}")

    # Переход в "Избранное"
    try:
        favorites_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".my-connection.btn.btn-blue.btn-shadow")))
        favorites_button.click()

        # Ожидание страницы "Избранное" и прокрутка до конца
        time.sleep(1)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        print("'Favorites' opened, all added routes inside!")
    except Exception:
        pass

finally:
    driver.quit()
    print("All tests completed.")
