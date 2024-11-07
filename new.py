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

# Настройки веб-драйвера
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

# Функция генерации случайной даты и времени
def random_datetime_generator():
    random_date = datetime.now() + timedelta(days=random.randint(1, 7))
    format_date = random_date.strftime("%d.%m.%Y")
    random_time = f"{random.randint(0, 23):02}:{random.randint(0, 59):02}"
    return format_date, random_time

try:
    driver.get("https://www.idos.cz/")

    # Нажатие на кнопку согласия с куки
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
    except Exception as e:
        print("Cookie consent button not found or not clickable:", e)

    # Ввод адреса отправления
    odkud_input = wait.until(EC.visibility_of_element_located((By.ID, "From")))
    odkud_input.clear()
    odkud_input.send_keys(route_data.address_from_2)

    # Проверка на ошибку "Takové místo neznáme" для адреса отправления
    odkud_input_error_message = driver.find_elements(By.XPATH, "//*[contains(@class,'label-error')]")
    if odkud_input_error_message:
        print("Invalid or nonexistent departure address! TEST PASSED - system doesn't accept invalid addresses.")
        # driver.quit()
        # exit()
        odkud_input.send_keys(Keys.TAB)
    # Переход к следующему полю
    time.sleep(1)
    odkud_input.send_keys(Keys.TAB)

    # Ввод адреса назначения
    kam_input = wait.until(EC.visibility_of_element_located((By.ID, "To")))
    kam_input.clear()
    kam_input.send_keys(route_data.address_to_2)

    # Проверка на ошибку "Takové místo neznáme" для адреса назначения
    kam_input_error_message = driver.find_elements(By.XPATH, "//*[contains(@class, 'label-error') and contains(text(), 'Takové místo neznáme.')]")
    if kam_input_error_message:
        print("Invalid or nonexistent destination address! TEST PASSED - system doesn't accept invalid addresses.")
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", kam_input)
        driver.quit()
        exit()
        # pass
        # kam_input.send_keys(Keys.TAB)
    # Если ошибок нет, продолжаем выполнение теста
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

    # Переход к следующему элементу
    date_input.send_keys(Keys.TAB)
    time_input.send_keys(Keys.TAB)
    time.sleep(0.5)

    # Выбор радиокнопки "Odjezd"
    odjezd_radioBox = driver.find_element(By.ID, "byArrival-departure")
    odjezd_radioBox.send_keys(Keys.TAB)
    time.sleep(1)

    # Нажатие на кнопку "Hledat"
    hledat_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(@class, 'btn btn-orange btn-small btn-shadow w-full')]")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", hledat_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", hledat_button)

    # Ожидание и прокрутка к результатам маршрута
    route_results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", route_results)
    time.sleep(1)

    # Проверка наличия маршрутов
    connections = route_results.find_elements(By.CLASS_NAME, "connection")
    if connections:
        print("Test passed! Routes found successfully.")
    else:
        print("No routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    driver.quit()
