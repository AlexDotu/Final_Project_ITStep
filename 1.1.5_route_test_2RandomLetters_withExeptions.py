import random
import time
from datetime import datetime, timedelta

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
wait = WebDriverWait(driver, 3)


def random_letters():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2))


def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time

def check_label_error():
    # Проверяет наличие ошибок с классом 'label-error' и обрабатывает их. Возвращает True, если ошибка обнаружена и обработана, иначе False.
    try:
        # Явное ожидание элемента ошибки
        error_elements = driver.find_elements(By.CSS_SELECTOR, ".label-error span")
        for error_element in error_elements:
            error_text = error_element.text
            if "Takové místo neznáme" in error_text:
                print("Error: 'Takové místo neznáme' detected.")
                clear_fields()
                return True
            elif "Zadání není jednoznačné, vyberte prosím z nabízeného seznamu." in error_text:
                print("Error: 'Zadání není jednoznačné...' detected.")
                clear_fields()
                return True
    except Exception as e:
        print(f"Error checking for label error: {e}")
    return False


def fill_field_with_random_letters(field_id, field_name):
    # Заполнение поля Odkud/Kam случайными буквами и выбор из выпадающего списка.
    while True:
        random_text = random_letters()
        input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
        input_field.clear()
        input_field.send_keys(random_text)
        time.sleep(1)

        try:
            suggestion_list = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".idos-autosuggest__suggestions-container"))
            )
            suggestions = suggestion_list.find_elements(By.CSS_SELECTOR, ".idos-autosuggest__suggestion")
            if suggestions:
                random.choice(suggestions).click()
                print(f"Randomly selected suggestion for '{field_name}' with text '{random_text}'.")
                return
        except Exception:
            pass

        if check_label_error(): # Проверяем наличие ошибки "Takové místo neznáme"
            continue

def fill_kam_field_via_keyboard(field_id, field_name):
    # Заполняет поле 'Kam' случайными буквами, проверяет наличие ошибок, и повторяет процесс до успешного ввода.
    while True:
        try:
            # Генерируем случайный текст и вводим его в поле
            random_text = random_letters()
            input_field = wait.until(EC.visibility_of_element_located((By.ID, field_id)))
            input_field.clear()
            input_field.send_keys(random_text)
            time.sleep(1)

            # Проверяем наличие ошибок
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".label-error")
            if error_elements:
                error_texts = [error.text.strip() for error in error_elements if error.text.strip()]

                if "Takové místo neznáme." in error_texts:
                    print(f"Retrying input for '{field_name}' due to error: {error_texts}")
                    continue  # Повторяем ввод, не выполняем код ниже

            # Если ошибки нет, выбираем первый элемент из выпадающего списка
            input_field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            input_field.send_keys(Keys.ENTER)
            print(f"Randomly selected suggestion for '{field_name}' with text '{random_text}'.")
            return # Успешный выход из цикла
        except Exception as e:
            print(f"Error during '{field_name}' input: {e}")
            time.sleep(1)


def search_spojeni():
    fill_field_with_random_letters("From", "Odkud")
    fill_kam_field_via_keyboard("To", "Kam")

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

    # Проверяем наличие ошибок и всплывающих окон
    try:
        NoRoutesFound_ModalWindow = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-in.idos-modal__content--560")))
        close_button = NoRoutesFound_ModalWindow.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")

        if NoRoutesFound_ModalWindow:
            close_button.click()
            print("Error modal detected and closed. Retrying search...")
            clear_fields()  # Очищаем поля и запускаем повторный поиск
            search_spojeni()
            return
    except Exception:
        pass

    # Проверяем наличие маршрутов
    try:
        spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", spojeni_results)
        time.sleep(1)

        spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")
        if spojeni_list:
            print("Routes found successfully.")
        else:
            print("No routes found.")
    except Exception as e:
        print(f"Error while checking routes: {e}")

try:
    driver.get("https://www.idos.cz/")

    # Принятие cookies
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    search_spojeni()

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
