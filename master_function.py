import asyncio
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
    for index, bot in bots:
        user_info = f"Account name : {bot.me.first_name} {bot.me.last_name if bot.me.last_name else ''}"
        print(index, user_info)
    return


async def print_bot_chat(bot: TelegramBot):
    await bot.print_chat()
    return


async def print_all_bots_chat(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print("Chat From Bot", index)
        await print_bot_chat(bot)
    return


async def all_bots_forward(bots: List[Tuple[int, TelegramBot]]):
    limit = eval_input("How many messages? (Default=1): ", 0, 100, 1)
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