from misc import exit_the_program, read_csv_file, write_members_to_csv, eval_input


async def print_bot_info(bot):
    user_info = f"Account name : {bot.me.first_name} {bot.me.last_name if bot.me.last_name else ''}"
    print(user_info)
    return


async def print_all_bots_info(bots):
    for index, bot in bots:
        user_info = f"Account name : {bot.me.first_name} {bot.me.last_name if bot.me.last_name else ''}"
        print(index, user_info)
    return


async def print_bot_chat(bot):
    await bot.print_chat()
    return


async def print_all_bots_chat(bots):
    for index, bot in bots:
        print("Chat From Bot", index)
        await print_bot_chat(bot)
    return


async def all_bots_forward(bots):
    limit = eval_input("How many messages? (Default=1): ", 0, 100, 1)
    print(f"Send {limit} messages to each group.")

    for index, bot in bots:
        print("Forwarding from Bot", index)
        await bot.forward_message_to_all_groups(limit)
    return


async def all_bots_add_members(bots, limit_per_bot=10, members_file="members.csv"):
    members = read_csv_file(members_file)

    chunks = [members[i:i + limit_per_bot]
              for i in range(0, len(members), limit_per_bot)]

    if not bots:
        print("[!] No bots available.")
        return

    target_group_entity = await bots[0][1].choose_group()['target_group_entity']

    remaining_members = []
    for i, chunk in enumerate(chunks):
        bot_index = i % len(bots)
        index, bot = bots[bot_index]
        print(f"Bot {index} is adding member.")
        try:
            for user in chunk:
                await bot.add_U2G(target_group_entity, user)
        except Exception as e:
            print(f"Error adding members with bot {bot_index}: {e}")
            remaining_members.extend(chunk)

    if remaining_members:
        remaining_file = "remaining_members.csv"
        write_members_to_csv(remaining_members, "Remaining Users",
                             0, filename=remaining_file, mode='w')
        print(f"Remaining members written to {remaining_file}")

    return


async def all_bots_scrape_members(bots):
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


async def all_bots_log_out(bots):
    for index, bot in bots:
        print(f"Bot {index} has logged out.")
        await bot.log_out()
    return


async def exit_program():
    exit_the_program()
