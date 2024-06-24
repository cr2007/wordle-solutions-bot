import re
import sys
import os
from datetime import datetime, date
from typing import TypedDict
from dotenv import load_dotenv
import requests

# {
#     "id": 1691,
#     "solution": "proud",
#     "print_date": "2024-06-15",
#     "days_since_launch": 1092,
#     "editor": "Tracy Bennett"
# }

class WordleAPIData(TypedDict):
    id:                int
    solution:          str
    print_date:        str
    days_since_launch: int
    editor:            str

def get_date() -> str:
    if len(sys.argv) > 1:
        dd_mm_yyyy_pattern = re.compile(r"^\d{2}-\d{2}-\d{4}$")
        yyyy_mm_dd_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

        input_date_str: str = sys.argv[1]

        try:
            if dd_mm_yyyy_pattern.match(input_date_str):
                input_date = datetime.strptime(input_date_str, "%d-%m-%Y")
            elif yyyy_mm_dd_pattern.match(input_date_str):
                input_date = datetime.strptime(input_date_str, "%Y-%m-%d")
            else:
                print("Invalid date format. Please use either DD-MM-YYYY or YYYY-MM-DD.")
                sys.exit(1)
        except ValueError as e:
            print("Value error appeared:", e)
            sys.exit(1)

        return input_date.date().isoformat()

    return date.today().isoformat()


def get_wordle_data(date_string: str) -> WordleAPIData:
    url: str = f"https://www.nytimes.com/svc/wordle/v2/{date_string}.json"

    response = requests.get(url, timeout=300)

    if response.status_code != 200:
        print(f"There was a {response.status_code} error when getting the data from the Wordle API")
        print(response.json())
        sys.exit(1)

    return response.json()


def main():
    load_dotenv()

    NTFY_URL = os.getenv("NTFY_URL")

    if NTFY_URL is None:
        print("NTFY_URL is not set in the environment variables")
        print("Please set it to the URL of your ntfy instance and try again")
        sys.exit(1)

    iso_date = get_date()

    wordle = get_wordle_data(iso_date)

    parsed_date: datetime = datetime.strptime(iso_date, "%Y-%m-%d")
    formatted_date = parsed_date.strftime("%d %B %Y")

    print(f"Wordle Solution ({formatted_date}): {wordle['solution']}")


if __name__ == "__main__":
    main()
