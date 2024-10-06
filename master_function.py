from misc import exit_the_program, read_csv_file, write_members_to_csv, eval_input, remove_duplicates
from typing import List, Tuple
from TelegramBot import TelegramBot


async def print_bot_info(bot: TelegramBot):
    if bot.me is None or not hasattr(bot.me, 'first_name') or not hasattr(bot.me, 'last_name'):
        print("Invalid User?")
        return

    first_name = getattr(bot.me, 'first_name', 'Unknown')
    last_name = getattr(bot.me, 'last_name', '')
    user_info = f"Account name : {first_name} {last_name}"
    print(user_info)
    return


async def print_all_bots_info(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        first_name = getattr(bot.me, 'first_name', 'Unknown')
        last_name = getattr(bot.me, 'last_name', '')
        user_info = f"Account name : {first_name} {last_name}"
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
    limit = eval_input("How many messages? (Default=1, Cancel=0): ", 0, 10, 1)
    if limit == 0:
        print("[!] Cancelled.")
        return
    
    print(f"\nSend {limit} messages to each group.")

    for index, bot in bots:
        print("Forwarding from Bot", index)
        await bot.forward_message_to_all_groups(limit)
    return


async def all_bots_add_members(bots: List[Tuple[int, TelegramBot]], limit_per_bot:int=10, members_file:str="members.csv"):
    if not bots:
        print("[!] No bots available.")
        return
    
    members = read_csv_file(members_file)

    if not members:
        print("[!] No member to add. Please check 'memebers.csv'")
        return

    chunks = [members[i:i + limit_per_bot] for i in range(0, len(members), limit_per_bot)]


    remaining_members = []
    i = 0
    for i, chunk in enumerate(chunks):
        if i >= len(bots):
            # If there are more chunks than bots, treat the remaining chunks as remaining members
            remaining_members.extend(chunk)
            continue

        print("Choose group to scrape from.")
        chosen_group = await bots[i][1].choose_group()
        if not chosen_group:
            return

        target_group = chosen_group['target_group']

        print(f"Bot {i+1} is scraping.")
        await bot.scrape_members(target_group)

        print("Choose group to add user to.")        
        chosen_group = await bots[i][1].choose_group()
        if not chosen_group: 
            return
        
        target_group_entity = chosen_group['target_group_entity']
        print(chosen_group)

        index, bot = bots[i]
        print(f"Bot {index} is adding members.")
        try:
            for user in chunk[:]:
                chunk.remove(user)
                await bot.add_U2G(target_group_entity, user)
        except Exception as e:
            print(f"Error adding members with bot {index}: {e}")
            remaining_members.extend(chunk)
            break  # Stop processing further chunks if an error occurs

    # Add any remaining chunks to the remaining members list
    for remaining_chunk in chunks[i+1:]:
        remaining_members.extend(remaining_chunk)

    if remaining_members:
        remaining_file = members_file
        write_members_to_csv(remaining_members, "Remaining Users", 0, filename=remaining_file)
        print(f"Remaining members written to {remaining_file}")
    else:
        open(members_file, 'w').close()
        print(f"No remaining members. {members_file} has been cleared.")
    return


async def all_bots_scrape_members(bots: List[Tuple[int, TelegramBot]]):
    if not bots:
        print("[!] No bots available.")
        return

    await print_all_bots_chat(bots)

    bot_index = eval_input("Please choose bots to scrape (enter number, Cancel=0): ", 0, len(bots), 0)
    
    if bot_index == 0:
        print("[!] Cancelled.")
        return


    bot = bots[bot_index - 1][1]
    chosen_group = await bot.choose_group()
    if not chosen_group:
        return
    
    target_group = chosen_group['target_group']

    print(f"Bot {bot_index} is scraping.")
    await bot.scrape_members(target_group)
    return


async def bot_clear_group(bot: TelegramBot):
    await bot.clear_group()


async def all_bots_clear_group(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print(f"Bot {index} has cleared groups.")
        await bot_clear_group(bot)


async def all_bots_log_out(bots: List[Tuple[int, TelegramBot]]):
    for index, bot in bots:
        print(f"Bot {index} has logged out.")
        await bot.log_out()
    return

async def clean_members():
    remove_duplicates('members.csv', 'members.csv')

async def exit_program():
    exit_the_program()
