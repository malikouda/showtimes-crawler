import logging, random
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from notify import notify
from config import settings


logging.basicConfig(
    filename="showtimes.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def crawl():
    logging.info("BEGIN ALAMO APPLICATION")
    random_sleep_time = random.randint(0, 61)
    logging.info("Sleeping for %s seconds", random_sleep_time)
    sleep(random_sleep_time)

    url = "https://drafthouse.com/austin"
    options = Options()
    options.headless = True
    options.add_argument("--disable-extensions")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    )
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        logging.info(f"Accessing url: {url}")
        driver.get(url)

        logging.info("Waiting for page content")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "film-wall"))
        )

        logging.info("Loading all films")
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@ng-click='$ctrl.loadMore()']")
            )
        )
        load_more_button = driver.find_element(
            By.XPATH, "//button[@ng-click='$ctrl.loadMore()']"
        )
        load_more_button.click()
        sleep(10)

        logging.info("Getting list of all current films")
        films = driver.find_elements(By.CLASS_NAME, "market-film")
        found_films = []
        alt_showings = {}
        for film in films:
            title = film.find_element(By.CSS_SELECTOR, "alamo-card-title").text

            # temporary fix - not sure why this movie keeps notifying
            if "A NIGHTMARE ON ELM STREET" in title:
                continue

            if title in found_films:
                if title in alt_showings:
                    alt_showings[title] += 1
                else:
                    alt_showings[title] = 1
                found_films.append(f"{title} (ALT SHOWING #{alt_showings[title]})")
            else:
                found_films.append(title)

        logging.info(
            "Films retrieved, comparing to last list to see if films have been added"
        )
        found_films = set(found_films)

        with open("films.txt", "r") as f:
            last_found = set(f.read().splitlines())

        added_films = found_films - last_found

        num_new_films = len(added_films)
        num_total_films = len(found_films)

        new_film_str = "\n".join(sorted(list(added_films)))
        found_films_str = "\n".join(sorted(list(found_films)))
        if new_film_str:
            logging.info(f"Found {num_new_films} new films of {num_total_films} total.")
            if len(new_film_str) > 1024:
                logging.warning(
                    "List of films larger than 1024 characters. Sending to ctxt.io page and notifying via Pushover"
                )
                # Pushover messages are limited to 1024 characters, so if we are larger than that
                # we can use ctxt.io to store the message and send the ctxt URL instead
                ctxt_url = requests.post(
                    settings.CTXT_URL,
                    data={
                        "content": f"<pre><code>{new_film_str}</code></pre>",
                        "ttl": "1d",
                    },
                ).url
                message = (
                    f"{new_film_str[:512]}...\nSee the full list here:\n{ctxt_url}"
                )
            else:
                logging.info("Notifying new films via Pushover.")
                message = new_film_str
            notify(
                title=f"{num_new_films} New Film(s) Found at the Alamo Drafthouse",
                message=message,
                priority=0,
                url=url,
            )
        else:
            logging.info(f"No new films found. Found {num_total_films} films.")

        logging.info("Updating film log with current film list.")
        with open("films.txt", "w") as f:
            f.write(found_films_str)

    except Exception as e:
        logging.error(f"There was a problem while running the program: {e}")
        notify(
            "Alamo Drafthouse Scraper Error",
            message=f"Scraper had an error: {e}",
            priority=1,
        )
    finally:
        driver.quit()
        logging.info(f"Application has completed and will terminate")
    logging.info("END APPLICATION")


if __name__ == "__main__":
    crawl()
