from colorama import Fore , Style , Back
from TelegramBot import TelegramBot
from misc import print_intro, get_api_credentials, print_info
from typing import List, Tuple


from master_function import (
    print_bot_info,
    print_all_bots_info,
    print_bot_chat,
    print_all_bots_chat,
    all_bots_forward,
    all_bots_add_members,
    all_bots_scrape_members,
    all_bots_log_out,
    clean_members,
    exit_program,
    all_bots_join_group,
)

from other_function import delete_first_100_rows


def create_telegram_bots(credentials_file="credentials.csv") -> List[Tuple[int, TelegramBot]]:
    credentials_list = get_api_credentials(credentials_file)
    bots = []

    for i, credentials in enumerate(credentials_list):
        api_id = int(credentials["api_id"])
        api_hash = credentials["api_hash"]
        session_key = credentials["session_key"]
        bot = TelegramBot(api_id, api_hash, session_key)
        
        bots.append([i + 1, bot])
        print(f"{Fore.CYAN}Connecting into bot :{i+1} {Style.RESET_ALL}")

    print("\n-----------------------------------")
    return bots


async def main():
    print_intro()
    
    bots = create_telegram_bots()

    for i, bot in bots:
        print(f"{Fore.GREEN}Sucessfully login into bot :{i} {Style.RESET_ALL}")
        await bot.start()

    # Start all bots concurrently
    # await asyncio.gather(*(bot.start() for bot in bots))

    OPTIONS = {
        '1': lambda: print_all_bots_info(bots),
        '2': lambda: print_all_bots_chat(bots),
        '3': lambda: all_bots_forward(bots),
        '4': lambda: all_bots_add_members(bots, members_file="members.csv"),
        '5': lambda: all_bots_scrape_members(bots),
        '6': lambda : all_bots_join_group(bots),
        '7': lambda: all_bots_log_out(bots),
        '8': clean_members,
        '9': lambda: delete_first_100_rows("members.csv"),
        '10': exit_program,
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