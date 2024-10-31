import asyncio
from datetime import datetime
import re
import pytz
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import UserStatusOffline, InputPeerChannel, InputUser, InputPeerEmpty, User
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import LeaveChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from colorama import Fore, Style, init , Back
import csv
import time
import random
import traceback
import os
from misc import eval_input
from telethon.tl.types import User 
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest , UpdateUsernameRequest 
from telethon.tl.functions.account import SetPrivacyRequest
from telethon.tl.types import InputPrivacyValueDisallowAll
from telethon.tl.types import InputPrivacyKeyChatInvite , InputPrivacyKeyPhoneCall
from telethon.tl.functions.photos import UploadProfilePhotoRequest
import requests
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteHashExpiredError,
    InviteHashInvalidError
)
from other_function import delete_rows_members
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import Channel, Chat
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest
from telethon.tl.types import Channel
from telethon.tl.types import InputPeerChannel, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, ChatAdminRequiredError
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantRequest

class TelegramBot:
    def __init__(self, api_id, api_hash, session_file):
        self.client = TelegramClient(session_file, api_id, api_hash)
        self.sleep_time = 5 
        self.chats = []
        self.last_date = None
        self.chunk_size = 200
        self.groups = []
        self.groups_id = []
        self.me = None
        restricted = False
        self.channels = []
        self.channels_id = []



    async def start(self):
        await self.client.start()
        result = await self.client(GetDialogsRequest(
            offset_date=self.last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=self.chunk_size,
            hash=0
        ))
        self.chats.extend(result.chats)
        await self.__get_me()


    async def __get_me(self):
        self.me = await self.client.get_me()

        if not isinstance(self.me, User):
            print("Unexpected error please try again!")
            exit()

    async def check_spam(self):
        self.restricted = False
        @self.client.on(events.NewMessage(from_users='SpamBot'))
        async def handler(event):
            message = event.message.text
            match = re.search(r'released on (\d{1,2} \w+ \d{4}, \d{2}:\d{2} UTC)', message)

            if match: 
                release_date = match.group(1)
                print(f"{Fore.LIGHTRED_EX}Release date : {release_date}")
                self.restricted = True
            else:
                print(f"{Fore.LIGHTGREEN_EX}This bot is free ")
        
        spam_bot = await self.client.get_entity('@SpamBot')
        await self.client.send_message(spam_bot, '/start')

        print(f"Waiting for SpamBot response for {str(self.me.first_name) + " " +str(self.me.last_name if self.me.last_name else "")}")
        await asyncio.sleep(1)  

        return self.restricted    

    async def check_account_broken(self):
        self.restricted = False

        @self.client.on(events.NewMessage(from_users='SpamBot'))
        async def handler(event):
            message = event.message.text

            if "While the account is limited" in message:
                print(f"{Fore.LIGHTRED_EX}Account is limited.")
                self.restricted = True
            else:
                print(f"{Fore.LIGHTGREEN_EX}This bot is free.")
            
            self.client.remove_event_handler(handler, events.NewMessage(from_users='SpamBot'))

        spam_bot = await self.client.get_entity('@SpamBot')
        await self.client.send_message(spam_bot, '/start')

        print(f"Waiting for SpamBot response for {self.me.first_name} {self.me.last_name or ''}")
        await asyncio.sleep(1)

        return self.restricted

    async def __get_chat(self):
        """Get list of all Megagroup in Chat list."""
        # Clear the groups and groups_id lists before fetching chats
        self.groups = []  # Reset groups
        self.groups_id = set()  # Use a set to ensure unique IDs

        for chat in self.chats:
            if getattr(chat, 'megagroup', False) and chat.id not in self.groups_id:
                self.groups.append(chat)
                self.groups_id.add(chat.id)  # Add the ID to the set to ensure uniqueness
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
    async def __get_channel(self):
        """
        Fetches channels from the bot's dialogs and ensures unique entries.
        """
        # Clear previous channel data
        self.channels = []
        self.channels_id = set()

        try:
            # Get all dialogs (conversations) for the client
            async for dialog in self.client.iter_dialogs():
                # Check if the chat is a channel and is unique
                if dialog.is_channel and not dialog.is_group:
                    if dialog.id not in self.channels_id:
                        self.channels.append(dialog.entity)
                        self.channels_id.add(dialog.id)
        except Exception as e:
            print(f"Error fetching channels: {e}")

    async def print_channel(self):
        """
        Prints the list of channels. If channels haven't been fetched, it fetches them first.
        """
        # Fetch channels if the list is empty
        if not self.channels:
            await self.__get_channel()

        # Print channels or a message if none are found
        if not self.channels:
            print("No channels found.")
        else:
            for index, channel in enumerate(self.channels, 1):
                try:
                    print(f"{index} - {channel.title} | ID - {channel.id}")
                except AttributeError:
                    print(f"{index} - Channel {channel.id} (title not available)")


    async def __LeaveChannel(self, group_id):
        try:
            await self.client(LeaveChannelRequest(group_id))
            print(f"[+] Left the group with ID {Fore.RED}{group_id}{Style.RESET_ALL} due to forwarding failure.")
        except Exception as leave_error:
            print(f"[!] Failed to leave the group {group_id}: {str(leave_error)}")


    async def forward_message_to_group(self, group_id, from_chat_id, message_id):
        """Forward the message from Chat to the group and leave if it fails."""
        try:
            await self.client.forward_messages(entity=group_id, messages=message_id, from_peer=from_chat_id)
            print(f"{Fore.GREEN}Message ID {message_id} forwarded to group with ID {group_id}{Style.RESET_ALL}")
        except Exception as e:
            print(f"Failed to forward message to group {group_id}: {str(e)}")
            await self.__LeaveChannel(group_id)


    async def forward_message_to_all_groups(self, limit):
        """
        Forward Message from Saved Messages to all Megagroup.
    
        Limit initially set to 1. Meaning the last saved message.
    
        Change it to n to Forward n last Saved Message. 
        """
        if not self.groups:
            await self.__get_chat()
        
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
    
    async def join_group_via_link(self, invite_link: str):
        try:
            if '+' in invite_link:
                # For new private invite links (t.me/+xxx)
                invite_code = invite_link.split('+')[1]
                print(f"New private group invite code: {Fore.CYAN}{invite_code}{Style.RESET_ALL}")
                await self.client(ImportChatInviteRequest(invite_code))
                
            elif 'joinchat' in invite_link:
                # For old private invite links (t.me/joinchat/xxx)
                invite_code = invite_link.split('/')[-1]
                print(f"Private group invite code: {Fore.CYAN}{invite_code}{Style.RESET_ALL}")
                await self.client(ImportChatInviteRequest(invite_code))
                
            else:
                # For public groups
                group_username = invite_link.split('/')[-1]
                print(f"Public group username: {Fore.CYAN}{group_username}{Style.RESET_ALL}")
                await self.client(JoinChannelRequest(group_username))
            
            print(f"{Fore.GREEN}[+] Successfully joined the group.{Style.RESET_ALL}")
            return True
            
        except UserAlreadyParticipantError:
            print(f"{Fore.YELLOW}[!] Already a member of this group{Style.RESET_ALL}")
            return True
            
        except FloodWaitError as e:
            print(f"{Fore.RED}[!] Flood wait error. Need to wait {e.seconds} seconds{Style.RESET_ALL}")
            return False
            
        except (InviteHashExpiredError, InviteHashInvalidError):
            print(f"{Fore.RED}[!] Invalid or expired invite link{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to join the group: {e}{Style.RESET_ALL}")
            return False
    def __print_messages(self, messages):
        for message in messages:
            print(f"Message: {message.text}, Message ID: {message.id}")
    

    async def __forward_to_all(self, group_ids, chat_id, messages):
        # Remove any duplicate group IDs
        unique_group_ids = list(set(group_ids))
        print(f"Unique group IDs: {unique_group_ids}")

        # Ensure at least one message exists
        if not messages:
            print("No messages to forward.")
            return

        # If only 1 message is to be forwarded, avoid the nested loop
        if len(messages) == 1:
            message_to_forward = messages[0]
            print(f"Forwarding single message ID {message_to_forward.id} to all groups")
            for group_id in unique_group_ids:
                try:
                    await self.forward_message_to_group(group_id, chat_id, message_to_forward.id)
                except Exception as e:
                    print(f"Failed to forward message to group {group_id}: {e}")
        else:
            # Forward multiple messages to all groups
            for group_id in unique_group_ids:
                for message in messages:
                    try:
                        await self.forward_message_to_group(group_id, chat_id, message.id)
                    except Exception as e:
                        print(f"Failed to forward message to group {group_id}: {e}")

        print("Forwarding completed.")

    async def scrape_members(self, target_group):
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

            # Skip users without a username
            if not user.username:
                print(f"Skipping user with no username (ID: {user.id})")
                continue
            
            # Skip users whose username starts with 'user_'
            if user.username.startswith("user_"):
                print(f"Skipping user with 'user_' username: {user.username} (ID: {user.id})")
                continue

            # Gather user info for valid users
            user_info = self.__get_user_info(user)
            if user_info:
                members_to_write.append(user_info)

        # Write filtered members to CSV
        self.__write_members_to_csv(members_to_write, target_group.title, target_group.id)
        print('[+] Members with valid usernames scraped successfully.')

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
    

    def __write_members_to_csv(self, members, target_group_title, target_group_id, filename="members.csv"):
        """Write members to a CSV file."""
        file_exists = os.path.isfile(filename)
        
        with open(filename, "a", encoding='UTF-8') as f:
            writer = csv.writer(f, delimiter=",", lineterminator="\n")
            
            if not file_exists:
                writer.writerow(['username', 'user_id', 'name', 'group', 'group_id'])
            
            for member in members:
                writer.writerow([member['username'], member['user_id'], member['name'], target_group_title, target_group_id])


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
    async def choose_channel(self):
        """
        Allows user to choose a channel from available channels
        """
        await self.print_channel()
        print(Fore.GREEN + "[+] Available channels:" + Style.RESET_ALL)

        try:
            c_index = int(input("[+] Enter a number: "))
            
            if c_index <= 0 or c_index > len(self.channels):
                print(f"{Fore.RED}Invalid channel number.{Style.RESET_ALL}")
                return None

            target_channel = self.channels[c_index - 1]
            target_channel_entity = InputPeerChannel(target_channel.id, target_channel.access_hash)
            return {'target_channel': target_channel, 'target_channel_entity': target_channel_entity}
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number.{Style.RESET_ALL}")
            return None



    async def choose_group(self):
        self.groups.clear()

        print(Fore.GREEN + "[+] Available groups:" + Style.RESET_ALL)
        await self.print_chat()

        g_index = eval(input("[+] Enter a number: "))
        
        if type(g_index) != int:
            print("Invalid Input! Exiting the program...")
            exit()

        if g_index <= 0 or g_index > len(self.groups):
            print("Invalid group number.")
            exit()

        target_group = self.groups[g_index - 1]
        target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)
        return {'target_group': target_group, 'target_group_entity':target_group_entity}


    def __read_csv_file(self, input_file): # also in misc
        """
        Read member from CSV with this format username,user_id,access_hash,name
        """

        users = []
        with open(input_file, mode="r", encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)  # Skip header
            for row in rows:
                user = {
                    'username': row[0],
                    'user_id': int(row[1]),
                    'name': row[2]
                }
                users.append(user)
        return users
    
    async def add_user_by_username(self, target_group_entity, user_data):
        try:
            username = user_data['username']

            if username.startswith("user_"):
                print(f"{Fore.YELLOW}[!] Skipping user: {username} because it starts with 'user_'{Style.RESET_ALL}")
                remove_user_from_csv(username, "members.csv")
                return False  # Skip the rest of the process

            print(f"[+] Attempting to add user: {username} ({user_data['name']})")

            # Resolve the username to get the user entity
            user_to_add = await self.client.get_input_entity(username)

            # Add the user to the group
            await self.client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print(f"{Fore.GREEN}[+] Successfully added user: {username}{Style.RESET_ALL}")

            delay = random.uniform(1, 3)
            print(f"[+] Waiting for {delay:.2f} seconds before next action...")
            await asyncio.sleep(delay)
            return True

        except ValueError as e:
            print(f"{Fore.RED}[!] Could not find user with username: {username}{Style.RESET_ALL}")
            return False
        except PeerFloodError:
            print(f"{Fore.RED}[!] Flood error from Telegram. Stopping for now.{Style.RESET_ALL}")
            raise
        except UserPrivacyRestrictedError:
            print(f"{Fore.YELLOW}[!] The user's ({username}) privacy settings prevent this action.{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error while adding {username}: {str(e)}{Style.RESET_ALL}")
            return False
    
    async def check_admin_rights(self, channel):
        """
        Check if the bot has admin rights in the channel
        """
        try:
            # Get the bot's participant info in the channel
            participant = await self.client(GetParticipantRequest(
                channel=channel,
                participant=await self.client.get_input_entity('me')
            ))
            
            # Check if the bot is an admin or creator
            is_admin = isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
            
            if not is_admin:
                print(f"{Fore.RED}[!] Bot does not have admin rights in this channel{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[!] Please make the bot an admin with 'Add Members' permission{Style.RESET_ALL}")
                return False
                
            # Check if the admin has invite users permission
            if isinstance(participant.participant, ChannelParticipantAdmin):
                admin_rights = participant.participant.admin_rights
                if not getattr(admin_rights, 'invite_users', False):
                    print(f"{Fore.RED}[!] Bot does not have 'Add Members' permission{Style.RESET_ALL}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error checking admin rights: {str(e)}{Style.RESET_ALL}")
            return False

    async def add_members_to_channel_by_username(self, target_channel_entity, user_data):
        """
        Adds a single member to the channel
        """
        try:
            if not isinstance(user_data, dict) or 'username' not in user_data:
                print(f"{Fore.RED}[!] Invalid user data format{Style.RESET_ALL}")
                return False

            username = user_data['username']
            name = user_data.get('name', 'Unknown Name')

            if username.startswith("user_"):
                print(f"{Fore.YELLOW}[!] Skipping user: {username} because it starts with 'user_'{Style.RESET_ALL}")
                remove_user_from_csv(username, "members.csv")
                return False

            print(f"[+] Attempting to add user: {username} ({name})")

            # Resolve the username to get the user entity
            user_to_add = await self.client.get_input_entity(username)

            # Add the user to the group
            await self.client(InviteToChannelRequest(target_channel_entity, [user_to_add]))
            print(f"{Fore.GREEN}[+] Successfully added user: {username}{Style.RESET_ALL}")

            delay = random.uniform(1, 3)
            print(f"[+] Waiting for {delay:.2f} seconds before next action...")
            await asyncio.sleep(delay)
            return True

        except ValueError as e:
            print(f"{Fore.RED}[!] Could not find user with username: {username}{Style.RESET_ALL}")
            return False
        except PeerFloodError:
            print(f"{Fore.RED}[!] Flood error from Telegram. Stopping for now.{Style.RESET_ALL}")
            raise
        except UserPrivacyRestrictedError:
            print(f"{Fore.YELLOW}[!] The user's ({username}) privacy settings prevent this action.{Style.RESET_ALL}")
            return False
        except ChatAdminRequiredError:
            print(f"{Fore.RED}[!] Bot needs admin privileges to add members.{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error while adding {username}: {str(e)}{Style.RESET_ALL}")
            return False

    async def add_users_to_channel(self, target_channel_entity, target_channel, members):
        """
        Adds multiple members to the channel
        """
        # First check admin rights
        if not await self.check_admin_rights(target_channel):
            print(f"{Fore.RED}[!] Cannot proceed without proper admin rights{Style.RESET_ALL}")
            return []

        successful_adds = 0
        failed_adds = 0
        flood_error_count = 0
        max_flood_errors = 3
        failed_members = []

        try:
            amount_user = int(input("How many users you want to add for each bot: "))
        except ValueError:
            print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
            return failed_members

        for member in members:
            if successful_adds >= amount_user:
                print(f"{Fore.GREEN}[+] Reached target amount of {amount_user} users. Stopping...{Style.RESET_ALL}")
                break

            try:
                success = await self.add_members_to_channel_by_username(target_channel_entity, member)

                if success:
                    successful_adds += 1
                    print(f"{Fore.GREEN}[+] Successfully added {member['username']}. Progress: {successful_adds}/{amount_user}{Style.RESET_ALL}")
                    
                    delay = random.uniform(1, 5)
                    print(f"{Fore.CYAN}Waiting for {delay:.2f} seconds before next addition...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)
                else:
                    failed_adds += 1
                    failed_members.append(member)
                    print(f"{Fore.YELLOW}[-] Failed to add {member['username']}. Total failed: {failed_adds}{Style.RESET_ALL}")
                    
                    if failed_adds >= 3:
                        print(f"{Fore.RED}[!] Reached maximum failed attempts (3){Style.RESET_ALL}")
                        break

            except PeerFloodError:
                flood_error_count += 1
                failed_members.append(member)
                print(f"{Fore.RED}[!] Flood error occurred. Count: {flood_error_count}/{max_flood_errors}{Style.RESET_ALL}")
                
                if flood_error_count >= max_flood_errors:
                    print(f"{Fore.RED}[!] Stopping due to multiple flood errors.{Style.RESET_ALL}")
                    break

                await asyncio.sleep(random.uniform(5, 10))

            except Exception as e:
                failed_adds += 1
                failed_members.append(member)
                print(f"{Fore.RED}[-] Unexpected error with {member['username']}: {str(e)}{Style.RESET_ALL}")

        if successful_adds > 0:
            await delete_rows_members("members.csv", successful_adds)
            print(f"{Fore.GREEN}[+] Deleted {successful_adds} successful entries from members.csv{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Final Results:{Style.RESET_ALL}")
        print(f"✓ Successfully added: {successful_adds} users")
        print(f"✗ Failed to add: {failed_adds} users")
        print(f"⚠ Flood errors: {flood_error_count}")
        
        return failed_members

    async def add_users_to_group(self, target_group_entity, usernames):
        successful_adds = 0
        failed_adds = 0
        flood_error_count = 0
        max_flood_errors = 3
        
        # Get the amount of users to add at the start
        amount_user = int(input("How many users you want to add for each bot: "))
        
        # Create a list to track failed usernames
        failed_members = []

        for username in usernames:
            # Check if we've reached the desired amount of successful adds
            if successful_adds >= amount_user:
                print(f"{Fore.GREEN}[+] Reached target amount of {amount_user} users. Stopping...{Style.RESET_ALL}")
                break

            try:
                success = await self.add_user_by_username(target_group_entity, username)

                if success:
                    successful_adds += 1
                    print(f"{Fore.GREEN}[+] Successfully added {username['username']}. Progress: {successful_adds}/{amount_user}{Style.RESET_ALL}")
                    
                    # Add delay between successful adds
                    delay = random.uniform(1, 5)
                    print(f"{Fore.CYAN}Waiting for {delay:.2f} seconds before next addition...{Style.RESET_ALL}")
                    await asyncio.sleep(delay)

                else:
                    failed_adds += 1
                    failed_members.append(username)
                    print(f"{Fore.YELLOW}[-] Failed to add {username['username']}. Total failed: {failed_adds}{Style.RESET_ALL}")
                    
                    if failed_adds >= 3:
                        print(f"{Fore.RED}[!] Reached maximum failed attempts (3){Style.RESET_ALL}")
                        break

            except PeerFloodError:
                flood_error_count += 1
                failed_members.append(username)
                print(f"{Fore.RED}[!] Flood error occurred. Count: {flood_error_count}/{max_flood_errors}{Style.RESET_ALL}")
                
                if flood_error_count >= max_flood_errors:
                    print(f"{Fore.RED}[!] Stopping due to multiple flood errors.{Style.RESET_ALL}")
                    break

                # Add longer delay after flood error
                await asyncio.sleep(random.uniform(5, 10))

            except UserPrivacyRestrictedError:
                failed_adds += 1
                failed_members.append(username)
                print(f"{Fore.YELLOW}[-] Could not add {username['username']} due to privacy restrictions.{Style.RESET_ALL}")

            except Exception as e:
                failed_adds += 1
                failed_members.append(username)
                print(f"{Fore.RED}[-] Unexpected error with {username['username']}: {str(e)}{Style.RESET_ALL}")

        # After the loop ends (either by completion or breaking), delete the successful rows
        if successful_adds > 0:
            await delete_rows_members("members.csv", successful_adds)
            print(f"{Fore.GREEN}[+] Deleted {successful_adds} successful entries from members.csv{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Final Results:{Style.RESET_ALL}")
        print(f"✓ Successfully added: {successful_adds} users")
        print(f"✗ Failed to add: {failed_adds} users")
        print(f"⚠ Flood errors: {flood_error_count}")
        
        return failed_members    
    async def add_members_to_group(self, input_file):
        """
        Add members to a group
        """

        # Get megagroups from the chats
        
        if not self.groups:
            await self.__get_chat()

        if not self.groups:
            print("[!] No megagroups found.")
            return

        # Let user select the group
        
        chosen_group = await self.choose_group()
        target_group_entity = chosen_group['target_group_entity']

        # Read the CSV file to get the list of users
        users = self.__read_csv_file(input_file=input_file)

        # Add users to the group
        await self.add_users_to_group(target_group_entity, users, input_file)


    async def add_U2G(self, target_group_entity, user):
        try:                

            if 'username' in user['username']:
                user_to_add = InputUser(user['username'])
                print(f"[+] Adding user : {user['name']} - ID : {user['user_id']}")

            # Add the user to the group
            await self.client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            print("[+] User successfully added. Removing user from list.")
            
            # Wait between 10 to 30 seconds to avoid getting rate-limited
            print("[+] Waiting for 10-30 seconds before adding the next user...")
            time.sleep(random.uniform(10, 30))

        except PeerFloodError:
            print("[!] Flood error from Telegram. Saving remaining users back to CSV and stopping the script.")
            
        except UserPrivacyRestrictedError:
            print("[!] The user's privacy settings prevent this action. Skipping to the next user.")
            
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            traceback.print_exc()


    # User details

    async def update_name(self):
        try:
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            await self.client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
            print(f"{Fore.GREEN}[+] Name updated to {first_name} {last_name}.")
        except Exception as e:
            print(f"Error updating name: {str(e)}")


    async def update_username(self):
        try:
            username = input("Enter username (use `` to remove username): ")

            
            # If the username is provided, ensure it's valid
            if username and not (username.isalnum() or "_" in username):
                print("Invalid username. Please enter only alphanumeric characters and underscores.")
                return

            # Update or remove the username
            await self.client(UpdateUsernameRequest(username=username))
            
            if username == "":
                print("Username removed successfully.")
            else:
                print(f"Username updated to {username}.")
                
        except Exception as e:
            print(f"Error updating/removing username: {str(e)}")

    
    async def remove_all_bot_username(self):
        username = ''
        try: 
            await self.client(UpdateUsernameRequest(username=username))
            if username == "":
                print("Username removed successfully.")
            else:
                print(f"Username updated to {username}.")
        except Exception as e:
            print(f"Error updating/removing username: {str(e)}")


    async def update_bot_bio(self):
        BIO_LIST = [
            "Lover of technology and coding.",
            "Just another bot in the Telegram universe.",
            "Here to make your life easier!",
            "Coding is my superpower.",
            "In a relationship with Python.",
            "Bot powered by coffee.",
            "Always learning, always growing.",
            "Sharing knowledge and friendship.",
            "Let's connect and share ideas!",
            "Living the bot life one message at a time.",
            "Living with the present forgot about the past." , 
            "Enjoy your adult life once you not able to turn back." , 
            "Appreciate with your life." , 
            "Life is not perfect but it's acceptable.",
            "Learning growing together. " , 
            "Family is the real supporter."
            "Don't let the time passed let enjoy the moment.",
            "Enjoy your time with your family some people can't even enjoy it even they want." , 
            "Life is not a race, it's a journey.",
            "Life is a beautiful journey filled with love, loss, and growth.",
        ]
        bio = random.choice(BIO_LIST) 
        try:
            await self.client(UpdateProfileRequest(about=bio))
            print("Bio updated successfully.")
        except Exception as e:
            print(f"Error updating bio: {str(e)}")

    async def update_privacy_settings(self):
            try:
                # Set call privacy to nobody
                await self.client(SetPrivacyRequest(
                    key=InputPrivacyKeyPhoneCall(),
                    rules=[InputPrivacyValueDisallowAll()]
                ))
                print("Call privacy updated successfully")

                # Set group invite privacy to nobody
                await self.client(SetPrivacyRequest(
                    key=InputPrivacyKeyChatInvite(),
                    rules=[InputPrivacyValueDisallowAll()]
                ))
                print("Group invite privacy updated successfully")

            except Exception as e:
                print(f"An error occurred: {str(e)}")

    async def update_profile_picture_from_url(self, image_url):
        try:
            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an error for bad responses

            # Create a temporary file to store the image
            temp_file_path = 'temp_image.jpg'
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)

            # Upload the file
            file = await self.client.upload_file(temp_file_path)

            # Update the profile photo using UploadProfilePhotoRequest
            await self.client(UploadProfilePhotoRequest(
                file=file
            ))
            
            print(f"{Fore.GREEN}[+] Profile picture updated successfully from URL.{Style.RESET_ALL}")

            # Clean up the temporary file
            os.remove(temp_file_path)
            
        except Exception as e:
            print(f"{Fore.RED}[-] Error updating profile picture from URL: {str(e)}{Style.RESET_ALL}")


    async def forward_from_group_to_saved(self, group_id):
        """Listen for forwarded messages in a specific group and forward them to Saved Messages."""
        @self.client.on(events.NewMessage(chats=group_id))
        async def handler(event):
            # Check if the message is forwarded
            if event.message.fwd_from:
                # Forward the message to your Saved Messages
                saved_messages_peer = 'me'
                await self.client.forward_messages(saved_messages_peer, event.message)

                print(f"{Fore.GREEN}Forwarded a message to Saved Messages from group {group_id}{Style.RESET_ALL}")

    async def show_last_five_messages(self, group_id):
        try:
            # Fetch group information
            group_info = await self.client.get_entity(group_id)

            # Fetch the last 5 messages from the group
            messages = await self.client.get_messages(group_id, limit=5)
            
            print(f"{Fore.CYAN}Last 5 messages from group '{group_info.title}' (ID: {group_info.id}):{Style.RESET_ALL}")
            for idx, message in enumerate(messages):
                print(f"================================================")
                message_text = message.text if message.text else "Media/Non-text message"
                print(f"{Fore.WHITE}Messages index : [{idx}] - {Back.LIGHTGREEN_EX}{message_text}{Style.RESET_ALL}")

            # Ask user how many messages they want to forward
            num_messages = int(input(f"{Fore.GREEN}[+]How many messages do you want to forward : {Style.RESET_ALL} "))

            # Get the indexes of the messages to forward
            selected_indexes = []
            for _ in range(num_messages):
                idx = int(input(f"{Fore.LIGHTYELLOW_EX}Enter the message index to forward:{Style.RESET_ALL} "))
                if idx < len(messages):  # Check if the index is valid
                    selected_indexes.append(idx)
                else:
                    print(f"Invalid index {idx}. Please enter a valid index.")

            # Forward the selected messages
            await self.forward_selected_messages(group_id, selected_indexes)

        except Exception as e:
            print(f"{Fore.RED}Failed to fetch messages from group {group_id}: {str(e)}{Style.RESET_ALL}")

    async def forward_selected_messages(self, group_id, selected_indexes):
        """Forward selected messages to Saved Messages."""
        try:
            # Get the last 5 messages from the group
            messages = await self.client.get_messages(group_id, limit=5)

            # Get the "Saved Messages" entity (your personal cloud chat)
            saved_messages_peer = await self.client.get_input_entity('me')

            # Iterate through the selected indexes and forward the messages
            for idx in selected_indexes:
                if idx < len(messages):
                    message_id = messages[idx].id  # Get the message ID to forward
                    from_peer = await self.client.get_input_entity(group_id)  

                    # Forward the message to Saved Messages
                    await self.client.forward_messages(
                        saved_messages_peer,  # Destination (Saved Messages)
                        messages=message_id,  # Message ID to forward
                        from_peer=from_peer   # The source group/entity
                    )
                    print(f"Forwarded message with index [{idx}] to Saved Messages")
                else:
                    print(f"Invalid message index: {idx}")
        except Exception as e:
            print(f"Failed to forward messages: {str(e)}")

    async def remove_all_saved_messages(self):
        try:
            saved_messages = await self.client.get_input_entity('me')
            
            messages = await self.client.get_messages(saved_messages, limit=100)
            print(f"Found {len(messages)} messages in Saved Messages: {[msg.id for msg in messages]}")  # Debug output


            for message in messages:
                await self.client.delete_messages(saved_messages, message.id)
                print(f"Deleted message ID {message.id}")

                # Respect rate limits
                await asyncio.sleep(1)
                                
                if len(messages) == 0:
                    print("No more messages to delete.")
                    break

        except Exception as e:
            print(f"Failed to delete messages: {str(e)}")


    async def leave_all_groups(self):
        """Leave all Telegram groups and channels."""
        async for dialog in self.client.iter_dialogs():
            try:
                entity = dialog.entity
                dialog_name = dialog.name or "Unnamed"
                
                if isinstance(entity, Channel):
                    print(f"Attempting to leave channel/supergroup: {Fore.YELLOW}{Style.BRIGHT}{dialog_name}")
                    try:
                        input_entity = await self.client.get_input_entity(dialog.id)
                        await self.client(LeaveChannelRequest(input_entity))
                        print(f"{Fore.GREEN}Successfully left channel: {dialog_name}")
                    except Exception as e:
                        print(f"{Fore.RED}Error leaving channel {dialog_name}: {str(e)}")
                        
                elif isinstance(entity, Chat):
                    print(f"Attempting to leave basic group: {dialog_name}")
                    try:
                        # Get your own user ID
                        me = await self.client.get_me()
                        await self.client(DeleteChatUserRequest(
                            chat_id=entity.id,
                            user_id=me.id
                        ))
                        print(f"Successfully left basic group: {dialog_name}")
                    except Exception as e:
                        print(f"Error leaving basic group {dialog_name}: {str(e)}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error processing dialog: {str(e)}")
                continue

        print("Finished processing all groups and channels.")

    async def auto_pvt_message(self, user, message_text):
        try:

            # Check if the user object is valid
            if hasattr(user, 'username'):
                print(f"Sending message to {user.username} (ID: {user.id})")
            else:
                print(f"Sending message to ID: {user.id}")

            # Send message using the user object directly
            await self.client.send_message(user, message_text)
            print("Message sent successfully!")
            return True  # Indicate success

        except Exception as e:
            print(f"Failed to send message to {user.username or user.id}: {e}")
            return False  # Indicate failure    
    # Function to remove the user from the CSV
def remove_user_from_csv(username_to_remove, csv_file):
    try:
        # Read the CSV and filter out the user with username 'user_'
        with open(csv_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = [row for row in reader if row['username'] != username_to_remove]

        # Write the filtered data back to the CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"{Fore.GREEN}[+] User {username_to_remove} removed from {csv_file}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] Error while removing user from CSV: {str(e)}{Style.RESET_ALL}")
