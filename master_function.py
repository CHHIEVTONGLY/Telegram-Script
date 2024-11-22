import asyncio
from telethon import events
import csv
import os
import random
import pandas as pd
from telethon.tl.functions.account import UpdateProfileRequest 
import sys
from colorama import Fore , Back, Style
from misc import exit_the_program, read_csv_file, write_members_to_csv, eval_input, write_sent_members_to_csv , count_rows_in_csv
from typing import List, Tuple
from TelegramBot import TelegramBot


async def print_bot_info(bot: TelegramBot):
    user_info = f"Account name : {bot.me.first_name} {bot.me.last_name if bot.me.last_name else ''}"
    print(user_info)
    return


async def print_all_bots_info(bots: List[Tuple[int, TelegramBot]]):
    api_sessions = []  # To store the session keys from the CSV

    # Reading the CSV file and storing the session keys
    with open("credentials.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            api_sessions.append(row["session_key"])

    for index, bot in bots:
        user_info = f"{Fore.GREEN}{index}.{Style.RESET_ALL} Account name : {bot.me.first_name} {bot.me.last_name if bot.me.last_name else ''} , {Fore.BLUE}Session file : {api_sessions[index-1]}"
        print(user_info)
    return


async def print_bot_chat(bot: TelegramBot):
    await bot.print_chat()
    return


async def print_all_bots_chat(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print("Chat From Bot", index)
        await print_bot_chat(bot)
    return

async def print_bot_channel_chat(bot: TelegramBot): 
    """
    Prints the channels for a single bot.
    """
    if not bot.client:
        print("Error: Bot client not initialized")
        return
    await bot.print_channel()

async def print_all_bot_channel_chat(bots: List[Tuple[int, TelegramBot]]):
    """
    Prints channels for each bot in the list of bots.
    """
    for index, bot in bots:
        print(f"Channels From Bot {Fore.GREEN}{index}")
        await print_bot_channel_chat(bot)
        print()


REPLIED_USERS_FILE = 'reply_data.csv'

# Load replied users from the CSV file if it exists
replied_users = set()
if os.path.exists(REPLIED_USERS_FILE):
    with open(REPLIED_USERS_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        replied_users = {int(row[0]) for row in reader}

async def load_auto_reply_message():
    message_file = 'auto_reply_message.txt'

    if os.path.exists(message_file):
        with open(message_file, 'r', encoding='utf-8') as f:
            return f.read().strip() 
    else:
        print("auto_reply_message.txt not found. Please input the auto-reply message:")
        user_message = input("Enter the auto-reply message: ")

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(user_message)

        print(f"Auto-reply message saved in {message_file}.")
        return user_message


async def read_message_file(message_path: str) -> str:
    """Read message content from file"""
    try:
        with open(message_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"{Fore.RED}[!] Error reading message file: {str(e)}{Style.RESET_ALL}")
        return ""
    

async def auto_reply(bot):
    auto_reply_message = await load_auto_reply_message()

    @bot.client.on(events.NewMessage)
    async def handle_new_message(event):
        if event.is_private:
            sender_id = event.sender_id
            if sender_id not in replied_users:
                await event.reply(auto_reply_message)
                replied_users.add(sender_id)
                with open(REPLIED_USERS_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([sender_id])

async def message_file():
    message_file = 'message_to_send.txt'
    if os.path.exists(message_file):
        with open(message_file, 'r', encoding='utf-8') as f:
            return f.read().strip() 
    else:
        print("message_to_send.txt not found. Please input the message you want to send :")
        user_message = input("Enter the message: ")

        with open(message_file, 'w', encoding='utf-8') as f:
            f.write(user_message)

        print(f"Message saved in {message_file}.")
        return user_message
    
async def all_bots_send_message(
    bots: List[Tuple[int, TelegramBot]], 
    members_file: str = "members.csv", 
    message_path: str = "message_to_send.txt"
):
    await message_file()
    """Main function to handle message sending through multiple bots."""
    try:
        message_text = await read_message_file(message_path)
        if not message_text:
            print(f"{Fore.RED}[!] No message content found.{Style.RESET_ALL}")
            return

        # Assuming read_csv_file is synchronous
        members = read_csv_file(members_file)
        if not members:
            print(f"{Fore.YELLOW}[!] No members found in the CSV file.{Style.RESET_ALL}")
            return

        total_members = len(members)
        print(f"{Fore.CYAN}[+] Total members in CSV: {total_members}{Style.RESET_ALL}")

        try:
            num_messages_per_bot = int(input("Enter the number of members each bot should send messages to: "))
        except ValueError:
            print(f"{Fore.RED}[!] Invalid input. Please enter a number.{Style.RESET_ALL}")
            return
        


        all_failed_members = []
        for index, bot in bots:
            print(f"{Fore.RED}Checking restricted forwards message...")
            is_restricted = await bot.check_account_broken()

            if is_restricted:
                print(f"{Fore.RED}Bot {index} is {Style.BRIGHT}broken{Style.RESET_ALL}{Fore.RED} and cannot send messages.")
                await asyncio.sleep(1)
                continue 

            print(f"\n{Fore.CYAN}[+] Bot {index} starting message-sending process{Style.RESET_ALL}")

            # Limit bot members
            bot_members = members[index::len(bots)][:num_messages_per_bot]  
            failed_members = []

            for member in bot_members:
                try:
                    username = member.get('username', '').strip()
                    if username:
                        user_to_message = await bot.client.get_entity(username)
                        print(f"Username : {username}")

                        if hasattr(user_to_message, 'username'):
                            success = await bot.auto_pvt_message(user_to_message, message_text)
                            if success:
                                # Remove successfully messaged member from the list
                                members.remove(member)
                                print(f"{Fore.GREEN}[+] Message sent to {user_to_message.username}{Style.RESET_ALL}")
                            else:
                                failed_members.append(member)
                                print(f"{Fore.YELLOW}[!] Failed to send to {user_to_message.username}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}[!] User '{username}' does not have a valid username.{Style.RESET_ALL}")
                            failed_members.append(member)
                    else:
                        print(f"{Fore.YELLOW}[!] Invalid username in member data{Style.RESET_ALL}")
                        failed_members.append(member)

                    # Write updated members back to CSV after each success
                    write_sent_members_to_csv(members, filename=members_file)

                    await asyncio.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"{Fore.RED}[!] Error sending to member: {str(e)}{Style.RESET_ALL}")
                    failed_members.append(member)
                    continue
            
            all_failed_members.extend(failed_members)
            await asyncio.sleep(random.uniform(2, 5))

        # Save failed members
        if all_failed_members:
            failed_file = "failed_members.csv"
            write_sent_members_to_csv(all_failed_members, filename=failed_file)
            print(f"{Fore.YELLOW}[+] Failed message attempts saved to {failed_file}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] Error in message-sending process: {str(e)}{Style.RESET_ALL}")

        
async def all_bots_forward(bots: List[Tuple[int, TelegramBot]]):
    limit = eval_input("How many messages? (Default=1): ", 0, 100, 1)
    print(f"Send {limit} messages to each group.")
    bot_count = len(bots)

    cycle_forward = 0

    while True:
        cycle_forward += 1
        print(f"{Fore.BLUE}Forwarding cycles : {Fore.GREEN}{cycle_forward}")
        
        for index, bot in bots:
            print(f"{Fore.RED}Checking restricted forwards message...")
            is_restricted = await bot.check_spam()

            print(f"{Back.GREEN}{is_restricted}")

            if is_restricted:
                print(f"{Fore.RED}Bot {index} is restricted and cannot forward messages.")
                await asyncio.sleep(1)
                continue 


            print("Forwarding from Bot", index)
            await bot.forward_message_to_all_groups(limit)

            if bot_count <= 5:
                delay1 = 5*60
                delay2 = 5.5*60
            elif 5 < bot_count <= 10:
                delay1 = 3.5*60
                delay2 = 4*60
            elif 10 < bot_count <= 15:
                delay1 = 2.5*60
                delay2 = 3*60
            else:
                delay1 = 1*60
                delay2 = 2*60


            delay = random.uniform(delay1, delay2)

            minutes = int(delay // 60)
            seconds = int(delay % 60)

            print(f"Waiting for {minutes} minutes and {seconds} seconds")
            await asyncio.sleep(delay)

async def all_bots_forward_and_auto_reply(bots: List[Tuple[int, TelegramBot]]):
    limit = eval_input("How many messages? (Recommend = 1 message ): ", 0, 100, 1)
    print(f"Send {limit} messages to each group.")
    

    cycle_forward = 0

    while True:
        cycle_forward += 1
        print(f"{Fore.BLUE}Forwarding cycles : {Fore.GREEN}{cycle_forward}")
        
        for index, bot in bots:
            print(f"{Fore.RED}Checking restricted forwards message...")
            is_restricted = await bot.check_spam()

            print(f"{Back.GREEN}{is_restricted}")

            if is_restricted:
                print(f"{Fore.RED}Bot {index} is restricted and cannot forward messages.")
                await asyncio.sleep(1)
                continue 


            print("Forwarding from Bot", index)
            await bot.forward_message_to_all_groups(limit)

            delay = random.uniform(120, 160)

            minutes = int(delay // 60)
            seconds = int(delay % 60)

            print(f"Waiting for {minutes} minutes and {seconds} seconds")
            await auto_reply(bot)
            await asyncio.sleep(delay)

              


async def all_bots_join_group(bots: List[Tuple[int, TelegramBot]]):
    # Ask the user for the number of groups to join
    limit = int(input("How many groups to join: "))
    
    # Collect multiple invite links
    invite_links = []
    for i in range(limit):
        link = input(f"Input invite link #{i + 1}: ")
        invite_links.append(link)
    
    # Loop through each bot
    for index, bot in bots:
        print(f"Bot {index} starting to join groups...")
        
        # Loop through each invite link and join the group
        for link in invite_links:
            print(f"Bot {index} trying to join: {Fore.YELLOW}{link}")
            await bot.join_group_via_link(link)
    
    return


async def all_bots_add_members(bots: List[Tuple[int, TelegramBot]], members_file="members.csv"):
    try:
        # Read and validate the CSV file
        members = read_csv_file(members_file)
        total_members = count_rows_in_csv('members.csv')
        print(f"{Fore.CYAN}[+] Total members in CSV: {total_members}{Style.RESET_ALL}")
        
        if not members:
            print(f"{Fore.YELLOW}[!] No members found in the CSV file.{Style.RESET_ALL}")
            return
            
        if not bots:
            print(f"{Fore.RED}[!] No bots available.{Style.RESET_ALL}")
            return

        # Let each bot process its portion of members
        all_failed_members = []
        for index, bot in bots:
            print(f"\n{Fore.CYAN}[+] Bot {index} starting member addition process{Style.RESET_ALL}")
            
            try:
                # Get fresh member list each time (in case it was modified by previous bot)
                current_members = read_csv_file(members_file)
                if not current_members:
                    print(f"{Fore.YELLOW}[!] No more members left to process.{Style.RESET_ALL}")
                    break
                    
                # Let bot choose target group
                chosen_group = await bot.choose_group()
                if not chosen_group:
                    print(f"{Fore.RED}[!] No group selected for bot {index}. Skipping.{Style.RESET_ALL}")
                    continue

                target_group_entity = chosen_group['target_group_entity']
                
                # Process members with this bot
                failed_members = await bot.add_users_to_group(target_group_entity, current_members)
                all_failed_members.extend(failed_members)
                
                # Optional delay between bots
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"{Fore.RED}[!] Error with bot {index}: {str(e)}{Style.RESET_ALL}")
                continue

        # Save failed members to CSV
        if all_failed_members:
            failed_file = "failed_members.csv"
            write_members_to_csv(all_failed_members, "Failed Users", filename=failed_file)
            print(f"{Fore.YELLOW}[+] Failed additions saved to {failed_file}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] Error in member addition process: {str(e)}{Style.RESET_ALL}")

async def all_bots_add_members_to_channels(bots: List[Tuple[int, TelegramBot]], members_file="members.csv"):
    """
    Coordinates member addition across multiple bots
    """
    try:
        members = read_csv_file(members_file)
        total_members = count_rows_in_csv(members_file)
        print(f"{Fore.CYAN}[+] Total members in CSV: {total_members}{Style.RESET_ALL}")
        
        if not members:
            print(f"{Fore.YELLOW}[!] No members found in the CSV file.{Style.RESET_ALL}")
            return
            
        if not bots:
            print(f"{Fore.RED}[!] No bots available.{Style.RESET_ALL}")
            return

        all_failed_members = []
        for index, bot in bots:
            print(f"\n{Fore.CYAN}[+] Bot {index} starting member addition process{Style.RESET_ALL}")
            
            try:
                current_members = read_csv_file(members_file)
                if not current_members:
                    print(f"{Fore.YELLOW}[!] No more members left to process.{Style.RESET_ALL}")
                    break
                    
                channel_info = await bot.choose_channel()
                if not channel_info:
                    print(f"{Fore.RED}[!] No channel selected for bot {index}. Skipping.{Style.RESET_ALL}")
                    continue

                failed_members = await bot.add_users_to_channel(
                    channel_info['target_channel_entity'],
                    channel_info['target_channel'],
                    current_members
                )
                if failed_members:
                    all_failed_members.extend(failed_members)
                
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"{Fore.RED}[!] Error with bot {index}: {str(e)}{Style.RESET_ALL}")
                continue

        if all_failed_members:
            failed_file = "failed_members.csv"
            write_members_to_csv(all_failed_members, "Failed Users", filename=failed_file)
            print(f"{Fore.YELLOW}[+] Failed additions saved to {failed_file}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] Error in member addition process: {str(e)}{Style.RESET_ALL}")


async def all_bots_scrape_members(bots: List[Tuple[int, TelegramBot]]):
    if not bots:
        print("[!] No bots available.")
        return

    await print_all_bots_chat(bots)

    bot_index = eval_input("Please choose bots to scrape (enter number): ", 0, len(bots) + 1, 1)

    bot = bots[bot_index - 1][1]
    chosen_group = await bot.choose_group()
    target_group = chosen_group['target_group']

    print(f"Bot {bot_index} is scraping.")
    await bot.scrape_members(target_group)
    return

async def bots_leave_all_groups(bots: List[Tuple[int, 'TelegramBot']]):
    """Process multiple bots leaving groups."""
    for index, bot in bots:
        print(f"Bot {index} is attempting to leave all groups and channels...")
        await bot.leave_all_groups()
        # Add delay between bots
        await asyncio.sleep(2)


async def bots_forwards_to_saved(bots: List[Tuple[int, TelegramBot]]):
    if not bots:
        print("[!] No bots available.")
        return

    option = input("1. Forward with credits\n2. Forward with no credits\nChoose an option: ")

    if option == "1":
        for index, bot in bots:
            await print_all_bots_info(bots)
            bot_index = eval_input("Please choose bots to forward (enter number): ", 0, len(bots) + 1, 1)

            bot = bots[bot_index - 1][1]
            chosen_group = await bot.choose_group()
            target_group = chosen_group['target_group']
            print(f"Bot {index} is forwarding messages with credits.")
            await bot.show_last_five_messages(target_group)

    elif option == "2":
        for index, bot in bots:
            await print_all_bots_info(bots)
            bot_index = eval_input("Please choose bots to forward (enter number): ", 0, len(bots) + 1, 1)

            bot = bots[bot_index - 1][1]
            chosen_group = await bot.choose_group()
            target_group = chosen_group['target_group']

            print(f"Bot {index} is forwarding messages without credits.")
            messages = await bot.show_last_five_messages(target_group)

            # Check that messages were retrieved
            if not messages:
                print(f"[!] No messages found in the selected group.")
                continue

            # Iterate over messages and send content as new messages without sender credits
            for message in messages:
                try:
                    if message.text:
                        # Send as a new message without sender's name
                        await bot.send_message("me", message.text)
                    elif message.photo:
                        # Send photo without original sender info
                        await bot.send_photo("me", message.photo.file_id, caption=message.caption)
                    elif message.document:
                        # Send document without original sender info
                        await bot.send_document("me", message.document.file_id, caption=message.caption)
                    else:
                        print(f"[!] Unsupported message type: {message}")
                
                except Exception as e:
                    print(f"[!] Error forwarding message: {e}")
        
    else:
        print("[!] Invalid option. Please choose 1 or 2.")


async def all_bot_removed_saved_messages(bots: List[Tuple[int, TelegramBot]]):
    if not bots:
        print("[!] No bots available to remove saved messages.")
        return

    for index, bot in bots:
        try:
            print(f"Bot {index} is removing saved messages...")
            await bot.remove_all_saved_messages()
            print(f"Successfully removed saved messages for Bot {index}.")
        except Exception as e:
            print(f"Failed to remove saved messages for Bot {index}: {str(e)}")
    
    print("Finished removing saved messages for all bots.")


async def all_bots_log_out(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print(f"Bot {index} has logged out.")
        await bot.log_out()
    return

async def clean_members():
    os.remove('members.csv')
    print(f"{Fore.GREEN}[+]Delete members.csv sucessfully")
    return

async def exit_program():
    exit_the_program()

async def all_bots_check_spam(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print(f"{Fore.LIGHTGREEN_EX}Bot {index} is checking spam.")
        await bot.check_spam()

async def all_bot_update_firstname(bots: List[Tuple[int, TelegramBot]], excel_file_path: str):
    if not bots:
        print(f"{Fore.RED}[!] No bots available.")
        return
    
    try:
        # Read the Excel file
        df = pd.read_csv(excel_file_path)
        
        # Check if the Excel file has 'first_name' column
        if 'first_name' not in df.columns:
            print(f"{Fore.RED}Error: Excel file must have 'first_name' column.")
            return
        
        # Ensure we have enough names for all bots
        if len(df) < len(bots):
            print(f"{Fore.YELLOW}[!] Warning: Not enough names for all bots. Will cycle through names.")
        
        # Iterate through bots and names
        for i, (bot_id, bot) in enumerate(bots):
            # Use modulo to cycle through names if not enough
            first_name = df.iloc[i % len(df)]['first_name']
            
            try:
                # Update profile for each bot
                await bot.client(UpdateProfileRequest(first_name=first_name))
                print(f"{Fore.BLUE}[+] Bot {bot_id} name updated to :{Fore.LIGHTGREEN_EX}{first_name}")
            except Exception as e:
                print(f"{Fore.RED}Error updating name for Bot {bot_id}: {str(e)}")
        
        print(f"{Fore.CYAN}Finished updating names for all bots.")
    
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Excel file not found at {excel_file_path}")
    except pd.errors.EmptyDataError:
        print(f"{Fore.RED}Error: The Excel file is empty.")
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}")


async def all_bot_change_name(bots: List[Tuple[int, TelegramBot]]): 
    if not bots:
        print("[!] No bots available.")
        return

    await print_all_bots_info(bots)

    print(f"""
    {Fore.BLUE}1. Change first name & last name  
    {Fore.LIGHTGREEN_EX}2. Change bot usernmae
    {Fore.MAGENTA}3. All bot remove username
    {Fore.GREEN}4. All bot auto setup bio
    {Fore.LIGHTWHITE_EX}5. All bot disallowed call and invite group (Nobody)
    {Fore.LIGHTYELLOW_EX}6. Upload profile image from url

""")
    option_selection = input("Input option: ")

    if option_selection == '1':
        bot_index = eval_input("Please choose bot to change: ", 0, len(bots) + 1, 1)
        bot = bots[bot_index - 1][1]
        await bot.update_name()
    elif option_selection == '2':
        bot_index = eval_input("Please choose bot to change: ", 0, len(bots) + 1, 1)
        bot = bots[bot_index - 1][1]
        await bot.update_username()
    elif option_selection == '3':
        for index, bot in bots:
            await bot.remove_all_bot_username()  
    elif option_selection == '4':
        for index, bot in bots:
            await bot.update_bot_bio()  
            print(f"{Fore.GREEN}[+] Bot {index} updated bio")    
    elif option_selection == '5':
        for index, bot in bots:
            await bot.update_privacy_settings()  
            print(f"{Fore.GREEN}[+] Bot {index} disallowed call and invite group")  
    elif option_selection == '6':
        await print_all_bots_info(bots)
        bot_index = eval_input(f"{Fore.GREEN}[+] Input bot account want to upload profile picture :  {Style.RESET_ALL}", 0, len(bots) + 1, 1)
        bot = bots[bot_index - 1][1]
        image_url = input("Enter the URL of the image: ")
        await bot.update_profile_picture_from_url(image_url)
    else: 
        print("Invalid option")

