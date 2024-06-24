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
    for arg in sys.argv[1:]:
        if re.match(r"^\d{2}-\d{2}-\d{4}$", arg) or re.match(r"^\d{4}-\d{2}-\d{2}$", arg):
            input_date_str: str = arg
            break
    else:
        return date.today().isoformat()

    try:
        if re.match(r"^\d{2}-\d{2}-\d{4}$", input_date_str):
            input_date = datetime.strptime(input_date_str, "%d-%m-%Y")
        else:
            input_date = datetime.strptime(input_date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use either DD-MM-YYYY or YYYY-MM-DD.")
        sys.exit(1)

    return input_date.date().isoformat()


def get_wordle_data(date_string: str) -> WordleAPIData:
    """
    Fetches the Wordle game data for a given date from the New York Times Wordle API.

    Parameters:
    - date_string (str): The date for which to fetch the Wordle data, in 'YYYY-MM-DD' format.

    Returns:
    - WordleAPIData: A dictionary containing the Wordle game data for the specified date.

    Raises:
    - SystemExit: If the request to the Wordle API fails with a non-200 status code, the
    function prints the error and exits the program.
    """

    # Construct the URL for the Wordle API request using the provided date string
    url: str = f"https://www.nytimes.com/svc/wordle/v2/{date_string}.json"

    # Make the GET request to the Wordle API
    response = requests.get(url, timeout=300)

    # Check if the response status code indicates an error
    if response.status_code != 200:
        # Print the error details and exit the program
        print(f"There was a {response.status_code} error when getting the data from the Wordle API")
        print(response.json())
        sys.exit(1)

    # Return the JSON response data as a dictionary
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
    formatted_date: str = parsed_date.strftime("%d %B %Y")

    solution_text = f"Wordle Solution ({formatted_date}): {wordle['solution']}"

    print(solution_text)

    requests.post(
        url=NTFY_URL,
        data=f"Wordle of the Day: {wordle['solution']} 🔠".encode("utf-8"),
        headers={
            "Title": f"Wordle Solution ({formatted_date})",
            "Tags": "book,wordle,"
        },
        timeout=300
    )

    if "-w" in sys.argv:
        filename: str = f"Wordle_Solution_{iso_date}.txt"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(solution_text)
            print(f"Solution saved to {filename}")


if __name__ == "__main__":
    main()
