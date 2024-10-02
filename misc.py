import os
import csv
from colorama import Fore, Back, Style, init


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
                'access_hash': int(row[2]),
                'name': row[3]
            }
            users.append(user)
    return users


# def write_members_to_csv(members, target_group_title, target_group_id, filename="members.csv"):
#     """Write members to a CSV file."""
#     with open(filename, "w", encoding='UTF-8') as f:
#         writer = csv.writer(f, delimiter=",", lineterminator="\n")
#         writer.writerow(['username', 'user_id', 'access_hash', 'name', 'group', 'group_id'])

#         for member in members:
#             writer.writerow([member['username'], member['user_id'], member['access_hash'], member['name'], target_group_title, target_group_id])

def write_members_to_csv(members, target_group_title, target_group_id, filename="members.csv", mode='a'):
    """Write members to a CSV file."""
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode=mode, encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        
        if not file_exists:
            writer.writerow(['username', 'user_id', 'access_hash', 'name', 'group', 'group_id'])
        
        for member in members:
            writer.writerow([member['username'], member['user_id'], member['access_hash'], member['name'], target_group_title, target_group_id])


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
  |_| |_____|_____|_____\____|_| \_\/_/   \_\_|  |_|   |_| \___/ \___/|_____|


"""
    print(f""" {Fore.LIGHTBLUE_EX}{title}{Style.RESET_ALL}""")


from colorama import Fore, Style

def print_info():
    print(f"""
        ---------------------------------------------------
        
        Options:
        1. Print all bots info
        2. Print all bots chat
        3. Forward message to all groups
        4. Add members to group
        5. Scrape members
        6. Log out all bots
        {Fore.RED}7. Exit the program.{Style.RESET_ALL}   
          
        ---------------------------------------------------
        """)

def exit_the_program():
    print("Exiting the program...")
    exit()
