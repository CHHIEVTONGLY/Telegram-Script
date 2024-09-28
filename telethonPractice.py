from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from colorama import Fore, Back, Style, init
import csv
import time
import os
import json

# Define the session file name
session_file = 'sessionkey'
credentials_file = 'credentials.json'

# Initialize colorama with autoreset=True
init(autoreset=True)

# Check if the credentials file exists
if not os.path.exists(credentials_file):
    # Ask the user for API credentials only if the credentials file doesn't exist
    api_id = int(input("Enter your API ID: "))  # Input for API ID
    api_hash = input("Enter your API Hash: ")   # Input for API Hash

    # Save the API credentials to a file for future use
    with open(credentials_file, 'w') as f:
        json.dump({"api_id": api_id, "api_hash": api_hash}, f)
else:
    # Load the saved API credentials from the file
    with open(credentials_file, 'r') as f:
        credentials = json.load(f)
        api_id = credentials['api_id']
        api_hash = credentials['api_hash']

# Create or load the client session using the session file and the credentials
client = TelegramClient(session_file, api_id, api_hash)
chats = []
last_date = None
chunk_size = 200
groups = []
groupid = []

async def getChat():
    for chat in chats:
        try:
            if chat.megagroup is True:
                groups.append(chat)
        except:
            continue

    print('Printing the group:')
    i = 0
    for group in groups:
        print(f"{i} - {group.title} | ID - {group.id}")
        groupid.append(group.id)
        i += 1

async def forward_message_to_group(group_id, from_chat_id, message_id):
    # Forward the message from Saved Messages to the group
    try:
        await client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
        print(f"Message {message_id} forwarded to group {group_id}")
    except Exception as e:
        print(f"Failed to forward message to group {group_id}: {str(e)}")

async def forward_message_to_all_groups():
    
    # Get the "Saved Messages" chat entity
    saved_messages = await client.get_entity('me')
    print(f"Saved Messages Chat ID: {saved_messages.id}")

    # Fetch the last message from Saved Messages
    messages = await client.get_messages(saved_messages, limit=1)
    if messages:
        message_id_to_forward = messages[0].id
        print(f"Message to forward: {messages[0].text}, ID: {message_id_to_forward}")

        # Forward the last message from Saved Messages to all groups
        for group in groupid:
            await forward_message_to_group(group, saved_messages.id, message_id_to_forward)
            time.sleep(5)  # Sleep for 5 seconds to avoid being rate-limited
    else:
        print("No messages found in Saved Messages.")

# Updated log_out function to disconnect the client and then delete files
async def clearkey():
    if os.path.exists(credentials_file):
        os.remove(credentials_file)
        print(f"{credentials_file} has been deleted.")
    else:
        print("Session file not found. Please login again.")

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



async def main():
    await client.start()  # Ensure client is started

    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)
    

    print("\t\t LCT TELEGRAM SERVICE")
    print("---------------------------------------------------")
    while True:
        me = await client.get_me()
        print(Fore.GREEN +  f"\nAccount name : {me.first_name} {me.last_name if me.last_name else ''}")
        print("\n1.Get chat list \n2.Forward messages to all groups\n3.Scrape members\n4.Clear API KEYs (optional if you enter wrong key on first input)\n---------------------------------------------------")
        option = input("Enter number to choose an option : ")

        if option == '1':
            await getChat()
        elif option == '2':
            # The first messages from your saved messages file will be forwarded into all groups
            await getChat()
            await forward_message_to_all_groups()
        elif option == '3':
            await scrape_members()
            break
        elif option == '4':
            await clearkey()  # Ensure to await the log_out function
            break
        else:
            break

# Run the main function
with client:
    client.loop.run_until_complete(main())
