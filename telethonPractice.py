from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, User
from colorama import Fore, Back, Style, init
import time
import os
import json
from other_function import get_api_credentials, clear_key, print_intro, print_info



# initalization
init(autoreset=True)

session_file = 'sessionkey'
credentials_file = 'credentials.json'

api_id, api_hash = get_api_credentials(credentials_file)
client = TelegramClient(session_file, api_id, api_hash)

chats = []
last_date = None
chunk_size = 200
groups = []
groupid = []


async def get_chat():
    """Get list of all Megagroup in Chat list."""
    
    print('Printing the group:')

    if groups:
        for index, chat in enumerate(groups):
            print(f"{index} - {chat.title} | ID - {chat.id}")
        return
    
    for chat in chats:
        if getattr(chat, 'megagroup', False):
            groups.append(chat)

            print(f"{len(groups)} - {chat.title} | ID - {chat.id}")
            groupid.append(chat.id)


async def forward_message_to_group(group_id, from_chat_id, message_id):
    """Forward the message from Saved Messages to the group."""

    try:
        await client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
        print(f"Message {message_id} forwarded to group {group_id}")
    except Exception as e:
        print(f"Failed to forward message to group {group_id}: {str(e)}")


async def forward_message_to_all_groups(limit=1):
    """
    Forward Message from Saved Messages to all Megagroup.

    Limit initially set to 1. Meaning the last saved message.

    Change it to n to Forward n last Saved Message. 
    
    """

    # Get the "Saved Messages" chat entity
    saved_messages = await client.get_entity('me')
    print(f"Saved Messages Chat ID: {saved_messages.id}") # type: ignore no worry it is single entity

    # Fetch the last message from Saved Messages
    messages = await client.get_messages(saved_messages, limit=limit)
    if messages:
        if isinstance(messages, list):
            message_id_to_forward = messages[0].id
            message_text = messages[0].text
        else:
            message_id_to_forward = messages.id
            message_text = messages.message
        print(f"Message to forward: {message_text}, ID: {message_id_to_forward}")

        # Forward from Saved Messages to all groups
        for group in groupid:
            await forward_message_to_group(group, saved_messages.id, message_id_to_forward) # type: ignore
            time.sleep(5)  # Sleep for 5 seconds to avoid being rate-limited
    else:
        print("No messages found in Saved Messages.")


async def forward_messages():
    await get_chat()
    await forward_message_to_all_groups()


async def main():

    OPTIONS = {
    '1': get_chat,
    '2': forward_messages,
    '3': clear_key,
    '4': exit
    }
    print_intro()

    client.start()

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats) # type: ignore

    me = await client.get_me()

    if not isinstance(me, User):
        print("Unexpected error please try again!")
        exit()

    while True:

        print_info(me)
        await get_chat()

        option = input("Enter number to choose an option : ")
        action = OPTIONS.get(option)
        if action:
            should_break = await action()
            if should_break:
                break
        else:
            print('Invalid option, please try again.')


# Run the main function
with client:
    client.loop.run_until_complete(main())
