from pathlib import Path

import discord

from dbot_utilities import load_config, schedule_task
from pyumilove.awakenchaosera import Hero, ACE


class AwakenChaosEra(discord.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        # Register all the ACE reset reminders
        try:
            for reminder in self.config["reminders"]:
                schedule_task(self.bot, reminder)
        except:
            # No reminders, skip
            pass

    _embed_colors = {
        "Light": discord.Colour.gold(),
        "Dark": discord.Colour.dark_purple(),
        "Fire": discord.Colour.red(),
        "Wood": discord.Colour.green(),
        "Water": discord.Colour.blue(),
    }

    # Create a command group for this cog, add all commands here to it
    _ace_group = discord.SlashCommandGroup("ace", "Awaken Chaos Era")

    @staticmethod
    def _build_hero_embed(hero: Hero):
        """Build a Discord embed object out of a pyumilove ACE Hero object."""
        embed_color = AwakenChaosEra._embed_colors[hero.element]
        embed_description = "{0} \U00002014 {1} \U00002014 {2} \U00002014 {3}".format(
            hero.rarity, hero.heroType, hero.element, hero.faction
        )

        # Build skills description
        for skill in hero.skills:
            embed_description += "\n\n**{0}**\n{1}".format(
                skill["name"], skill["description"]
            )

        embed = discord.Embed(
            title=hero.name,
            description=embed_description,
            url=hero.url,
            colour=embed_color,
        )

        return embed

    @_ace_group.command(description="Search for a hero. E.g. /ace hero imogen")
    async def hero(self, ctx, name: str):
        """Search for a hero by name and respond with an embed if one is found."""
        print("/ace hero {0} - searching AyumiLove...".format(name), end="")
        async with ACE() as client:
            hero = await client.get_hero(name)

        if hero:
            embed = AwakenChaosEra._build_hero_embed(hero)
            print(" Found " + hero.name)
            await ctx.respond(embed=embed)
        else:
            print(" Not found")
            await ctx.respond("Unable to find '{0}'".format(name))

    @_ace_group.command(description="List of buffs in ACE")
    async def buffs(self, ctx):
        """Return an embed with a list of all buffs."""
        print("/ace buffs - returning list of buffs")
        async with ACE() as client:
            buffs = await client.buffs()

        buffs_str = "".join(
            "[{0}]({1})\n".format(buff_name, buffs[buff_name]) for buff_name in buffs
        ).rstrip()

        embed = discord.Embed(
            title="ACE Buffs",
            description=buffs_str,
        )

        await ctx.respond(embed=embed)

    @_ace_group.command(description="List of debuffs in ACE")
    async def debuffs(self, ctx):
        """Return an embed with a list of all debuffs."""
        print("/ace debuffs - returning list of debuffs")
        async with ACE() as client:
            debuffs = await client.debuffs()

        debuffs_str = "".join(
            "[{0}]({1})\n".format(debuff_name, debuffs[debuff_name])
            for debuff_name in debuffs
        ).rstrip()

        embed = discord.Embed(
            title="ACE Debuffs",
            description=debuffs_str,
        )

        await ctx.respond(embed=embed)


def setup(bot):
    """Required function to load the cog and add it to the Discord bot."""
    config = load_config(Path(__file__).parent.joinpath("config.toml"))
    bot.add_cog(AwakenChaosEra(bot, config))
