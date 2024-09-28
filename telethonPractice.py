from datetime import datetime
import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, User , UserStatusOffline
from colorama import Fore, Back, Style, init
import csv
import time
from other_function import get_api_credentials, print_intro, print_info
import os


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
    
    print()
    return


# Scrap members and save into csv file
async def scrape_members():
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
        
        # Define the timezone
        utc = pytz.utc

        start_of_today = datetime.now(utc)

        for user in all_participants:
             # Skip users who have deleted accounts
            if user.deleted:
                first_name = user.first_name if user.first_name else "Unknown"
                last_name = user.last_name if user.last_name else ""
                print(f"Skipping deleted user: {first_name} {last_name} (ID: {user.id})")  # Debugging line
                continue
            
            if isinstance(user.status, UserStatusOffline):
                if user.status.was_online.date() == start_of_today.date():

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
        print(f"You are now Logged out and {credentials_file} and has been deleted.")
    else:
        print("Session file not found. Please login again.")
    return True


async def forward_messages():
    await get_chat()
    await forward_message_to_all_groups()


async def main():

    OPTIONS = {
    '1': get_chat,
    '2': forward_messages,
    '3': clear_key,
    '4': scrape_members,
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
