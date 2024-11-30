import random
import time
import pandas as pd
from datetime import datetime, timedelta
# from Supporting_files import All_Wornings_and_Errors_to_Avoid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

excel_path = "Supporting_files/CzechRepublicLocations.xlsx"
locations_df = pd.read_excel(excel_path)


def close_help_page_if_open():
    """Закрывает страницу 'napoveda', если она открыта, и возвращается к основной."""
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

# Функция для генерирования случайных дат и времени
def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time


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
        """Сбрасывает все настройки маршрута через меню."""
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
    repeat_count = 100  # Количество повторений теста
    close_help_page_if_open()

    for test_number in range(repeat_count):

        try:
            print(f"Starting test iteration {test_number + 1}/{repeat_count}...")

            close_help_page_if_open() # Закрываем доп.страницу

            # Генерация рандомных адресов
            address_from = locations_df["Locality"].sample(1).values[0]
            address_to = locations_df["Locality"].sample(1).values[0]

            # Ввод "Odkud"
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
                    print(f"For \"{address_from}\" address clarification needed! Selected the first suggestion.")
            except Exception:
                print(f"No address clarification needed for \"{address_from}\".")

            # Ввод "Kam"
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
                    print(f"For \"{address_to}\" address clarification needed! Selected the first suggestion.")
            except Exception:
                print(f"No address clarification needed for \"{address_to}\".")

            # Генерация и ввод случайных даты и времени
            random_date, random_time = random_datetime_generator()
            print(f"Generated random date: {random_date}, time: {random_time}")

            date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
            time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))

            driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
            driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)

            date_input.send_keys(Keys.ESCAPE)
            date_input.send_keys(Keys.TAB)
            time_input.send_keys(Keys.TAB)

            # Клик на кнопку "Hledat"
            hledat_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", hledat_button)

            # Обрабатываем исключение для всплывающего окна, если маршрут не найден
            try:
                NoRoutesFound_ModalWindow = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-in.idos-modal__content--560")))
                close_button = NoRoutesFound_ModalWindow.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")

                popUp_window = driver.find_elements(By.CLASS_NAME, "popup-in")

                if NoRoutesFound_ModalWindow:
                    close_button.click()
                    print("Error modal detected and closed. Retrying search...")
                    clear_fields()  # Очищаем поля и запускаем повторный поиск
                    search_spojeni()

                elif popUp_window:
                    close_button = popUp_window[0].find_element(By.XPATH,
                                                                ".//button[@class='swal-button swal-button--cancel']")
                    print("No direct routes available. Closing popup and suggesting to adjust the route points...")
                    close_button.click()
                    # time.sleep(1)
                    search_spojeni()

            except Exception:
                pass

            # Ожидание и проверка результатов маршрута
            spojeni_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", spojeni_results)
            time.sleep(1)

            spojeni_list = spojeni_results.find_elements(By.CLASS_NAME, "connection")
            if spojeni_list:
                print("Routes found successfully.")
            else:
                print("No routes found.")

            # Сброс настроек после теста
            reset_settings()

        except Exception as e:
            print(f"Test iteration {test_number + 1} failed due to exception: {e}")

        print(f"Test iteration {test_number + 1} completed.\n")

finally:
    driver.quit()
    print("All tests completed.")
