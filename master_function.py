import asyncio
from telethon import events
import csv
import os
import random
import sys
from colorama import Fore , Back, Style
from misc import exit_the_program, read_csv_file, write_members_to_csv, eval_input, remove_duplicates , count_rows_in_csv
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
    # Read the CSV file
    try:
        members = read_csv_file(members_file)
        count_rows_in_csv('members.csv')
    except FileNotFoundError:
        print(f"{Fore.RED}[!] File {members_file} not found.{Style.RESET_ALL}")
        return
    except Exception as e:
        print(f"{Fore.RED}[!] Error reading CSV file: {str(e)}{Style.RESET_ALL}")
        return

    if not members:
        print(f"{Fore.YELLOW}[!] No members found in the CSV file.{Style.RESET_ALL}")
        return

    if not bots:
        print(f"{Fore.RED}[!] No bots available.{Style.RESET_ALL}")
        return

    # Distribute members among bots
    members_per_bot = len(members) // len(bots)
    extra_members = len(members) % len(bots)

    start_idx = 0
    all_failed_members = []

    for i, (index, bot) in enumerate(bots):
        # Let each bot choose the target group
        print(f"{Fore.CYAN}Bot {index} is selecting the group to add members to.{Style.RESET_ALL}")
        
        try:
            # Each bot prompts for a group selection
            chosen_group = await bot.choose_group()  # Bot-specific group selection
            target_group_entity = chosen_group['target_group']  # Contains group info like access hash
            
            if not target_group_entity:
                print(f"{Fore.RED}[!] Invalid group entity for bot {index}. Skipping.{Style.RESET_ALL}")
                continue

            # Calculate how many members this bot should handle
            bot_members_count = members_per_bot + (1 if i < extra_members else 0)
            end_idx = start_idx + bot_members_count
            
            bot_members = members[start_idx:end_idx]
            print(f"{Fore.CYAN}Bot {index} is adding {len(bot_members)} users to the selected group.{Style.RESET_ALL}")
            
            # Attempt to add members to the selected group
            failed_members = await bot.add_users_to_group(target_group_entity, bot_members)
            all_failed_members.extend(failed_members)
        
        except Exception as e:
            print(f"{Fore.RED}Error with bot {index}: {e}{Style.RESET_ALL}")
            all_failed_members.extend(bot_members)
        
        start_idx = end_idx

    # Save failed members to a CSV file
    if all_failed_members:
        failed_file = "failed_members.csv"
        write_members_to_csv(all_failed_members, "Failed Users", target_group_entity.id, filename=failed_file)
        print(f"{Fore.YELLOW}[+] Failed additions have been saved to {failed_file}{Style.RESET_ALL}")


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
        await asyncio.sleep(5)


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

