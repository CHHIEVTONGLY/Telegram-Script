import os
import csv
from colorama import Fore, Back, Style, init
import pandas as pd


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


def read_csv_file(input_file): # also in misc
    """
    Read member from CSV with this format username,id,access_hash,name
    """

    users = []
    with open(input_file, mode="r", encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Skip header
        for row in rows:
            user = {
                'username': row[0],
                'user_id': int(row[1]),
                'name': row[2]
            }
            users.append(user)
    return users


def write_members_to_csv(members, target_group_title, target_group_id, filename="members.csv"):
    """Write members to a CSV file."""
    with open(filename, "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user_id', 'name', 'group', 'group_id'])

        for member in members:
            writer.writerow([member['username'], member['user_id'], member['name'], target_group_title, target_group_id])

# def write_members_to_csv(members, target_group_title, target_group_id, filename="members.csv", mode='a'):
#     """Write members to a CSV file."""
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode=mode, encoding='UTF-8') as f:
#         writer = csv.writer(f, delimiter=",", lineterminator="\n")
        
#         if not file_exists:
#             writer.writerow(['username', 'user_id', 'access_hash', 'name', 'group', 'group_id'])
        
#         for member in members:
#             writer.writerow([member['username'], member['user_id'], member['access_hash'], member['name'], target_group_title, target_group_id])


def eval_input(prompt: str, lower_limit: int, upper_limit: int, default: int) -> int:

    try:
        the_input = int(input(prompt))
        if the_input > upper_limit or the_input < lower_limit:
            the_input = default
    except:
        the_input = default

    return the_input


def print_intro():

    title = r"""

        
 _____ _____ _     _____ ____ ____      _    __  __   _____ ___   ___  _     
|_   _| ____| |   | ____/ ___|  _ \    / \  |  \/  | |_   _/ _ \ / _ \| |    
  | | |  _| | |   |  _|| |  _| |_) |  / _ \ | |\/| |   | || | | | | | | |    
  | | | |___| |___| |__| |_| |  _ <  / ___ \| |  | |   | || |_| | |_| | |___ 
  |_| |_____|_____|_____\____|_| \_\/_/   \_\_|  |_|   |_| \___/ \___/|_____| by LCT


"""
    print(f""" {Fore.LIGHTBLUE_EX}{title}{Style.RESET_ALL}""")


from colorama import Fore, Style

def print_info():
    print(f"""
          
        {Fore.RED}[+] Beware all of these functions are not 100% safe for your bot accounts it's depend on accounts quality
        {Fore.YELLOW}[+] Because of telegram caughtion , it's depend on your bot account is old or new account
        {Fore.CYAN}[+] We recommend using old accounts telegram , or premium bot accounts 
        {Fore.MAGENTA}[+] Use accounts as your primary location - {Fore.RED}Ex : If you live in USA use +1 account telegram 
        {Fore.GREEN}[+] Use this script at your own risk {Style.RESET_ALL}
        ---------------------------------------------------
        
        Options:
        0. Customer Service {Fore.YELLOW}(If have any problems send message via my telegram){Style.RESET_ALL}
        1. Add more bot
        2. Print all bots info
        3. Print all bots chat
        4. Forward message to all groups{Fore.GREEN} (SAFE 100% for OLD ACCOUNT) {Style.RESET_ALL}
        5. Forward message to all groups + Auto reply to when user DM
        6. Add members to group{Fore.GREEN} ( Scrape members first before using this function ) {Style.RESET_ALL}
        7. Scrape members 
        8. Join gp via link
        9. Check bot is restricted sending messages
        10. Clean members.csv
        11. Delete 100 row members
        12. Log out all bots
        {Fore.RED}13. Exit the program.{Style.RESET_ALL}   
          
        {Fore.GREEN}{Style.BRIGHT}-------------------- ADVANCED FUNCTION -------------------- {Style.RESET_ALL}

        {Fore.CYAN}14. Bot account adjustments {Style.RESET_ALL}
        {Fore.BLUE}15. Bot account forwards messages into saved messages {Style.RESET_ALL}
        {Fore.RED}16. Clear all saved messages from all bots {Style.RESET_ALL}

        ---------------------------------------------------

        """)


def remove_duplicates(input_file, output_file):
    unique_rows = set()
    header = None
    with open(input_file, 'r', encoding='utf-8') as infile:
        header = infile.readline()  # Read the header
        for line in infile:
            if line not in unique_rows:
                unique_rows.add(line)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(header)
        for row in unique_rows:
            outfile.write(row)
        
def count_rows_in_csv(filename):
    try:
        df = pd.read_csv(filename)
        row_count = len(df)  # Get the number of rows
        print(f"{Fore.LIGHTMAGENTA_EX}Total members in {filename}: {row_count}")
        return row_count
    except FileNotFoundError:
        print(f"[!] File {filename} not found.")
    except Exception as e:
        print(f"[!] Error reading CSV file: {str(e)}")


def exit_the_program():
    print("Exiting the program...")
    exit()
