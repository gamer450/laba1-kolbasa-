from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_driver():
    """Настройка WebDriver"""
    options = webdriver.ChromeOptions()
    # Убери # у следующей строки чтобы браузер не открывался
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def scrape_dynamic_page():
    """Сбор данных с динамической страницы"""
    print("\n" + "=" * 60)
    print("ЭТАП D: SELENIUM")
    print("=" * 60)

    driver = None
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    import pandas as pd
    from pathlib import Path
    import time
    import logging
    import os

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    def setup_driver():
        """Настройка WebDriver"""
        options = webdriver.ChromeOptions()
        # Раскомментируй следующую строку, чтобы браузер не открывался
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(options=options)

    def scrape_dynamic_page():
        """Сбор данных с динамической страницы"""
        print("\n" + "=" * 60)
        print("ЭТАП D: SELENIUM")
        print("=" * 60)

        driver = None
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            import pandas as pd
            from pathlib import Path
            import time
            import logging
            import os

            # Настройка логирования
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)

            def setup_driver():
                """Настройка WebDriver"""
                options = webdriver.ChromeOptions()
                # Раскомментируй для работы без браузера
                # options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                return webdriver.Chrome(options=options)

            def scrape_dynamic_page():
                """Сбор данных с динамической страницы"""
                print("\n" + "=" * 60)
                print("ЭТАП D: SELENIUM")
                print("=" * 60)

                driver = None
                try:
                    # 1. Запуск браузера
                    print("Запуск браузера...")
                    driver = setup_driver()

                    # 2. Переход на страницу
                    url = "http://127.0.0.1:8000/dynamic"
                    print(f"Переход на {url}")
                    driver.get(url)
                    time.sleep(2)  # Даём странице загрузиться

                    # 3. Ожидание загрузки кнопки
                    print("Ожидание кнопки...")
                    wait = WebDriverWait(driver, 10)
                    button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Загрузить данные')]")))

                    # 4. Нажатие кнопки
                    print("Нажатие кнопки загрузки...")
                    button.click()

                    # 5. Ожидание появления таблицы
                    print("Ожидание данных...")
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                    time.sleep(1)

                    # 6. Применение фильтра
                    print("Применение фильтра по категории...")
                    filter_select = driver.find_element(By.ID, "categoryFilter")
                    filter_select.click()
                    option = driver.find_element(By.XPATH, "//option[@value='Электроника']")
                    option.click()
                    time.sleep(2)

                    # 7. Сбор данных из таблицы
                    print("Сбор данных...")
                    table = driver.find_element(By.TAG_NAME, "table")
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    data = []
                    for row in rows[1:]:  # Пропускаем заголовок
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells and len(cells) >= 6:
                            row_data = {
                                'id': int(cells[0].text),
                                'name': cells[1].text,
                                'category': cells[2].text,
                                'value': float(cells[3].text),
                                'updated_at': cells[4].text,
                                'active': cells[5].text == 'Да'
                            }
                            data.append(row_data)

                    if not data:
                        print("Внимание: данные не найдены!")
                        # Попробуем собрать без фильтра
                        print("Пробуем собрать без фильтра...")
                        filter_select = driver.find_element(By.ID, "categoryFilter")
                        filter_select.click()
                        option_all = driver.find_element(By.XPATH, "//option[@value='all']")
                        option_all.click()
                        time.sleep(1)

                        table = driver.find_element(By.TAG_NAME, "table")
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        for row in rows[1:]:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if cells and len(cells) >= 6:
                                row_data = {
                                    'id': int(cells[0].text),
                                    'name': cells[1].text,
                                    'category': cells[2].text,
                                    'value': float(cells[3].text),
                                    'updated_at': cells[4].text,
                                    'active': cells[5].text == 'Да'
                                }
                                data.append(row_data)

                    df = pd.DataFrame(data)
                    print(f"Собрано записей: {len(df)}")
                    if not df.empty:
                        print(df)
                    else:
                        print("Данные не найдены - проверьте, что сервер работает и содержит данные")

                    # 8. Сохранение
                    Path('results').mkdir(parents=True, exist_ok=True)
                    df.to_csv('results/selenium_items.csv', index=False, encoding='utf-8-sig')
                    print("Данные сохранены в results/selenium_items.csv")

                    return df

                except TimeoutException:
                    logger.error("Превышено время ожидания")
                    print("Ошибка: превышено время ожидания элемента")
                    return None

                except NoSuchElementException as e:
                    logger.error(f"Элемент не найден: {e}")
                    print(f"Ошибка: элемент не найден - {e}")
                    return None

                except Exception as e:
                    logger.error(f"Ошибка: {e}")
                    print(f"Ошибка: {e}")
                    return None

                finally:
                    if driver:
                        print("Закрытие браузера...")
                        driver.quit()

            if __name__ == "__main__":
                print("=" * 60)
                print("ВНИМАНИЕ: Убедись что backend.py запущен!")
                print("=" * 60)

                # Переключаемся в корень проекта
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                os.chdir(project_root)
                print(f"Рабочая директория: {os.getcwd()}")

                scrape_dynamic_page()
        except TimeoutException:
            logger.error("Превышено время ожидания")
            print("Ошибка: превышено время ожидания элемента")
            return None

        except NoSuchElementException as e:
            logger.error(f"Элемент не найден: {e}")
            print(f"Ошибка: элемент не найден - {e}")
            return None

        except Exception as e:
            logger.error(f"Ошибка: {e}")
            print(f"Ошибка: {e}")
            return None

        finally:
            if driver:
                print("Закрытие браузера...")
                driver.quit()

    if __name__ == "__main__":
        print("=" * 60)
        print("ВНИМАНИЕ: Убедись что backend.py запущен!")
        print("=" * 60)

        # Переключаемся в корень проекта
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)

        scrape_dynamic_page()