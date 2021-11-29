import logging

from notify import notify

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


logging.basicConfig(
    filename="pizza_showtimes.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def crawl():
    logging.info("BEGIN APPLICATION")
    found = False
    url = "https://drafthouse.com/market/tickets/35mm:+licorice+pizza/0004/172636/showtimes"
    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(chrome_options=chrome_options)

    try:
        logging.info(f"Accessing url: {url}")
        driver.get(url)

        logging.info("Waiting for page content to load")
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "alamo-showtime-sliders > alamo-slider.showtime-slider.showtime-slider--time > div > div.slider-container__spacer > div > button > span",
                )
            )
        )

        elts = driver.find_elements(
            By.CSS_SELECTOR,
            "alamo-showtime-sliders > alamo-slider.showtime-slider.showtime-slider--time > div > div.slider-container__spacer > div > button > span",
        )

        logging.info("Checking showtimes for availability...")
        for elt in elts:
            if elt.get_attribute("class") == "status--soldout":
                logging.info(
                    f"Found a showing that is not sold out at {elt.text}, notifying via Pushover..."
                )
                found = True
                try:
                    notify(
                        title="Licorice Pizza Tickets Available",
                        message="Licorice pizza showtimes are now available at the Alamo Drafthouse",
                        url=url,
                        priority=1,
                    )
                    logging.info(f"Pushover notification sent")
                    break
                except Exception as e:
                    logging.error(f"There was an issue notifying via Pushover: {e}")
            else:
                logging.info(f"Showing at {elt.text} is sold out")

        if not found:
            logging.warning("All showtimes are sold out")

    except Exception as e:
        logging.error(f"There was a problem while searching the page: {e}")
    finally:
        driver.quit()
        logging.info(f"Application has completed and will terminate")
    logging.info("END APPLICATION")


if __name__ == "__main__":
    crawl()
