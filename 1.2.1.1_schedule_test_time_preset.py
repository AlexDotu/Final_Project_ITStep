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


try:
    # Переход на сайт
    driver.get("https://www.idos.cz/")

    # Принятие cookies
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    # Переход к расписаниям
    try:
        timetable_button = wait.until(EC.visibility_of_element_located((By.ID, "timetablesModalLink")))
        timetable_button.click()
    except Exception as e:
        print("Timetable button not found or not clickable:", e)

    # Проверяем наличие iframe перед переключением
    try:
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        print("Switched to iframe successfully.")
    except Exception as e:
        print("No iframe found or unable to switch to iframe:", e)

    # Выбор опции маршрута (например, "Spojení", "Odjezdy ze zastávky" и т.д.)
    try:
        route_options = wait.until(
            EC.visibility_of_all_elements_located((By.XPATH, "//ul[contains(@class, 'tabs-timetable')]"))
        )
        random_route_option = random.choice(route_options)
        driver.execute_script("arguments[0].click();", random_route_option)
        time.sleep(1)
        print("Random route option selected successfully.")
    except Exception as e:
        print("No route options found:", e)

    # Выбор категории вида транспорта (например, "Všechny jízdní řády", "Vlaky + Autobusy" и т.д.)
    try:
        transport_options = wait.until(
            EC.visibility_of_all_elements_located(
                (By.XPATH, "//div[@class='left']//ul[contains(@class, 'box-links')]//a")
            )
        )
        random_transport_option = random.choice(transport_options)
        driver.execute_script("arguments[0].click();", random_transport_option)
        time.sleep(1)
        print("Random transport option selected successfully.")
    except Exception as e:
        print("No transport options found:", e)

    # Переключаемся обратно на основной контент, если iframe больше не нужен
    driver.switch_to.default_content()

    # Ввод данных маршрута
    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(route_data.address_from_1)
    odkud_input.send_keys(Keys.TAB)

    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(route_data.address_to_1)
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

    odjezd_radioBox = driver.find_element(By.ID, "byArrival-departure")
    odjezd_radioBox.send_keys(Keys.TAB)
    time.sleep(1)

    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", route_results)
    time.sleep(1)

    connections = route_results.find_elements(By.CLASS_NAME, "connection")
    if connections:
        print("Routes found successfully.")
    else:
        print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
