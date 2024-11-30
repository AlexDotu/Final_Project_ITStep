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

# Импорт функций для обработки ошибок и предупреждений
from Test_Scripts_python.Supporting_files.All_Warnings_and_Errors_Avoid import (
    warnings_and_notifications_clear,
    close_help_page_if_open,
    close_survey_if_open,
)

# Загрузка данных из Excel
excel_path = "CzechRepublicLocations.xlsx"
locations_df = pd.read_excel(excel_path)

# Функция для генерации случайных даты и времени
def random_datetime_generator():
    now = datetime.now()
    random_date = now + timedelta(days=random.randint(1, 7))
    if random_date.date() == now.date():
        start_hour = now.hour + 1
    else:
        start_hour = 0
    random_time = f"{random.randint(start_hour, 23):02}:{random.randint(0, 59):02}"
    return random_date.strftime("%d.%m.%Y"), random_time

# Настройки WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 5)

# Проверяет наличие ошибки 'Takové místo neznáme'
def takove_misto_nezname():
    try:
        error_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".label-error")))
        if "Takové místo neznáme" in error_message.text:
            odkud_input.send_keys(Keys.ARROW_DOWN)
            kam_input.send_keys(Keys.ARROW_DOWN)
            print("Detected error: 'Takové místo neznáme'. Retrying...")
            return True
    except Exception:
        # Если ошибка отсутствует, то идем дальше
        pass

# Добавляем переменную-счетчик перед началом тестов
total_favorites_added = 0

try:
    driver.get("https://www.idos.cz/")

    # Согласие с куки
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    # Количество повторов теста
    repeat_count = 3  # Укажите количество повторов теста

    for test_iteration in range(repeat_count):
        print(f"Starting test iteration {test_iteration + 1}/{repeat_count}...")
        warnings_and_notifications_clear(driver)
        # Очистка всплывающих окон перед началом итерации
        close_help_page_if_open(driver)
        close_survey_if_open(driver)
        warnings_and_notifications_clear(driver)

        takove_misto_nezname()
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
                    total_favorites_added += 1  # Увеличиваем счетчик
                    time.sleep(1)
                except Exception as e:
                    print(f"Failed to add route {index + 1} to favorites: {e}")

        # Очистка полей поиска для следующей итерации
        try:
            clear_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Vymazat')]")))
            clear_button.click()
            print("Search fields cleared.")
        except Exception as e:
            print(f"Failed to clear search fields: {e}")

    # Переход в "Избранное"
    print("Opening 'Favorites'...")
    favorites_button = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".my-connection.btn.btn-blue.btn-shadow")))
    favorites_button.click()

    # Ожидание страницы "Избранное" и прокрутка до конца
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    print(f"Test PASSED! Total favorites added: {total_favorites_added}")  # Итоговый результат

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
    print(f"All tests completed. Total favorites added: {total_favorites_added}")  # Итоговый результат
