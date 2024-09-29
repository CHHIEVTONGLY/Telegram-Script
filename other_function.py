import os
import json
from colorama import Fore, Back, Style, init


init(autoreset=True)


def get_api_credentials(credentials_file):
    if not os.path.exists(credentials_file):
        api_id = int(input("Enter your API ID: "))
        api_hash = input("Enter your API Hash: ")
        with open(credentials_file, 'w') as f:
            json.dump({"api_id": api_id, "api_hash": api_hash}, f)
    else:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)
            api_id = credentials['api_id']
            api_hash = credentials['api_hash']
    return api_id, api_hash


def print_intro():
    print(f""" {Fore.LIGHTBLUE_EX} 
        
 _____ _____ _     _____ ____ ____      _    __  __   _____ ___   ___  _     
|_   _| ____| |   | ____/ ___|  _ \    / \  |  \/  | |_   _/ _ \ / _ \| |    
  | | |  _| | |   |  _|| |  _| |_) |  / _ \ | |\/| |   | || | | | | | | |    
  | | | |___| |___| |__| |_| |  _ <  / ___ \| |  | |   | || |_| | |_| | |___ 
  |_| |_____|_____|_____\____|_| \_\/_/   \_\_|  |_|   |_| \___/ \___/|_____|

{Style.RESET_ALL}"""  )


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
