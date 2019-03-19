import asyncio
from helpers import *
from system import System
from platform import Platform


# Init system and platforms
system = System(total_supply=100_000_000_000,
                premine=16_000_000_000,
                min_supply_points=151,
                block_time_in_seconds=.005,
                daily_blocks=24 * 3600 * 2,
                block_reward_percent=5e-10,
                minimal_block_reward=4,
                blockchain_speedup_multiplier=100_000)

steemit = Platform("Steemit",
                   share_of_supply=.005,
                   scoring_round_time_in_days=1,
                   max_part_of_registered_attention=.8,
                   growth_speed=2)

twitter = Platform("Twitter",
                   share_of_supply=.995,
                   scoring_round_time_in_days=2,
                   max_part_of_registered_attention=.01,
                   growth_speed=.75)


# Register platforms
el = asyncio.get_event_loop()
el.run_until_complete(system.register_platform(steemit))
el.run_until_complete(system.register_platform(twitter))

# Run scoring rounds
asyncio.ensure_future(twitter.score_rounds(), loop=el)
asyncio.ensure_future(steemit.score_rounds(), loop=el)

# Run users registration
asyncio.ensure_future(twitter.new_users_are_coming(), loop=el)
asyncio.ensure_future(steemit.new_users_are_coming(), loop=el)

# Run blockchain
el.run_until_complete(system.run())


import matplotlib.pyplot as plot
from numpy import vectorize
import numpy as np


# Show supply parabola
x = np.linspace(0, 151, num=1000)
plot.plot(x, vectorize(calc_parabola)(system.parabola[0], system.parabola[1], system.parabola[2], x))
plot.title("Rest of the SNAX supply")
plot.show()


# Show block reward graph
x = np.linspace(1, len(system.block_reward_graph) + 1, num=len(system.block_reward_graph))
plot.plot(x, system.block_reward_graph, label="SNAX per 1 block")
plot.title("Block reward")
plot.legend()
plot.show()


# Show users growth
x = np.linspace(1, len(twitter.credited_graph) + 1, num=len(twitter.credited_graph))
plot.plot(x, steemit.registered_users_graph, label=steemit.name)
plot.plot(x, twitter.registered_users_graph, label=twitter.name)
plot.yscale("log")
plot.title("Registered users share of the whole platform")
plot.legend()
plot.show()


# Show supply growth
x = np.linspace(1, len(twitter.credited_graph) + 1, num=len(twitter.credited_graph))
plot.plot(x, steemit.credited_graph, label=steemit.name)
plot.plot(x, twitter.credited_graph, label=twitter.name)
plot.plot(x, system.bp_reward_graph, label="BP supply")
plot.title("Total supply emitted by platform")
plot.legend()
plot.show()
