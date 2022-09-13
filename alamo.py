import logging, random
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from notify import notify

logging.basicConfig(
    filename="showtimes.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def crawl():
    logging.info("BEGIN APPLICATION")
    random_sleep_time = random.randint(0, 31)
    logging.info("Sleeping for %s seconds", random_sleep_time)
    sleep(random_sleep_time)

    url = "https://drafthouse.com/austin"
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
            EC.presence_of_element_located((By.CLASS_NAME, "film-wall"))
        )

        logging.info("Loading all films")
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@ng-click='$ctrl.loadMore()']")
            )
        )
        load_more_button = driver.find_element_by_xpath(
            "//button[@ng-click='$ctrl.loadMore()']"
        )
        load_more_button.click()
        sleep(10)

        logging.info("Getting list of all current films")
        films = driver.find_elements_by_class_name("market-film")
        found_films = []
        alt_showings = {}
        for film in films:
            title = film.find_element_by_css_selector("alamo-card-title").text

            if title in found_films:
                if title in alt_showings:
                    alt_showings[title] += 1
                else:
                    alt_showings = 1
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

        logging.info("Sending Pushover notification")
        new_film_str = "\n".join(list(added_films))
        found_films = "\n".join(list(found_films))
        if new_film_str:
            notify(
                title=f"{len(added_films)} New Film(s) Found at the Alamo Drafthouse",
                message=new_film_str,
                priority=0,
                url=url,
            )
        else:
            notify(
                title="No New Films Found at the Alamo Drafthouse",
                message=found_films,
                priority=-2,
                url=url,
            )

        logging.info("Writing found films to text file")
        with open("films.txt", "w") as f:
            for film in found_films:
                f.write(f"{film}\n")

    except Exception as e:
        logging.error(f"There was a problem while running the program: {e}")
    finally:
        driver.quit()
        logging.info(f"Application has completed and will terminate")
    logging.info("END APPLICATION")


if __name__ == "__main__":
    crawl()