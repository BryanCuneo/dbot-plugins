import re
from random import randrange

import discord


class DiceRoller(discord.Cog):
    _about_message = """Built with DBot - A plugin-based Discord bot framework
<https://github.com/BryanCuneo/dbot>

Copyright 2018-2022 Bryan Cuneo
https://www.gnu.org/licenses/agpl-3.0.en.html"""
    _dice_pattern = "[1-9]\d*d[1-9]\d*"

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        description="Roll dice with any number of sides. e.g. /roll 6 or /roll 3d8"
    )
    async def roll(self, ctx, dice: str):
        results = "Error: invalid input."

        try:
            # User entered one number: e.g. /roll X
            # Roll one die with X sides
            results = randrange(1, int(dice) + 1)
            print("Rolling a die with {0} sides: {1}".format(dice, results))
        except:
            # User entered multipl dice. e.g. /roll XdY
            # Roll X dice with Y sides
            dice_str = re.search(DiceRoller._dice_pattern, dice)
            if dice_str:
                split = dice_str.group().split("d")
                count = int(split[0])
                sides = int(split[1])

                print("Rolling {0} dice with {1} sides: ".format(count, sides), end="")
                rolls = sorted([randrange(1, sides + 1) for die in range(count)])
                print(rolls)

                total = sum(rolls)
                results = "{0}. **Total:** {1}".format(
                    ", ".join(list(map(str, rolls))), total
                )

        await ctx.respond(results)


def setup(bot):
    bot.add_cog(DiceRoller(bot))
