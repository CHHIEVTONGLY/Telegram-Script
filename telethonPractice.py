from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, User
from colorama import Fore, Back, Style, init
import csv
import time
from other_function import get_api_credentials,create_telegram_clients, print_intro, print_info
import os


# initalization
init(autoreset=True)

credentials_file = "credentials.csv"

clients = create_telegram_clients(credentials_file)
client = clients[0]
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
            print(f"{index + 1} - {chat.title} | ID - {chat.id}")
        print()
        return
    
    for chat in chats:
        if getattr(chat, 'megagroup', False):
            groups.append(chat)

            print(f"{len(groups)} - {chat.title} | ID - {chat.id}")
            groupid.append(chat.id)
    print()
    return


async def forward_message_to_group(group_id, from_chat_id, message_id):
    """Forward the message from Saved Messages to the group."""

    try:
        await client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
        print(f"Message ID {message_id} forwarded to group with ID {group_id}")
    except Exception as e:
        print(f"Failed to forward message to group {group_id}: {str(e)}")


def print_messages(messages):
    for message in messages:
        print(f"Message: {message.text}, Message ID: {message.id}")


async def forward_to_all(group_ids, chat_id, messages):
    for group_id in group_ids:
        for message in messages:
            await forward_message_to_group(group_id, chat_id, message.id)
            time.sleep(5)  # Sleep for 5 seconds to avoid being rate-limited


async def forward_message_to_all_groups():
    """
    Forward Message from Saved Messages to all Megagroup.

    Limit initially set to 1. Meaning the last saved message.

    Change it to n to Forward n last Saved Message. 
    
    """
    if not groups:
        await get_chat()

    # Get the "Saved Messages" chat entity
    saved_messages = await client.get_entity('me')
    print(f"Saved Messages Chat ID: {saved_messages.id}") # type: ignore no worry it is single entity

    try:
        limit = int(input("How many messages? (Default=1): "))
        if limit > 100:
            limit = 1
    except:
        limit = 1
    print(f"Send {limit} messages to each group.")
    
    # Fetch the last message from Saved Messages
    messages = await client.get_messages(saved_messages, limit=limit)
    if messages:
        if isinstance(messages, list):
            print_messages(messages)
        else:
            print(f"Message: {messages.message}, Message ID: {messages.id}")
            messages = [messages]

        await forward_to_all(group_ids=groupid, chat_id=saved_messages.id, messages=messages) # type: ignore
    else:
        print("No messages found in Saved Messages.")
    
    print()
    return


async def scrape_members():
    """Scrap members and save into csv file"""

    groups.clear()  # Make sure to clear the groups before populating again

    # Populate the list of groups
    for chat in chats:
        try:
            if chat.megagroup:  # Ensure chat is a mega group
                groups.append(chat)
        except Exception as e:
            print(f"Error: {str(e)}")
            continue

    # Check if there are groups available
    if not groups:
        print("No groups available to scrape members from.")
        return

    print('[+] Choose a group to scrape members from:')
    i = 0
    for g in groups:
        print(f'[{i}] - {g.title}')
        i += 1

    # Prompt the user to choose a group
    g_index = int(input("[+] Enter a number: "))
    if g_index < 0 or g_index >= len(groups):
        print("Invalid group number.")
        return

    target_group = groups[g_index]

    print(f'[+] Fetching members from group: {target_group.title}')
    time.sleep(1)

    try:
        # Use await for the asynchronous get_participants method
        all_participants = await client.get_participants(target_group, aggressive=True)
    except Exception as e:
        print(f"Failed to fetch members: {str(e)}")
        return

    print('[+] Saving members into file...')
    time.sleep(1)

    # Open CSV and save members with usernames
    with open("members.csv", "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
        
        for user in all_participants:
            # Use username if it exists, otherwise fallback to user ID
            username = user.username if user.username else f"user_{user.id}"

            # Collect user's first and last name
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            name = (first_name + ' ' + last_name).strip()

            # Write the user information to the CSV file
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

    print('[+] Members with usernames scraped successfully.')


async def clear_key():
    """Delete The Credential and Session."""

    if os.path.exists(credentials_file):
        os.remove(credentials_file)
        await client.log_out()
        print(f"You are now Logged Out and {credentials_file} and has been deleted.")
    else:
        print("Session file not found. Please login again.")
    return True


async def main():

    OPTIONS = {
    '1': get_chat,
    '2': forward_message_to_all_groups,
    '3': scrape_members,
    '4': clear_key,
    '5': exit
    }
    print_intro()

    await client.start() # type: ignore

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
