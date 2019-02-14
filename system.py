import asyncio
from helpers import *


class System:

    current_supply_offset = 0
    lock_blocks = False
    bp_reward_graph = None

    def __init__(self,
                 total_supply,
                 premine,
                 min_supply_points,
                 block_time_in_seconds,
                 daily_blocks,
                 block_reward_percent,
                 minimal_block_reward):

        self.total_supply = total_supply
        self.premine = premine
        self.circulating_tokens = premine
        self.min_supply_points = min_supply_points
        self.block_time = block_time_in_seconds
        self.daily_blocks = daily_blocks
        self.block_reward = block_reward_percent
        self.minimal_block_reward = minimal_block_reward
        self.total_bp_supply = 0
        self.bp_reward_graph = list()

        self.platforms = list()
        self.parabola = get_parabola(min_supply_points, total_supply)
        print("Parabola a, b, c", self.parabola)
        self.block_number = 0
        self.day_number = 0
        self.set_current_supply_offset()

    def set_current_supply_offset(self):
        self.current_supply_offset = solve_quadratic_equation(self.parabola[0],
                                                              self.parabola[1],
                                                              self.circulating_tokens)[1]

    def calc_platform_round_supply(self, platform):
        assert platform.__class__.__name__ == "Platform", "`platform` has to be a valid Platform instance!"
        if (self.block_number - platform.last_round_block_number) / self.daily_blocks < platform.scoring_round_time:
            self.lock_blocks = False
            raise Exception(platform.name +
                            " has to wait for supply for " +
                            str(platform.scoring_round_time * self.daily_blocks -
                                self.block_number +
                                platform.last_round_block_number) +
                            " blocks")

        # offset_of_this_round = self.block_number - platform.last_round_block_number

        offset_of_this_round = 0
        for p in self.platforms:
            if p.scoring_round_time > offset_of_this_round:
                offset_of_this_round = p.scoring_round_time

        if self.current_supply_offset + offset_of_this_round > self.min_supply_points:
            total_supply_for_round = self.total_supply - self.circulating_tokens
        else:
            total_supply_for_round = \
                self.total_supply - \
                self.circulating_tokens - \
                calc_parabola(self.parabola[0],
                              self.parabola[1],
                              self.parabola[2],
                              self.current_supply_offset + offset_of_this_round)

        print("toal_round_supply", total_supply_for_round)

        return total_supply_for_round * platform.share_of_supply * platform.scoring_round_time / offset_of_this_round

    async def register_platform(self, platform):
        assert platform.__class__.__name__ == "Platform", "`platform` have to be a valid Platform instance!"

        while self.lock_blocks:
            await asyncio.sleep(self.block_time / 10)

        self.lock_blocks = True
        self.platforms.append(platform)
        platform.system = self
        self.lock_blocks = False

    async def run(self):
        while True:
            await self.produce_block()
            if self.circulating_tokens >= self.total_supply - 1e9:
                print("\n## System stopped ##\n")
                print(self.block_number / self.daily_blocks, "days passed")
                for platform in self.platforms:
                    print(platform.name, platform.total_emitted, platform.total_emitted / self.circulating_tokens)
                print("Premine", self.premine, self.premine / self.circulating_tokens)
                print("Total BP supply", self.total_bp_supply, self.total_bp_supply / self.circulating_tokens)
                break

    async def produce_block(self):
        await asyncio.sleep(self.block_time)
        while self.lock_blocks:
            await asyncio.sleep(self.block_time / 10)
        self.block_number += 1

        # Add BP rewards
        block_reward = self.block_reward * (self.total_supply - self.circulating_tokens)
        if block_reward < self.minimal_block_reward:
            block_reward = self.minimal_block_reward
        self.circulating_tokens += block_reward
        self.total_bp_supply += block_reward

        if self.block_number / self.daily_blocks - 1 > self.day_number:
            self.day_number += 1

            # Add BP rewards and registered users graphs
            for platform in self.platforms:
                platform.credited_graph.append(platform.total_emitted)
                platform.registered_users_graph.append(platform.registered_users_share)

            self.bp_reward_graph.append(self.total_bp_supply)

    async def get_tokens(self, platform):
        while self.lock_blocks:
            await asyncio.sleep(self.block_time / 10)
        self.lock_blocks = True

        platform_round_supply = self.calc_platform_round_supply(platform)
        tokens_to_credit = platform_round_supply * platform.registered_users_share
        self.circulating_tokens += tokens_to_credit
        self.set_current_supply_offset()

        to_return = tokens_to_credit, self.block_number
        self.lock_blocks = False

        return to_return
