from TelegramBot import TelegramBot
from misc import print_intro, get_api_credentials, print_info

from master_function import (
    print_bot_info,
    print_all_bots_info,
    print_bot_chat,
    print_all_bots_chat,
    all_bots_forward,
    all_bots_add_members,
    all_bots_scrape_members,
    all_bots_log_out,
    exit_program
)


def create_telegram_bots(credentials_file="credentials.csv"):
    credentials_list = get_api_credentials(credentials_file)
    bots = []

    for credentials in credentials_list:
        api_id = int(credentials["api_id"])
        api_hash = credentials["api_hash"]
        session_key = credentials["session_key"]
        bot = TelegramBot(api_id, api_hash, session_key)
        
        bots.append(bot)

    return bots


async def main():
    print_intro()
    
    bots = create_telegram_bots()

    for bot in bots:
        await bot.start()

    OPTIONS = {
        '1': lambda: print_all_bots_info(bots),
        '2': lambda: print_all_bots_chat(bots),
        '3': lambda: all_bots_forward(bots),
        '4': lambda: all_bots_add_members(bots, limit_per_bot=10, members_file="members.csv"),
        '5': lambda: all_bots_scrape_members(bots),
        '6': lambda: all_bots_log_out(bots),
        '7': exit_program,
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