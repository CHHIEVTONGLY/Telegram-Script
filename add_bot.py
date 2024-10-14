import csv
from colorama import Fore , Style , Back
from TelegramBot import TelegramBot
from misc import print_intro, get_api_credentials, print_info
import os

async def add_bot():
    if os.path.exists("credentials.csv"):
        with open("credentials.csv", mode='a', newline='') as file:
            fieldnames = ["api_id", "api_hash", "session_key"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Check if the file is empty to write headers
            file_exists = os.path.getsize("credentials.csv") > 0
            if not file_exists:
                writer.writeheader()

            try:
                num_bots = int(input("How many bots do you want to add :  "))
            except ValueError:
                print("Invalid number. Please enter a valid integer.")
                return

            for _ in range(num_bots):
                api_id = input("Enter API ID: ")
                api_hash = input("Enter API Hash: ")
                session_key = input("Enter session key: ")

                # Write the bot details
                writer.writerow({"api_id": api_id, "api_hash": api_hash, "session_key": session_key})
                print(f"Bot with API ID {api_id} added successfully.")

    else:
        print("File credentials.csv not found!")

def remove_faulty_row(file_path: str, row_to_remove: dict):
    """Remove a row from the CSV file by comparing key values."""
    rows = []
    # Read all rows into a list
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Compare each row's fields explicitly
            if not (
                row["api_id"].strip() == row_to_remove["api_id"].strip() and
                row["api_hash"].strip() == row_to_remove["api_hash"].strip() and
                row["session_key"].strip() == row_to_remove["session_key"].strip()
            ):
                rows.append(row)

    # Overwrite the file with valid rows only
    with open(file_path, mode='w', newline='') as file:
        fieldnames = ["api_id", "api_hash", "session_key"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


