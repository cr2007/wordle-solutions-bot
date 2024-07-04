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
    """
    Parses command line arguments for a date string and returns it in ISO format (YYYY-MM-DD).

    If no valid date string is found in the arguments, returns today's date in ISO format.

    Supports date strings in DD-MM-YYYY or YYYY-MM-DD format.

    Returns:
    - str: The date in ISO format (YYYY-MM-DD).

    Raises:
    - SystemExit: If an invalid date format is provided.
    """

    # Iterate over command line arguments to find a valid date string
    for arg in sys.argv[1:]:
        # Check if the argument matches the expected date formats
        if re.match(r"^\d{2}-\d{2}-\d{4}$", arg) or re.match(r"^\d{4}-\d{2}-\d{2}$", arg):
            input_date_str: str = arg
            break
    else:
        # If no date argument is found, return today's date in ISO format
        return date.today().isoformat()

    # Attempt to parse the found date string
    try:
        # Parse date string in DD-MM-YYYY format
        if re.match(r"^\d{2}-\d{2}-\d{4}$", input_date_str):
            input_date = datetime.strptime(input_date_str, "%d-%m-%Y")
        # Parse date string in YYYY-MM-DD format
        else:
            input_date = datetime.strptime(input_date_str, "%Y-%m-%d")
    except ValueError:
        # If parsing fails, print an error message and exit
        print("Invalid date format. Please use either DD-MM-YYYY or YYYY-MM-DD.")
        sys.exit(1)

    # Return the parsed date in ISO format
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
    """
    Main function to fetch and post the Wordle solution for a specified or current date.
    """

    # Load environment variables from a .env file
    load_dotenv()

    # Retrieve the NTFY_URL from environment variables
    NTFY_URL = os.getenv("NTFY_URL")

    # Fetch the date for which to retrieve the Wordle solution
    iso_date = get_date()

    # Fetch the Wordle data for the specified date
    wordle = get_wordle_data(iso_date)

    # Parse and format the date for display
    parsed_date: datetime = datetime.strptime(iso_date, "%Y-%m-%d")
    formatted_date: str = parsed_date.strftime("%d %B %Y")

    # Construct the solution text
    solution_text = f"Wordle Solution ({formatted_date}): {wordle['solution']}"

    # Print the solution text
    print(solution_text)

    if NTFY_URL is not None:
        # Sends a push notification via ntfy with the Wordle solution
        requests.post(
            url=NTFY_URL,
            data=f"Wordle of the Day: {wordle['solution']} 🔠".encode("utf-8"),
            headers={
                "Title": f"Wordle Solution ({formatted_date})",
                "Tags": "book,wordle,"
            },
            timeout=300
        )
    else:
        print("NTFY_URL is not set in the environment variables")
        print("Please set it to the URL of your ntfy instance if you want to receive "
              "push notifications.")
        print("More Info: https://docs.ntfy.sh")

    # Check if the '-w' flag is present in command line arguments to write the solution to a file
    if "-w" in sys.argv:
        filename: str = f"solutions/Wordle_Solution_{iso_date}.txt"

        # If the 'solutions' directory does not exist, create it
        if not os.path.exists("solutions"):
            print("Creating 'solutions' directory...")
            os.makedirs("solutions")

        # Write the solution to a text file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(solution_text)
            print(f"Solution saved to {filename}")


if __name__ == "__main__":
    main()
