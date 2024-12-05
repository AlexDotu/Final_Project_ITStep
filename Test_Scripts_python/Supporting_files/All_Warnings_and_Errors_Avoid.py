from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# options = webdriver.ChromeOptions()
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# wait = WebDriverWait(driver, 5)


def warnings_and_notifications_clear(driver):
    # Проверяет наличие ошибки 'Takové místo neznáme'
    try:
        # Явное ожидание элемента с ошибкой
        error_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".label-error")))
        if "Takové místo neznáme" in error_message.text:
            print("Detected error: 'Takové místo neznáme'. Retrying...")
            return True
    except Exception:
        # Если ошибка отсутствует, то идем дальше
        pass
        return False
    try:
        # Ожидаем появления всплывающего окна
        spojeni_nebylo_nalezeno = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent")))
        if spojeni_nebylo_nalezeno:
            # Закрытие окна
            close_button = driver.find_element(By.CSS_SELECTOR, ".swal-button--cancel")
            close_button.click()
            print("Сообщение 'Spojení nebylo nalezeno.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Spojení nebylo nalezeno': {e}")
        pass
        return False

    try:
        NoRoutesFound_ModalWindow = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-in.idos-modal__content--560")))
        close_button = NoRoutesFound_ModalWindow.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")

        popUp_window = driver.find_elements(By.CLASS_NAME, "popup-in")

        if NoRoutesFound_ModalWindow:
            close_button.click()
            print("Error modal detected and closed. Retrying search...")

            return True
        elif popUp_window:
            close_button = popUp_window[0].find_element(By.XPATH,
                                                        ".//button[@class='swal-button swal-button--cancel']")
            print("No direct routes available. Closing popup and suggesting to adjust the route points...")
            close_button.click()
            return True
    except Exception:
        pass
        return False

    try:
        handle_connection_list_not_available = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent"))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, ".swal-button--cancel")

        if handle_connection_list_not_available:
            close_button.click()
            print("Сообщение 'Seznam spojení již není k dispozici.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Seznam spojení již není k dispozici': {e}")
        pass
        return False

    try:
        handle_ticket_not_for_sale = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent"))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, ".swal-button--cancel")
        if handle_ticket_not_for_sale:
            close_button.click()
            print("Сообщение 'Jízdenku nelze prodat.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Jízdenku nelze prodat': {e}")
        pass
        return False

    try:
        handle_payment_error = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent"))
        )
        close_button = driver.find_element(By.ID, "basketErrorModalOkButton")
        if handle_payment_error:
            close_button.click()
            print("Сообщение 'Došlo ke změně košíku.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Došlo ke změně košíku': {e}")
        pass
        return False

    try:
        handle_general_error = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent"))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, ".swal-button--cancel")
        if handle_general_error:
            close_button.click()
            print("Сообщение 'Něco se nepovedlo.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Něco se nepovedlo': {e}")
        pass
        return False

    try:
        hdle_general_error = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "errorModalContent"))
        )
        close_button = driver.find_element(By.CSS_SELECTOR, ".swal-button--cancel")
        if hle_general_error:
            close_button.click()
            print("Сообщение 'Něco se nepovedlo.' обработано.")
            return True
    except Exception as e:
        print(f"Ошибка при обработке 'Něco se nepovedlo': {e}")
        pass
        return False

 # Проверяет наличие ошибки 'Takové místo neznáme' Проверяет наличие ошибок с классом 'label-error' и обрабатывает их. Возвращает True, если ошибка обнаружена и обработана, иначе False.

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


# =================================

def close_help_page_if_open(driver):
    # Закрывает страницу 'napoveda', если она открыта, и возвращается к основной.
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


# =================================


def close_survey_if_open(driver):
    # Закрывает появившееся окно с опросом нажатием на кнопку отказa "NE"
    try:
        # Явное ожидание элемента с ошибкой
        survey_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'id="invitation"')))
        close_button = driver.find_element(By.CSS_SELECTOR, "button.swal-button--cancel")
        if survey_message:
            print("Survey/Dotaznik opened. Clicked to 'NE'")
            close_button.click()
            return True

    except Exception:
        # Если popUp не появился, то идем дальше
        pass
        return False

# =================================
