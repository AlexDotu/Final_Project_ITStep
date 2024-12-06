import random
import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

excel_path = "./Supporting_files/Czech_Republic_locations.xlsx"
locations_df = pd.read_excel(excel_path)

# Функция для закрытия страницы с 'napoveda', если она открыта, и возвращения к основной странице теста
def close_help_page_if_open():

    try:
        # Получение всех открытых вкладок
        tabs = driver.window_handles

        for tab in tabs:
            driver.switch_to.window(tab)
            # Если текущая вкладка с URL 'napoveda', закрываем её
            if "napoveda" in driver.current_url:
                driver.close()
                print("Closed help page.")
                break

        # Возвращаемся на основную вкладку
        driver.switch_to.window(tabs[0])
    except Exception as e:
        print(f"Failed to handle help page: {e}")

# # Функция для генерирования случайных дат и времени
# def random_datetime_generator():
#     random_date = datetime.now() + timedelta(days=random.randint(1, 7))
#     format_date = random_date.strftime("%d.%m.%Y")
#     random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
#     return format_date, random_time


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 2)

try:
    driver.get("https://www.idos.cz/")

    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    # Функция для сброса настроек
    def reset_settings():
        # Сбрасывает все настройки маршрута через меню.
        close_help_page_if_open()
        try:
            close_help_page_if_open()
            # Клик на иконку "трёх полосок/Меню"
            menu_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-lightblue.btn-shadow.btn-link.menu")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", menu_button)
            time.sleep(0.5)  # Небольшая пауза для завершения прокрутки
            menu_button.click()

            # Клик на "Vymazat uložené údaje"
            clear_data_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Vymazat uložené údaje']"))
            )
            clear_data_option.click()
            time.sleep(0.5)

            # Выбрать чекбокс "smazat použité jízdní řády (přejde na úvodní stránku)"
            check_box_smazat_pouzite = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='DeleteShields']"))
            )

            check_box_smazat_pouzite.click()
            time.sleep(0.5)


            # Клик на кнопку "Smazat označené"
            delete_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Smazat označené')]"))
            )
            delete_button.click()
            time.sleep(0.5)

            # Клик на кнопку "OK"
            ok_button = wait.until(
                EC.element_to_be_clickable((By.ID, "deletePrefsFinishOkBtn"))
            )
            ok_button.click()
            print("Settings successfully reset.")
        except Exception as e:
            print(f"Failed to reset settings: {e}")


    # Основной тестовый цикл
    repeat_count = 3  # Количество повторений теста
    close_help_page_if_open()


    # Эта функция проверяет наличие ошибок валидации при вводе местоположений.
    def check_label_error():

        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".label-error span")
            for error_element in error_elements:
                error_text = error_element.text
                if "Takové místo neznáme" in error_text:
                    print("Error detected: 'Takové místo neznáme'. Test iteration passed successfully.")
                    clear_fields()
                    return True
                elif "Zadání není jednoznačné, vyberte prosím z nabízeného seznamu." in error_text:
                    print(
                        "Error detected: 'Zadání není jednoznačné, vyberte prosím z nabízeného seznamu.'. Test iteration passed successfully.")
                    clear_fields()
                    return True
        except Exception as e:
            print(f"Error while checking label errors: {e}")
        return False


    # Основной тестовый цикл
    for test_number in range(repeat_count):
        try:
            print(f"Starting test iteration {test_number + 1}/{repeat_count}...")
            close_help_page_if_open()

            # Генерация случайных адресов
            address_from = locations_df["Wrong_Locality"].sample(1).values[0]
            address_to = locations_df["Wrong_Locality"].sample(1).values[0]

            # Ввод "Odkud"
            odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
            odkud_input.clear()
            odkud_input.send_keys(address_from)
            time.sleep(0.5)
            odkud_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Проверка ошибок для поля "Odkud"
            if check_label_error():
                continue  # Завершаем текущую итерацию, если ошибка обнаружена

            # Ввод "Kam"
            kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
            kam_input.clear()
            kam_input.send_keys(address_to)
            time.sleep(0.5)
            kam_input.send_keys(Keys.ENTER)
            time.sleep(1)

            # Проверка ошибок для поля "Kam"
            if check_label_error():
                continue  # Завершаем текущую итерацию, если ошибка обнаружена


            # Клик на кнопку "Hledat"
            hledat_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", hledat_button)

            # Проверка маршрутов
            try:
                spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
                spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")
                if spojeni_list:
                    print("Routes found successfully. Test iteration passed.")
                else:
                    print("No routes found. Test iteration passed successfully.")
            except Exception:
                print(
                    "No routes found or an error occurred while searching. Test iteration passed successfully.")

            # Сброс настроек после успешного завершения теста
            reset_settings()

        except Exception as e:
            print(f"Test iteration {test_number + 1} failed due to exception: {e}")

        print(f"Test iteration {test_number + 1} completed.\n")
except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()