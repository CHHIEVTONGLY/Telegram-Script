from TelegramBot import TelegramBot
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, User
from misc import print_info, print_intro, exit_the_program
import sys


async def main():
    bot = TelegramBot()

    OPTIONS = {
        '1': bot.print_chat,
        '2': bot.forward_message_to_all_groups,
        '3': lambda: bot.add_members_to_group("members.csv"),
        '4': bot.scrape_members,
        '5': bot.log_out,
        '6': exit_the_program,
    }
    print_intro()

    await bot.client.start()  # type: ignore

    result = await bot.client(GetDialogsRequest(
        offset_date=bot.last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=bot.chunk_size,
        hash=0
    ))
    bot.chats.extend(result.chats)  # type: ignore

    me = await bot.client.get_me()

    if not isinstance(me, User):
        print("Unexpected error please try again!")
        sys.exit()

    while True:
        print_info(me)
        option = input("Enter number to choose an option : ")
        action = OPTIONS.get(option)
        if action:
            should_break = await action()
            if should_break:
                break
        else:
            print('Invalid option, please try again.')

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())