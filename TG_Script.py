from datetime import datetime
import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, User , UserStatusOffline
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import LeaveChannelRequest
import random
import traceback
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import InputPeerUser, InputPeerChannel
from colorama import Fore, Back, Style, init
import csv
import time
from other_function import get_api_credentials, print_intro, print_info , read_csv_file
import os, sys


# initalization
init(autoreset=True)

credentials_file = 'tg_script_account.csv'

credentials_list = get_api_credentials(credentials_file)

for credentials in credentials_list:
    api_id = credentials["api_id"]
    api_hash = credentials["api_hash"]
    
session_file = read_csv_file(credentials_file)

index_acc = 1

session_file = "session_key_" + str(index_acc) + ".session"

# Correct the condition to check if the file exists
if os.path.exists(session_file):
    client = TelegramClient(session_file, api_id, api_hash)
else:
    print(f"Session file '{session_file}' does not exist.")

session_list = read_csv_file(credentials_file)

chats = []
last_date = None
chunk_size = 200
groups = []
groupid = []

async def increment_and_switch_account():
    global index_acc, client, session_file, api_id, api_hash

    # Disconnect from the current client if it exists
    await client.disconnect()

    # Increment the account index
    index_acc += 1

    # Generate the new session file name
    session_file = f"session_key_{index_acc}.session"

    # Check if the new session file exists
    if os.path.exists(session_file):
        print(f"Session file '{session_file}' found. Switching to account {index_acc}.")

        # Create a new client instance with the new session
        client = TelegramClient(session_file, api_id, api_hash)

        # Start the new client session
        await client.start()
        print(f"Switched to account with session: {session_file}")

        # Fetch the new account info and update `me`
        me = await client.get_me()  # Ensure that the `me` object is updated
        print(f"Switched to account: {me.first_name} {me.last_name} (ID: {me.id})")

        return  
    else:
        # If no session file exists, print an error and stop
        print(f"Session file '{session_file}' does not exist. Cannot switch accounts.")
        return False  # Indicate that switching was unsuccessful


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
    """Forward the message from Saved Messages to the group and leave if it fails."""
    try:
        await client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
        print(f"Message ID {message_id} forwarded to group with ID {group_id}")
    except Exception as e:
        print(f"Failed to forward message to group {group_id}: {str(e)}")
        # Automatically leave the group on failure
        try:
            await client(LeaveChannelRequest(group_id))
            print(f"[+] Left the group with ID {group_id} due to forwarding failure.")
        except Exception as leave_error:
            print(f"[!] Failed to leave the group {group_id}: {str(leave_error)}")


async def forward_message_to_all_groups(limit=1):
    """
    Forward Message from Saved Messages to all Megagroup.

    Limit initially set to 1. Meaning the last saved message.

    Change it to n to Forward n last Saved Message. 
    
    """

    # Get the "Saved Messages" chat entity
    saved_messages = await client.get_entity('me')
    print(f"Saved Messages Chat ID: {saved_messages.id}") 

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
        while True :
            for group in groupid:
                await forward_message_to_group(group, saved_messages.id, message_id_to_forward) # type: ignore
                time.sleep(5)  # Sleep for 5 seconds to avoid being rate-limited
            print("[+] Finished forwarding messages to all groups. Waiting for 20-30 minutes...")
            print(f"[+] Waiting for 20-30 minutes {Fore.RED} (if you want to exit press ctrl+c to exit){Style.RESET_ALL}")
            time.sleep(random.uniform(1200, 1800))
            
    else:
        print("No messages found in Saved Messages.")
    
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
        print("[+] Logging out and removing session...")
        await client.log_out()  
        await client.disconnect()
        
        #remove the session file
        session_file = 'sessionkey.session'
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"[+] Successfully removed {session_file}.")
            sys.exit()


        print(f"You are now Logged out and {credentials_file} and has been deleted.")
    else:
        print("Session file not found. Please login again.")
    return True


async def forward_messages():
    await get_chat()
    await forward_message_to_all_groups()


# Function to get the megagroups from chats
def get_megagroups(chats):
    groups = []
    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue
    return groups


# Function to display groups and let user choose one
def choose_group(groups):
    print( Fore.GREEN + "[+] Available groups:" + Style.RESET_ALL)
    for i, group in enumerate(groups):
        print(f"[{i}] - {group.title}")
    
    g_index = input("\n[+] Choose a group to add members: ")
    return groups[int(g_index)]


