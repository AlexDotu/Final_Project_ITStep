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
    print("Opening website...")
    driver.get("https://www.idos.cz/")

    # Нажатие кнопки согласия с куки
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
        print("Cookie consent button clicked.")
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    # Ввод начального и конечного адреса
    print("Filling 'From' field...")
    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(route_data.address_from_2)
    odkud_input.send_keys(Keys.TAB)

    print("Filling 'To' field...")
    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(route_data.address_to_2)
    kam_input.send_keys(Keys.TAB)

    # Генерация случайной даты и времени
    random_date, random_time = random_datetime_generator()
    print(f"Generated random date: {random_date}, time: {random_time}")

    date_input = wait.until(EC.presence_of_element_located((By.ID, "Date")))
    time_input = wait.until(EC.presence_of_element_located((By.ID, "Time")))

    # Установка даты и времени
    driver.execute_script("arguments[0].value = arguments[1];", date_input, random_date)
    driver.execute_script("arguments[0].value = arguments[1];", time_input, random_time)
    time.sleep(1)
    date_input.send_keys(Keys.ESCAPE)
    time.sleep(0.5)
    date_input.send_keys(Keys.TAB)
    time_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    # Установка флажка "Только прямые соединения"
    print("Selecting 'Direct connection only' checkbox...")
    onlyDirectRoutes_CheckBox = driver.find_element(By.XPATH,
                                                    "//label[text()[normalize-space(.)='Pouze přímá spojení']]")
    onlyDirectRoutes_CheckBox.click()
    time.sleep(1)

    # Нажатие на кнопку "Hledat"
    print("Clicking 'Hledat' button using JavaScript...")
    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    # Проверка на наличие попап-окна с использованием 'if' вместо 'wait.until'
    time.sleep(2)  # Небольшая задержка, чтобы попап успел появиться, если он будет
    popUp_window = driver.find_elements(By.CLASS_NAME, "popup-in")
    if popUp_window:
        close_button = popUp_window[0].find_element(By.XPATH, ".//button[@class='swal-button swal-button--cancel']")
        print("No direct routes available. Closing popup and suggesting to adjust the route points...")
        close_button.click()
        time.sleep(1)

        # Сообщение пользователю об отсутствии маршрутов и предложение скорректировать маршрут
        print("Маршруты не найдены. Пожалуйста, скорректируйте точки отправления и прибытия.")

    else:
        # Если попап не появился, продолжаем ожидание результатов
        print("No popup appeared, continuing to check for routes.")

        # Ожидание результатов маршрута и прокрутка к ним
        print("Waiting for route results...")
        route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", route_results)
        time.sleep(1)

        # Проверка наличия маршрутов
        connections = route_results.find_elements(By.CLASS_NAME, "connection")
        if connections:
            print("Routes found successfully.")
        else:
            print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
