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


def random_letters():
    """Генерация случайных двух букв английского алфавита."""
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2))


def random_datetime_generator():
    """Генерация случайной даты и времени в пределах 7 дней."""
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time


def handle_error_and_retry():
    """Проверяет появление ошибки 'Spojení nebylo nalezeno' и закрывает её, если обнаружена."""
    try:
        # Ожидание появления окна ошибки
        error_modal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-in.idos-modal__content--560")))
        print("Error modal detected: No connection found.")

        # Нажатие кнопки 'Zavřít'
        close_button = error_modal.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")
        close_button.click()
        print("Error modal closed. Retrying...")

        # Небольшая пауза перед повторной попыткой
        time.sleep(1)
        return True
    except Exception as e:
        print(f"No error modal detected or failed to handle it: {e}")
        return False


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 5)

try:
    driver.get("https://www.idos.cz/")

    # Принятие cookies
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    def fill_field_with_random_letters(field_id, field_name):
        """Заполнение поля Odkud/Kam случайными буквами и выбор из выпадающего списка."""
        while True:
            # Генерация случайных двух букв
            random_text = random_letters()
            input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
            input_field.clear()
            input_field.send_keys(random_text)
            time.sleep(1)  # Ожидание появления выпадающего списка

            try:
                # Проверяем, есть ли выпадающий список
                suggestion_list_odkud = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".idos-autosuggest__suggestions-container"))
                )
                suggestions_odkud = suggestion_list_odkud.find_elements(By.CSS_SELECTOR, ".idos-autosuggest__suggestion")
                if suggestions_odkud:
                    # Выбираем случайный вариант из списка
                    random.choice(suggestions_odkud).click()
                    print(f"Randomly selected suggestion for '{field_name}' with text '{random_text}'.")
                    return
            except Exception:
                pass

            # Проверяем наличие ошибки "Takové místo neznáme"
            try:
                error_message_odkud = driver.find_element(By.CSS_SELECTOR, ".label-error")
                if "Takové místo neznáme" in error_message_odkud.text:
                    print(f"'{random_text}' not recognized for '{field_name}'. Retrying...")
                    continue
            except Exception:
                pass

    def fill_kam_field_via_keyboard_with_retry(field_id, field_name):
        """Заполняет поле 'Kam' двумя случайными буквами и выбирает первый элемент через клавиши стрелки и Enter."""
        while True:
            random_text = random_letters()
            input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
            input_field.clear()
            input_field.send_keys(random_text)
            time.sleep(0.5)  # Небольшая пауза для завершения обработки ввода

            try:
                # Симулируем выбор первого элемента в выпадающем списке
                input_field.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.5)  # Ожидание для надежности
                input_field.send_keys(Keys.ENTER)
                print(f"Input for '{field_name}': '{random_text}' - ARROW_DOWN and ENTER keys used.")
                return
            except Exception as e:
                print(f"Error while selecting from '{field_name}' with text '{random_text}': {e}")


    while True:
        # Заполняем поля Odkud и Kam
        fill_field_with_random_letters("From", "Odkud")
        fill_kam_field_via_keyboard_with_retry("To", "Kam")

        # Генерация случайной даты и времени
        random_date, random_time = random_datetime_generator()
        print(f"Generated random date: {random_date}, time: {random_time}")

        # Ввод даты и времени
        date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
        time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))

        driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
        driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)

        date_input.send_keys(Keys.ESCAPE)
        date_input.send_keys(Keys.TAB)
        time_input.send_keys(Keys.TAB)

        # Нажимаем кнопку "Hledat"
        hledat_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", hledat_button)

        # Обрабатываем результаты маршрутов
        try:
            route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", route_results)
            time.sleep(1)

            connections = route_results.find_elements(By.CLASS_NAME, "connection")
            if connections:
                print("Routes found successfully.")
                break  # Успешно завершить цикл
            else:
                print("No routes found.")
        except Exception:
            print("No routes found, retrying...")
            if not handle_error_and_retry():
                break  # Если ошибка не обработана, выходим из цикла

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
