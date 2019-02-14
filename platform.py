import asyncio
from helpers import *


class Platform:

    system = None
    registered_users_graph = None

    def __init__(self,
                 name,
                 share_of_supply,
                 scoring_round_time_in_days,
                 max_part_of_registered_attention=1,
                 growth_speed=1):
        self.name = name
        self.share_of_supply = share_of_supply
        self.scoring_round_time = scoring_round_time_in_days
        self.max_registered = max_part_of_registered_attention
        self.growth_speed = growth_speed

        self.registered_users_share = 0
        self.registered_users_graph = list()

        self.total_emitted = 0
        self.last_round_block_number = 0
        self.current_scoring_round_number = 0

        self.credited_graph = list()

    async def score_rounds(self):
        while True:

            print("\n")
            print(self.name, "is collecting new round...")
            await asyncio.sleep(self.scoring_round_time * self.system.block_time * self.system.daily_blocks)

            print(self.name, "is scoring round...")
            while True:
                try:
                    score_round = await self.system.get_tokens(self)
                    break
                except Exception as e:
                    print(e)
                    await asyncio.sleep(self.system.block_time)

            self.total_emitted += score_round[0]
            self.last_round_block_number = score_round[1]
            self.current_scoring_round_number += 1

            print(self.name, "emitted", score_round[0])
            print(self.name, "last round block number", score_round[1])
            print(self.name, "registered users share", self.registered_users_share)
            print(self.name, "scoring round number", self.current_scoring_round_number)
            print("Circulating tokens =", self.system.circulating_tokens)

    async def new_users_are_coming(self):
        while True:
            self.registered_users_share = \
                sigmoid(self.system.block_number / self.system.daily_blocks / 100 - 10 / self.growth_speed) * \
                self.max_registered

            await asyncio.sleep(self.system.block_time)
