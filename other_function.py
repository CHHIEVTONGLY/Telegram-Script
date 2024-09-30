import os
import csv
from colorama import Fore, Back, Style, init
from telethon import TelegramClient

init(autoreset=True)


def get_api_credentials(credentials_file="credentials.csv"):
    if not os.path.exists(credentials_file):
        api_id = int(input("Enter your API ID: "))
        api_hash = input("Enter your API Hash: ")
        session_key = input("Enter your Session Key: ")
        
        with open(credentials_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["api_id", "api_hash", "session_key"])
            writer.writeheader()
            writer.writerow({"api_id": api_id, "api_hash": api_hash, "session_key": session_key})
        
        return [{"api_id": api_id, "api_hash": api_hash, "session_key": session_key}]
    else:
        credentials_list = []
        with open(credentials_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                credentials_list.append(row)
        
        return credentials_list # format: [{api_key:api,api_hash:hash,session_key:location}]


def create_telegram_clients(credentials_file="credentials.csv"):
    credentials_list = get_api_credentials(credentials_file)
    clients = []

    for credentials in credentials_list:
        api_id = int(credentials["api_id"])
        api_hash = credentials["api_hash"]
        session_key = credentials["session_key"]
        client = TelegramClient(session_key, api_id, api_hash)
        clients.append(client)

    return clients


def print_intro():
    print(f""" {Fore.LIGHTBLUE_EX} 
        
 _____ _____ _     _____ ____ ____      _    __  __   _____ ___   ___  _     
|_   _| ____| |   | ____/ ___|  _ \    / \  |  \/  | |_   _/ _ \ / _ \| |    
  | | |  _| | |   |  _|| |  _| |_) |  / _ \ | |\/| |   | || | | | | | | |    
  | | | |___| |___| |__| |_| |  _ <  / ___ \| |  | |   | || |_| | |_| | |___ 
  |_| |_____|_____|_____\____|_| \_\/_/   \_\_|  |_|   |_| \___/ \___/|_____|

{Style.RESET_ALL}""")


def print_info(me):
    
    user_info = f"Account name : {me.first_name} {me.last_name if me.last_name else ''}"
    print(f"""
        ---------------------------------------------------
        {Fore.GREEN + user_info + Style.RESET_ALL}
          
        1.Get chat list
        2.Forward your Last Saved messages to all groups
        3.Add members to a group
        4.Scrape only active users
        5.Clear API KEYs (optional if you enter wrong key on first input)
        {Fore.RED}6.Exit the program.{Style.RESET_ALL}   

        ---------------------------------------------------
        """)
