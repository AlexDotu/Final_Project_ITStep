import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Импорт корректных логина и пароля из файла 'route_data.py'
import sys
import os

sys.path.append('/Users/Alex/ITStepAcademy/Final_Project/Test_Scripts_python/Supporting_files')
from route_data import valid_email, valid_password

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 1)

try:
    driver.get("https://www.idos.cz/")

    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button")))
        cookie_button.click()
        print("Accepted cookies")
    except Exception as e:
        print("Cookie consent button not found or not clickable")

    def random_email():
        # Генерирует случайный e-mail с некорректным форматом
        local_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=random.randint(5, 10)))
        domain_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=random.randint(2, 5)))
        if random.random() > 0.5:  # Иногда делаем неправильный формат
            return f"{local_part}@{domain_part}"  # Правильный формат
        else:
            return f"{local_part}{domain_part}"  # Без "@"


    def random_password():
        #Генерирует случайный пароль.
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*', k=random.randint(8, 16)))


    def check_label_error(css_selector):
        #Проверяет наличие ошибки по селектору.
        try:
            error_message = driver.find_element(By.CSS_SELECTOR, css_selector)
            return error_message.is_displayed()
        except Exception:
            return False


    def login_test(email, password):
        # Ввод логина, пароля и проверка успешного входа
        email_input = wait.until(EC.visibility_of_element_located((By.ID, "Email")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "Password")))

        # Очистка полей и ввод значений
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)

        # Нажимаем иконку глаза для отображения пароля
        try:
            eye_icon = driver.find_element(By.CSS_SELECTOR, "i.fa-regular.eye-ico")
            eye_icon.click()
            print("Password is now visible.")
        except Exception as e:
            print("Eye icon for password visibility not found:", e)

        # Нажимаем кнопку "Přihlásit se"
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-orange btn-small btn-shadow w-full']")))
        login_button.click()

        # Далее ждём успешного входа или ошибки:
        try:
            # Проверяем наличие имени пользователя после успешного входа
            user_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn.btn-lightblue.btn-shadow.btn-link.userName"))
            )
            print(f"Login successful. User button found: {user_button.text}")
            return True
        except Exception:
            print("User button not found. Login might have failed.")

        # Проверка на ошибку "Chybně zadaný e-mail nebo heslo."
        try:
            login_error = driver.find_element(By.XPATH, "//span[contains(text(), 'Chybně zadaný e-mail nebo heslo.')]")
            if login_error.is_displayed():
                print("Login failed: Incorrect email or password.")
                return False
        except Exception:
            print("No specific login error message found.")

        print("Login status unknown. Assuming failure.")
        return False

    try:
        # Переход на сайт и нажатие кнопки "Přihlásit"
        driver.get("https://idos.cz")
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'btn-lightblue') and contains(@title, 'Přihlásit')]")))
        login_button.click()

        # Негативные сценарии: 2 попытки с неправильными данными
        for attempt in range(10):
            print(f"Attempt {attempt + 1} with random incorrect credentials.")
            random_email_address = random_email()
            random_password_text = random_password()
            success = login_test(random_email_address, random_password_text)
            if success:
                print("Unexpected success with invalid credentials! Exiting test.")
                break

        # Позитивный сценарий: вводим правильные логин и пароль из файла 'route_data.py'
        print("Attempting login with valid credentials.")
        if login_test(valid_email, valid_password):
            print("Login successful with valid credentials.")

        else:
            print("Failed to login with valid credentials. Exiting test.")
    except Exception as e:
        print(f"Test failed due to exception: {e}")
finally:
    # Завершение теста, переход к результатам в PyCharm
    driver.quit()
    print("Test completed.")
