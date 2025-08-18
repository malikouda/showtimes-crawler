import logging, random, os
from time import sleep
from pathlib import Path
from collections import namedtuple

import requests

from notify import notify

Show = namedtuple("Show", ["event_type", "super_title", "title"])

logging.basicConfig(
    filename="showtimes_v2.txt",
    format="%(asctime)s :: %(levelname)s :: %(message)s",
    encoding="utf-8",
    level=logging.INFO,
)


def chunk_respect_line_break(text, chunk_size):
    if not text:
        return None
    if not text.endswith("\n"):
        text += "\n"
    start_idx = 0
    end_idx = 0
    chunks = []

    while end_idx < len(text):
        end_idx = text.rfind("\n", start_idx, chunk_size + start_idx) + 1
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx

    return chunks


def crawl():
    border = "-" * 10
    logging.info("{0} BEGIN ALAMO APPLICATION {0}".format(border))
    random_sleep_time = random.randint(1, 5)
    logging.info("Sleeping for %s seconds", random_sleep_time)
    sleep(random_sleep_time)

    url = "https://drafthouse.com/s/mother/v2/schedule/market/austin"

    try:
        data = requests.get(url).json()["data"]

        presentations = data["presentations"]
        shows = dict()
        for p in presentations:
            show = Show(
                event_type=(p.get("eventType") or {}).get("title"),
                super_title=(p.get("superTitle") or {}).get("superTitle"),
                title=p["show"]["title"],
            )
            shows[p["slug"]] = show

        shows_file = "films_v2.txt"
        if os.path.exists(shows_file):
            with open(shows_file, "r") as f:
                existing_show_slugs = set(f.read().splitlines())
        else:
            file_path = Path(shows_file)
            file_path.touch()
            existing_show_slugs = set()

        current_show_slugs = set(slug for slug in shows.keys())
        new_show_slugs = current_show_slugs - existing_show_slugs

        shows_to_notify = [shows[slug] for slug in new_show_slugs]

        overlapping_tags = ["Movie Party"]

        new_shows_titles = []
        for show in shows_to_notify:
            msg = ""
            if (
                show.event_type
                and show.super_title
                and (
                    show.event_type == show.super_title
                    or f"{show.event_type}s" == show.super_title
                    or f"{show.event_type}" in overlapping_tags
                    or f"{show.super_title}" in overlapping_tags
                )
            ):
                msg += f"[{show.event_type}] "
            else:
                if show.event_type:
                    msg += f"[{show.event_type}] "
                if show.super_title:
                    msg += f"[{show.super_title}] "
            msg += show.title
            new_shows_titles.append(msg)

        new_shows_notification_msg = "\n".join((sorted(new_shows_titles)))

        messages = chunk_respect_line_break(new_shows_notification_msg, 1024)

        if messages:
            logging.info(
                f"Found {len(new_show_slugs)} new films of {len(current_show_slugs)} total."
            )
            for i, message in enumerate(messages):
                sleep(1)
                notification_title = f"{len(new_show_slugs)} New Film{'s' if len(new_show_slugs) > 1 else ''} Found at the Alamo Drafthouse"
                logging.info(f"Sending notification: {notification_title}")
                if len(messages) > 1:
                    notification_title += f" ({i+1}/{len(messages)})"
                notify(
                    title=notification_title,
                    message=message.strip(),
                    priority=0,
                    url=url,
                )
        else:
            logging.info(f"No new films found. Found {len(current_show_slugs)} films.")

        current_shows_slug_str = "\n".join(sorted(list(current_show_slugs)))
        
        with open(shows_file, "w") as f:
            f.write(current_shows_slug_str)

    except Exception as e:
        logging.error("There was a problem while running the program: %s", str(e))
        notify(
            "Alamo Drafthouse Scraper Error",
            message=f"Scraper had an error: {str(e)}",
            priority=1,
        )
    
    logging.info("{0} END ALAMO APPLICATION {0}".format(border))


if __name__ == "__main__":
    crawl()
