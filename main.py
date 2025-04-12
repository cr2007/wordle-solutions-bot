import re
import sys
import os
from datetime import datetime, date
from typing import TypedDict, Optional
from dotenv import load_dotenv
import click
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

def parse_date(date_input: Optional[str]) -> str:
    """
    Parses command line arguments for a date string and returns it in ISO format (YYYY-MM-DD).

    If no valid date string is found in the arguments, returns today's date in ISO format.

    Supports date strings in DD-MM-YYYY or YYYY-MM-DD format.

    Returns:
    - str: The date in ISO format (YYYY-MM-DD).

    Raises:
    - SystemExit: If an invalid date format is provided.
    """

    if date_input is None:
        return date.today().isoformat()

    try:
        # Try both formats
        if re.match(r"^\d{2}-\d{2}-\d{4}$", date_input):
            return datetime.strptime(date_input, "%d-%m-%Y").date().isoformat()
        elif re.match(r"^\d{4}-\d{2}-\d{2}$", date_input):
            return datetime.strptime(date_input, "%Y-%m-%d").date().isoformat()
        else:
            raise ValueError
    except ValueError:
        raise click.BadParameter("Invalid date format. Use either DD-MM-YYYY or YYYY-MM-DD.")


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
        click.echo(f"There was a {response.status_code} error when getting the data from the Wordle API")
        click.echo(response.json(), err=True)
        raise click.Abort()

    # Return the JSON response data as a dictionary
    return response.json()


@click.command()
@click.argument("date_input", required=False)
@click.option("-w", "--write", is_flag=True, help="Write the Wordle solution to a file.")
@click.pass_context
def main(ctx, date_input: Optional[str], write: bool):
    """
    Fetch and print the Wordle solution for a given date (or today if no date is provided).
    Accepts date formats DD-MM-YYYY or YYYY-MM-DD.
    """

    # ⬇️ Print the help message before continuing
    click.echo(ctx.get_help())
    click.echo()  # Add spacing

    load_dotenv()
    NTFY_URL = os.getenv("NTFY_URL")

    iso_date = parse_date(date_input)
    wordle = get_wordle_data(iso_date)

    # Parse and format the date for display
    parsed_date: datetime = datetime.strptime(iso_date, "%Y-%m-%d")
    formatted_date: str = parsed_date.strftime("%d %B %Y")

    # Construct the solution text
    solution_text = f"Wordle Solution ({formatted_date}): {wordle['solution']}"

    # Print the solution text
    click.echo(solution_text)

    if NTFY_URL:
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
    if write:
        filename: str = f"solutions/Wordle_Solution_{iso_date}.txt"

        os.makedirs("solutions", exist_ok=True)

        # Write the solution to a text file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(solution_text)
            click.echo(f"Solution saved to {filename}")


if __name__ == "__main__":
    main()
