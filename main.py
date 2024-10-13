from colorama import Fore , Style , Back
from TelegramBot import TelegramBot
from misc import print_intro, get_api_credentials, print_info
from typing import List, Tuple
import os


from master_function import (
    print_all_bots_info,
    print_all_bots_chat,
    all_bots_forward,
    all_bots_add_members,
    all_bots_scrape_members,
    all_bots_log_out,
    clean_members,
    exit_program,
    all_bots_join_group,
    all_bots_check_spam
)

from other_function import delete_first_100_rows

from license_validation import (
    load_public_key , 
    verify_license_data,
    is_license_expired,
    store_license_key,
    load_license_from_file,
)


def create_telegram_bots(credentials_file="credentials.csv") -> List[Tuple[int, TelegramBot]]:
    credentials_list = get_api_credentials(credentials_file)
    bots = []

    for i, credentials in enumerate(credentials_list):
        api_id = int(credentials["api_id"])
        api_hash = credentials["api_hash"]
        session_key = credentials["session_key"]
        bot = TelegramBot(api_id, api_hash, session_key)
        
        bots.append([i + 1, bot])
        print(f"{Fore.CYAN}Connecting into bot :{i+1}, Session : {str(session_key)}{Style.RESET_ALL}")

    print("\n-----------------------------------")
    return bots


async def main():
    # Load stored license if it exists
    stored_license_key, stored_expiration_date, stored_signature = load_license_from_file()                

    if stored_license_key:
        public_key = load_public_key()
        if is_license_expired(stored_expiration_date):
            print(f"{Fore.RED}License expired on {stored_expiration_date}!{Style.RESET_ALL}")
            os.remove("license.csv")
            return
        elif verify_license_data(stored_license_key, stored_expiration_date, stored_signature, public_key):
            print(f"{Fore.GREEN}Stored license key validated!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Stored license key is invalid! Please try again...{Style.RESET_ALL}")
            os.remove("license.csv")
            return
    else:
        license_key = input("Enter your username: ")
        expiration_date = input("Enter your license expiration date (YYYY-MM-DD): ")
        signature = input("Enter your license signature: ")

        public_key = load_public_key()
        if is_license_expired(expiration_date):
            print(f"{Fore.RED}The provided license has already expired on {expiration_date}!{Style.RESET_ALL}")
            os.remove("license.csv")
            return
        elif not verify_license_data(license_key, expiration_date, signature, public_key):
            print(f"{Fore.RED}Invalid license key! Please try again...{Style.RESET_ALL}")
            os.remove("license.csv")
            return  # Exit the program if the license is invalid

        print(f"{Fore.GREEN}License key validated!{Style.RESET_ALL}")
        # Store the validated license key
        store_license_key(license_key, expiration_date, signature)

    print_intro()
    
    bots = create_telegram_bots()

    for i, bot in bots:
        print(f"{Fore.GREEN}Sucessfully login into bot :{i} {Style.RESET_ALL}")
        await bot.start()


    OPTIONS = {
        '1': lambda: print_all_bots_info(bots),
        '2': lambda: print_all_bots_chat(bots),
        '3': lambda: all_bots_forward(bots),
        '4': lambda: all_bots_add_members(bots, members_file="members.csv"),
        '5': lambda: all_bots_scrape_members(bots),
        '6': lambda : all_bots_join_group(bots),
        '7': lambda : all_bots_check_spam(bots),
        '8': clean_members,
        '9': lambda: delete_first_100_rows("members.csv"),
        '10': lambda: all_bots_log_out(bots),
        '11' : exit_program
    }

    while True:
        print_info()

        option = input("Enter number to choose an option: ")
        action = OPTIONS.get(option)
        if action:
            await action()
        else:
            print('Invalid option, please try again.')

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())