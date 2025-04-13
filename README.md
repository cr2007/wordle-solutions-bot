# Wordle Solutions Bot

A simple Python program that gets the Wordle solutions from the Wordle API.

# Requirements

To run this program, make sure to have and [uv](https://docs.astral.sh/uv/) installed on your machine.

# Usage

```bash
uv run main.py # Gets today's Wordle solution
```

If you want to get a solution from a particular date, you can pass the date as an argument:

```bash
uv run main.py 01-01-2022 # Gets the solution for January 1st, 2022

uv run main.py 2022-03-01 # Gets the solution for March 1st, 2022
```

If you want to write the solution to a file, you can pass the `-w` argument to save the solutions:

```bash
uv run main.py -w # Saves today's solution to a file

uv run main.py 01-01-2022 -w # Saves the solution for January 1st, 2022 to a file

uv run main.py -w 2022-03-01 # Saves the solution for March 1st, 2022 to a file
```
