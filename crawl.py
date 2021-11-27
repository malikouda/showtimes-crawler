import re, logging

from notify import notify

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


logging.basicConfig(
    filename="showtimes.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def crawl():
    logging.info("BEGIN APPLICATION")
    found = False
    url = "https://www.thestoryoftexas.com/visit/see-films"
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    try:
        logging.info(f"Accessing url: {url}")
        driver.get(url)

        logging.info("Waiting for page content")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-content"))
        )

        pattern = re.compile(r"spider[- ]?man", flags=re.IGNORECASE)

        logging.info(
            f"Searching for film title cards with regex pattern: {pattern.pattern}"
        )
        elements = driver.find_elements_by_css_selector("div.film-item > h3 > a")
        for element in elements:
            match = pattern.match(element.text)
            if match:
                found = True
                href = element.get_attribute("href")
                logging.info(
                    f"MATCH FOUND: Title card ({element.text}) matches pattern {pattern.pattern}. URL: {href}"
                )
                logging.info("Attempting to notify via Pushover")
                try:
                    notify(
                        title="Spider-Man: No Way Home Tickets On Sale",
                        message="Spider-Man: No Way Home tickets are on sale now at the Bob Bullock IMAX theater.",
                        url=href,
                        priority=1,
                    )
                    logging.info(f"Pushover notification sent")
                    break
                except Exception as e:
                    logging.error(f"There was an issue notifying via Pushover: {e}")
            else:
                logging.info(
                    f"Title card ({element.text}) does not match pattern: {pattern.pattern}"
                )
        if not found:
            logging.warning(f"NO MATCHES FOUND for pattern: {pattern.pattern}")

    except Exception as e:
        logging.error(f"There was a problem while searching the page: {e}")
    finally:
        driver.quit()
        logging.info(f"Application has completed and will terminate")
    logging.info("END APPLICATION")


if __name__ == "__main__":
    crawl()
