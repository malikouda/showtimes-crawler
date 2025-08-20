import logging, random
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from notify import notify


logging.basicConfig(
    filename="logs/universal.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def crawl():
    logging.info("BEGIN APPLICATION")
    random_sleep_time = random.randint(0, 15)
    logging.info("Sleeping for %s seconds", random_sleep_time)
    sleep(random_sleep_time)

    url = "https://www.universalorlando.com/web-store/en/us/add-ons"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        logging.info(f"Accessing url: {url}")
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-aui-content-id*="VIP"]')
            )
        )

        vip_card = driver.find_element(By.CSS_SELECTOR, '[data-aui-content-id*="VIP"]')

        select_button = vip_card.find_element(By.CSS_SELECTOR, '[aria-label="Select"]')

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(select_button))

        select_button.click()

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-aui="UNIVERSAL EPIC UNIVERSE"]')
            )
        )

        epic_button = driver.find_element(
            By.CSS_SELECTOR, '[data-aui="UNIVERSAL EPIC UNIVERSE"]'
        )

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(epic_button))

        epic_button.click()

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-label="add one Adult VIP Experience"]')
            )
        )

        add_button = driver.find_element(
            By.CSS_SELECTOR, '[aria-label="add one Adult VIP Experience"]'
        )

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(add_button))

        add_button.click()
        add_button.click()

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "gds-sticky-nav-footer-bottom")
            )
        )

        nav_footer = driver.find_element(By.CLASS_NAME, "gds-sticky-nav-footer-bottom")

        next_button = nav_footer.find_element(By.TAG_NAME, "button")

        next_button.click()

        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div[class='purchase-product-content multi-day']")
            )
        )

        inner_window = driver.find_element(
            By.CSS_SELECTOR, "div[class='purchase-product-content multi-day']"
        )
        body = driver.find_element(By.TAG_NAME, "body").text
        while "December 2025" not in body:
            driver.implicitly_wait(5)
            inner_window.click()
            inner_window.send_keys(Keys.PAGE_DOWN)
            body = driver.find_element(By.TAG_NAME, "body").text

        september_header = driver.find_element(
            By.XPATH, '//div[text()="September 2025"]'
        )

        calendar = september_header.find_element(By.XPATH, "./ancestor::gds-calendar")

        date_range = range(8, 13)

        for date in date_range:
            day = calendar.find_element(
                By.CSS_SELECTOR, f'[aria-label*="VIP Experience - Sep {date}, 2025"]'
            )
            label = day.get_attribute("aria-label")
            if "Unavailable" not in label:
                notify(
                    title="Universal VIP Scraper",
                    message=label,
                    url=url,
                )
            else:
                logging.info(label)

    except Exception as e:
        logging.error(f"There was a problem while running the program: {str(e)}")
        notify(
            "Universal VIP Scraper",
            message=f"Scraper had an error: {str(e)}",
            priority=1,
        )
    finally:
        driver.quit()
        logging.info(f"Application has completed and will terminate")
    logging.info("END APPLICATION")


if __name__ == "__main__":
    crawl()