# Function to write remaining users back to CSV
def write_remaining_users_to_csv(remaining_users, input_file):
    with open(input_file, mode='w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(['username', 'id', 'access_hash', 'name'])
        for user in remaining_users:
            writer.writerow([user['username'], user['id'], user['access_hash'], user['name']])
    print("[+] Remaining users saved back to CSV file.")


def write_remaining_users_to_csv(remaining_users, input_file):
    with open(input_file, mode='w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        # Writing the header first into a CSV file
        writer.writerow(['username', 'id', 'access_hash', 'name'])
        for user in remaining_users:
            writer.writerow([user['username'], user['id'], user['access_hash'], user['name']])
    print("[+] Remaining users saved back to CSV file.")


def read_csv_file():
    users = []

    # Open the CSV file correctly
    with open("members.csv", mode="r", encoding='UTF-8') as input_file:
        rows = csv.reader(input_file, delimiter=",", lineterminator="\n")
        next(rows, None)  # Skip header

        for row in rows:
            # Create a dictionary for each user and append to the list
            user = {
                'username': row[0],
                'id': int(row[1]),
                'access_hash': int(row[2]),
                'name': row[3]
            }
            users.append(user)
    
    return users


# Add users to group
async def add_users_to_group(client, target_group_entity, users, input_file):
    print("1.Adding users by timestamp to group\n2.Adding users by set limit to group")
    mode = int(input("Choose an option: "))

    if mode == 2:
        max_users = int(input("Enter the maximum number of users to add: "))

    users_added = 0

    for user in users[:]:  # iterating over a copy of the list so we can modify it
        try:

            if mode == 2 and users_added >= max_users:
                print(f"[+] Reached the limit of {max_users} users. Stopping.")
                break

            user_to_add = InputPeerUser(user['id'], user['access_hash'])
            print(f"[+] Adding user : {user['name']} + ' - ID : ' {user['id']}")

            # Add the user to the group
            await client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print("[+] User successfully added. Removing user from list.")
            
            # Remove user from the list after successfully adding
            users.remove(user)

            users_added += 1

            # Wait between 10 to 30 seconds to avoid getting rate-limited
            print("[+] Waiting for 10-30 seconds before adding the next user...")
            time.sleep(random.uniform(10, 30))

        except PeerFloodError:
            print("[!] Flood error from Telegram. Saving remaining users back to CSV and stopping the script.")
            write_remaining_users_to_csv(users, input_file)
            break  # Stop adding more users to prevent more flood errors

        except UserPrivacyRestrictedError:
            print("[!] The user's privacy settings prevent this action. Skipping to the next user.")
            users.remove(user)  # Remove from the list even if we skip due to privacy settings

        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            traceback.print_exc()
            continue  # Continue to the next user in case of any other exception

    # If there are still users left, save them back to the CSV
    if users:
        write_remaining_users_to_csv(users, input_file)


# Add members to group
async def add_members_to_group(client, chats, input_file):
    # Get megagroups from the chats
    groups = get_megagroups(chats)

    if not groups:
        print("[!] No megagroups found.")
        return

    # Let user select the group
    target_group = choose_group(groups)
    target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

    # Read the CSV file to get the list of users
    users = read_csv_file()

    # Add users to the group
    await add_users_to_group(client, target_group_entity, users, input_file)

def exit_the_program():
    print("Exiting the program...")
    sys.exit()

async def main():

    OPTIONS = {
    '1': get_chat,
    '2': forward_messages,
    '3': lambda: add_members_to_group(client, chats, "members.csv"),
    '4': scrape_members,
    '5': clear_key,
    '6': exit_the_program,
    "7": increment_and_switch_account
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
        sys.exit()

    while True:
        print_info(me)  # Update the user info in the menu

        option = input("Enter number to choose an option: ")
        action = OPTIONS.get(option)
        if action:
            should_break = await action()

            # After switching accounts, refetch and update user info
            if option == "7":  # If account switching was triggered
                me = await client.get_me()  # Fetch new account info after switching
                print_info(me)  # Update UI with the new account details

            if should_break:
                break
        else:
            print('Invalid option, please try again.')
# Run the main function
with client:
    client.loop.run_until_complete(main())
