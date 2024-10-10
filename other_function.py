import os
import csv
from colorama import Fore, Back, Style, init
import pandas as pd
from telethon import TelegramClient
from misc import count_rows_in_csv

init(autoreset=True)


def get_api_credentials(credentials_file="tg_script_account.csv"):
    num_iter = 0
    num_accounts = int(input(f"How many accounts do you want to store {Fore.GREEN}( if you already have account press 0 ): {Style.RESET_ALL}"))
    
    # Check if file exists, if not create it with headers
    if not os.path.exists(credentials_file):
        with open(credentials_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["api_id", "api_hash", "session_key"])
            writer.writeheader()

    # Store the new accounts
    while num_iter < num_accounts:
        api_id = int(input(f"Enter API ID for account {num_iter + 1}: "))
        api_hash = input(f"Enter API Hash for account {num_iter + 1}: ")
        session_key = f"session_key_{num_iter + 1}.session"
        
        # Log in the account
        client = TelegramClient(session_key, api_id, api_hash)
        client.start()  # This will prompt for the code and complete the login
        print(f"Successfully logged in account {num_iter + 1}")

        # Store the credentials in the CSV file
        with open(credentials_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["api_id", "api_hash", "session_key"])
            writer.writerow({"api_id": api_id, "api_hash": api_hash, "session_key": session_key})
        
        num_iter += 1

    # Read and return the entire list of credentials from the CSV
    credentials_list = []
    with open(credentials_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials_list.append(row)

    return credentials_list  # format: [{'api_id': id, 'api_hash': hash, 'session_key': key}]

def create_telegram_clients(credentials_file="tg_script_account.csv"):
    credentials_list = get_api_credentials(credentials_file)
    clients = []

    for credentials in credentials_list:
        api_id = int(credentials["api_id"])
        api_hash = credentials["api_hash"]
        session_key = credentials["session_key"]
        client = TelegramClient(session_key, api_id, api_hash)
        clients.append(client)

    return clients

def read_csv_file(csv_file):
    user_acc = []
    
    try:
        with open(csv_file, 'r', newline='', encoding='UTF-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "session_key" in row:  # Check if the key exists
                    user_acc.append(row["session_key"])
                else:
                    print("Warning: 'session_key' not found in the row.")
    
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return user_acc

def delete_first_100_rows(csv_file):
    try:
        count_rows_in_csv('members.csv')
        row_delete = int(input("How many rows u want to delete : "))
        # Read all rows from the CSV file
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = list(csv.reader(file))


            # Ensure there are rows to delete after the header
            if len(reader) > 101:  # 1 for the header, 100 for the rows to remove
                header = reader[0]  # Keep the header intact
                rows_to_keep = reader[row_delete:]  # Keep rows starting from the 102nd row
            else:
                print(f"[!] File has fewer than 101 rows (including the header). Cannot remove 100 rows.")
                return

        # Write the header and remaining rows back into the same CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write the header
            writer.writerows(rows_to_keep)  # Write remaining rows

        print(f"[+] Successfully deleted the first 100 data rows (keeping the header) from {csv_file}")
        return

    except FileNotFoundError:
        print(f"[!] File {csv_file} not found.")
    except Exception as e:
        print(f"[!] An error occurred: {str(e)}")

def print_intro():

    title = r"""

        
 _____ _____ _     _____ ____ ____      _    __  __   _____ ___   ___  _     
|_   _| ____| |   | ____/ ___|  _ \    / \  |  \/  | |_   _/ _ \ / _ \| |    
  | | |  _| | |   |  _|| |  _| |_) |  / _ \ | |\/| |   | || | | | | | | |    
  | | | |___| |___| |__| |_| |  _ <  / ___ \| |  | |   | || |_| | |_| | |___ 
  |_| |_____|_____|_____\____|_| \_\/_/   \_\_|  |_|   |_| \___/ \___/|_____|


"""
    print(f""" {Fore.LIGHTBLUE_EX}{title}{Style.RESET_ALL}""")


def print_info(me):
    
    user_info = f"Account name : {me.first_name} {me.last_name if me.last_name else ''}"
    print(f"""
        ---------------------------------------------------
        {Fore.GREEN + user_info + Style.RESET_ALL}
          
        1.Get chat list
        {Fore.GREEN}2.Forward your Last Saved messages to all groups
        3.Add members to a group
        4.Scrape only active users
        5.Clear API KEYs (optional if you enter wrong key on first input)
        6.Swtich account
        {Fore.RED}7.Exit the program.{Style.RESET_ALL}   

        ---------------------------------------------------
        """)
