from pathlib import Path

import discord

from dbot_utilities import load_config, schedule_task


class RecurringMessages(discord.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        # Configurable reminders
        for reminder in self.config["reminders"]:
            schedule_task(self.bot, reminder)

        # Hardcoded reminder
        reminder = {
            "message": "I'm hard coded.",
            "recur_on": ["friday", "saturday", "sunday"],
            "time": "12:00:00",
            "channel": 123,
        }
        task = schedule_task(self.bot, reminder)


def setup(bot):
    config = load_config(Path(__file__).parent.joinpath("config.toml"))
    bot.add_cog(RecurringMessages(bot, config))
