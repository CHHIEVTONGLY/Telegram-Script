from datetime import datetime
import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UserStatusOffline, InputPeerChannel, InputUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import LeaveChannelRequest, InviteToChannelRequest
from colorama import Fore, Style, init
import csv
import time
import random
import traceback


class TelegramBot:
    def __init__(self, api_id, api_hash, session_file):
        self.client = TelegramClient(session_file, api_id, api_hash)
        self.sleep_time = 5 
        self.chats = []
        self.last_date = None
        self.chunk_size = 200
        self.groups = []
        self.groups_id = []


    async def __get_chat(self):
        """Get list of all Megagroup in Chat list."""
        for chat in self.chats:
            if getattr(chat, 'megagroup', False):
                self.groups.append(chat)
                self.groups_id.append(chat.id)
        return
    

    async def print_chat(self):
        """Print the list of all Megagroup in Chat list."""
        # print('Printing the group:')
        if not self.groups:
            await self.__get_chat()
        if not self.groups:
            print("No groups found.")
        for index, chat in enumerate(self.groups):
            print(f"{index + 1} - {chat.title} | ID - {chat.id}")
        print()
        return


    async def __LeaveChannel(self, group_id):
        try:
            await self.client(LeaveChannelRequest(group_id))
            print(f"[+] Left the group with ID {group_id} due to forwarding failure.")
        except Exception as leave_error:
            print(f"[!] Failed to leave the group {group_id}: {str(leave_error)}")


    async def forward_message_to_group(self, group_id, from_chat_id, message_id):
        """Forward the message from Saved Messages to the group and leave if it fails."""
        try:
            await self.client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
            print(f"Message ID {message_id} forwarded to group with ID {group_id}")
        except Exception as e:
            print(f"Failed to forward message to group {group_id}: {str(e)}")
            await self.__LeaveChannel(group_id)


    async def forward_message_to_all_groups(self):
        """
        Forward Message from Saved Messages to all Megagroup.
    
        Limit initially set to 1. Meaning the last saved message.
    
        Change it to n to Forward n last Saved Message. 
        """
        if not self.groups:
            await self.__get_chat()

        # find out how many chat to forward
        try:
            limit = int(input("How many messages? (Default=1): "))
            if limit > 100:
                limit = 1
        except:
            limit = 1
        print(f"Send {limit} messages to each group.")
        
        # Get the "Saved Messages" chat and fetch messages
        saved_messages = await self.client.get_entity('me')
        if isinstance(saved_messages, list):
            saved_messages = saved_messages[0]
        print(f"Saved Messages Chat ID: {saved_messages.id}")
        messages = await self.client.get_messages(saved_messages, limit=limit)
    
        # print the message out and forward it
        if messages:
            if isinstance(messages, list):
                self.__print_messages(messages)
            else:
                print(f"Message: {messages.message}, Message ID: {messages.id}")
                messages = [messages]
            await self.__forward_to_all(group_ids=self.groups_id, chat_id=saved_messages.id, messages=messages)
        else:
            print("No messages found in Saved Messages.")
    
        print()
        return
    

    def __print_messages(self, messages):
        for message in messages:
            print(f"Message: {message.text}, Message ID: {message.id}")
    

    async def __forward_to_all(self, group_ids, chat_id, messages):
        for group_id in group_ids:
            for message in messages:
                await self.forward_message_to_group(group_id, chat_id, message.id)
                time.sleep(self.sleep_time)


    async def scrape_members(self):
        self.groups.clear()

        await self.__get_chat()
        
        if not self.groups:
            print("No groups available to scrape members from.")
            return

        print('[+] Choose a group to scrape members from:')
        await self.print_chat()

        # Prompt the user to choose a group
        g_index = eval(input("[+] Enter a number: "))
        
        if type(g_index) != int:
            print("Invalid Input! Exiting the program...")
            exit()

        if g_index <= 0 or g_index > len(self.groups):
            print("Invalid group number.")
            return

        target_group = self.groups[g_index - 1]

        print(f'[+] Fetching members from group: {target_group.title}')
        time.sleep(1)

        try:
            # Use await for the asynchronous get_participants method
            all_participants = await self.client.get_participants(target_group, aggressive=True)
        except Exception as e:
            print(f"Failed to fetch members: {str(e)}")
            return

        print('[+] Processing members...')
        time.sleep(1)

        members_to_write = []

        for user in all_participants:
            # Skip users who have deleted accounts
            if user.deleted:
                first_name = user.first_name if user.first_name else "Unknown"
                last_name = user.last_name if user.last_name else ""
                print(f"Skipping deleted user: {first_name} {last_name} (ID: {user.id})")  # Debugging line
                continue

            user_info = self.__get_user_info(user)
            if user_info:
                members_to_write.append(user_info)

        self.__write_members_to_csv(members_to_write, target_group.title, target_group.id)
        print('[+] Members with usernames scraped successfully.')

    def __get_user_info(self, user):
        """Get user information if the user was online today."""
        # Define the timezone
        utc = pytz.utc
        start_of_today = datetime.now(utc)

        if isinstance(user.status, UserStatusOffline) and user.status.was_online and user.status.was_online.date() == start_of_today.date():
            username = user.username if user.username else f"user_{user.id}"

            # Collect user's first and last name
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            name = (first_name + ' ' + last_name).strip()

            # Return the user information
            return {
                'username': username,
                'user_id': user.id,
                'access_hash': user.access_hash,
                'name': name
            }
        return None
    

    def __write_members_to_csv(self, members, target_group_title, target_group_id):
        """Write members to a CSV file."""
        with open("members.csv", "w", encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            writer.writerow(['username', 'user_id', 'access_hash', 'name', 'group', 'group_id'])

            for member in members:
                writer.writerow([member['username'], member['user_id'], member['access_hash'], member['name'], target_group_title, target_group_id])


    async def log_out(self):
        """Delete The Credential and Session."""

        print("[+] Logging out and removing session...")
        await self.client.log_out()  
        self.client.disconnect()
        print(f"You are now Logged out.")

        # Remove the session file
        # session_file = 'sessionkey.session'
        # if os.path.exists(session_file):
        #     os.remove(session_file)
        #     print(f"[+] Successfully removed {session_file}.")
        #     sys.exit()
        # else:
        #     print("Session file not found. Please login again.")
        return True


    def __choose_group(self, groups):
        print(Fore.GREEN + "[+] Available groups:" + Style.RESET_ALL)
        for i, group in enumerate(groups):
            print(f"[{i+1}] - {group.title}")
        
        g_index = input("\n[+] Choose a group to add members: ")
        return groups[int(g_index) - 1]


    def __read_csv_file(self, input_file="members.csv"):
        users = []
        with open(input_file, mode="r", encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)  # Skip header
            for row in rows:
                user = {
                    'username': row[0],
                    'id': int(row[1]),
                    'access_hash': int(row[2]),
                    'name': row[3]
                }
                users.append(user)
        return users


    async def add_users_to_group(self, target_group_entity, users, input_file):
        print("1.Adding users by timestamp to group")
        print("2.Adding users by set limit to group")
        
        mode = int(input("Choose an option: "))

        if mode == 2:
            max_users = int(input("Enter the maximum number of users to add: "))

        users_added = 0

        for user in users[:]:  # iterating over a copy of the list so we can modify it
            try:
                if mode == 2 and users_added >= max_users:
                    print(f"[+] Reached the limit of {max_users} users. Stopping.")
                    break
                
                user_to_add = InputUser(user['id'], user['access_hash'])
                print(f"[+] Adding user : {user['name']} + ' - ID : ' {user['id']}")

                # Add the user to the group
                await self.client(InviteToChannelRequest(target_group_entity, [user_to_add]))
                print("[+] User successfully added. Removing user from list.")
                
                # Remove user from the list after successfully adding
                users.remove(user)

                users_added += 1

                # Wait between 10 to 30 seconds to avoid getting rate-limited
                print("[+] Waiting for 10-30 seconds before adding the next user...")
                time.sleep(random.uniform(10, 30))

            except PeerFloodError:
                print("[!] Flood error from Telegram. Saving remaining users back to CSV and stopping the script.")
                self.__write_members_to_csv(users, "Remaining Users", target_group_entity.id)
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
            self.__write_members_to_csv(users, "Remaining Users", target_group_entity.id)


    async def add_members_to_group(self, input_file):
        # Get megagroups from the chats
        
        if not self.groups:
            await self.__get_chat()

        if not self.groups:
            print("[!] No megagroups found.")
            return

        # Let user select the group
        target_group = self.__choose_group(self.groups)
        target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

        # Read the CSV file to get the list of users
        users = self.__read_csv_file()

        # Add users to the group
        await self.add_users_to_group(target_group_entity, users, input_file)

