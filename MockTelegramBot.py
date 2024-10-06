from typing import List, Dict, Any

class Me:
    def __init__(self, idd, username):
        self.first_name = idd
        self.last_name = username

class MockTelegramBot:
    id_counter = 12345
    username = "mockuser"

    def __init__(self, api_id, api_hash, session_file):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_file = session_file
        self.sleep_time = 5
        self.chats = []
        self.groups = []
        self.groups_id = []
        self.me = None
        

    async def start(self):
        print("Mock start method called.")
        self.me = Me(MockTelegramBot.id_counter, MockTelegramBot.username + str(MockTelegramBot.id_counter))
        MockTelegramBot.id_counter += 1

    async def print_chat(self):
        print("Mock print_chat method called.")
        for index, chat in enumerate(self.groups):
            print(f"{index + 1} - {chat['title']} | ID - {chat['id']}")

    async def forward_message_to_group(self, group_id, from_chat_id, message_id):
        print(f"Mock forward_message_to_group called with group_id={group_id}, from_chat_id={from_chat_id}, message_id={message_id}")

    async def forward_message_to_all_groups(self, limit):
        print(f"Mock forward_message_to_all_groups called with limit={limit}")

    async def scrape_members(self, target_group):
        print(f"Mock scrape_members called with target_group={target_group['title']}")

    async def log_out(self):
        print("Mock log_out method called.")
        return True

    async def choose_group(self) -> Dict[str, Any]:
        print("Mock choose_group method called.")
        return {'target_group': {"id": 123, "title": "Mock Group"}, 'target_group_entity': {"id": 123, "access_hash": 456}}

    def __read_csv_file(self, input_file) -> List[Dict[str, Any]]:
        print(f"Mock __read_csv_file called with input_file={input_file}")
        return [{"username": "mock_user", "user_id": 123, "access_hash": 456, "name": "Mock User"}]

    async def add_users_to_group(self, target_group_entity, users, input_file):
        print(f"Mock add_users_to_group called with target_group_entity={target_group_entity}, users={users}, input_file={input_file}")

    async def add_members_to_group(self, input_file):
        print(f"Mock add_members_to_group called with input_file={input_file}")
        await self.add_users_to_group({"id": 123, "access_hash": 456}, self.__read_csv_file(input_file), input_file)

    async def add_U2G(self, target_group_entity, user):
        print(f"Mock add_U2G called with target_group_entity={target_group_entity}, user={user}")