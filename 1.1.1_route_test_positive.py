from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# from selenium import scrollIntoView
import time
import route_data

# Опции браузера
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

# Инициализация браузера
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

try:
    # Открываем сайт IDOS.cz
    driver.get("https://www.idos.cz/")

    # Согласие на использование куки
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
        print("Accepted cookies")
    except Exception as e:
        print("Cookie consent button not found or not clickable")

    # Находим и заполняем поле начальной точки
    from_input = wait.until(EC.presence_of_element_located((By.ID, "From")))
    from_input.clear()
    from_input.send_keys(route_data.address_from)
    time.sleep(1)  # Задержка для отображения автозаполнения

    # Находим и заполняем поле конечной точки
    to_input = driver.find_element(By.ID, "To")
    to_input.clear()
    to_input.send_keys(route_data.address_to)
    time.sleep(1)  # Задержка для отображения автозаполнения

    # Запускаем поиск, нажимая клавишу Enter
    to_input.send_keys(Keys.ENTER)

    # Ожидаем появления результатов поиска
    results = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "connection-list")))
    results.scrollIntoView({behavior: 'smooth', block: 'end'})

    # Проверяем наличие маршрутов
    connections = results.find_elements(By.CLASS_NAME, "connection")
    if connections:
        print("Test passed - found routes.")
    else:
        print("Test failed - no routes found.")

except Exception as e:
    print(f"Test failed due to exception: {e}")

finally:
    # Закрываем браузер
    driver.quit()
