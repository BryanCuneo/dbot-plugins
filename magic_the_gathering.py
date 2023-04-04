from pathlib import Path

import discord
import nest_asyncio
import scrython

from dbot_utilities import load_config, schedule_task


# Required for scrython calls to work
nest_asyncio.apply()


class MagicTheGathering(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    _embed_colors = {
        "W": discord.Colour.from_rgb(255, 255, 255),
        "U": discord.Colour.blue(),
        "B": discord.Colour.dark_purple(),
        "R": discord.Colour.red(),
        "G": discord.Colour.green(),
        "colorless": discord.Colour.light_grey(),
        "multicolor": discord.Colour.gold(),
    }

    # Create a command group for this cog, add all commands here to it
    _mtg_group = discord.SlashCommandGroup("mtg", "Magic: The Gathering")

    def _build_card_embed(card: scrython.cards.named.Named):
        """Build a Discord embed object out of a scrython card object."""
        # Determine embed color based on card colors.
        color_count = len(card.color_identity())
        if color_count == 0:
            # colorless card
            embed_color = MagicTheGathering._embed_colors["colorless"]
        elif color_count > 1:
            # multicolor card
            embed_color = MagicTheGathering._embed_colors["multicolor"]
        else:
            # monocolored card
            embed_color = MagicTheGathering._embed_colors[card.color_identity()[0]]

        # Description should be: <mana cost> - <type> - power/toughness
        embed_description = card.type_line()
        try:
            # If the card has a mana cost, add it to the description
            embed_description = "{0} \U00002014 {1}".format(
                card.mana_cost(), embed_description
            )
        except KeyError:
            # Card has no mana cast. Ignore
            pass

        try:
            # If the card has a power and toughness, add it
            embed_description += " \U00002014 [{0}/{1}]".format(
                card.power(), card.toughness()
            )
        except KeyError:
            # Card has no power or toughness. Ignore
            pass

        try:
            embed_description += " \U00002014 \U00002989 {} \U0000298A".format(
                card.loyalty()
            )
        except KeyError:
            # Card has no loyalty. Ignore
            pass

        embed = discord.Embed(
            title=card.name(),
            description=embed_description,
            url=card.scryfall_uri().split("?")[0],
            colour=embed_color,
        )
        # If the card has Oracle text and/or flavor text, add those to the embed
        try:
            if card.oracle_text():
                embed.add_field(
                    name="Oracle Text", value=card.oracle_text(), inline=False
                )
        except:
            # Card has no oracle text. Ignore
            pass

        try:
            if card.flavor_text():
                embed.add_field(
                    name="Flavor Text",
                    value="*{}*".format(card.flavor_text()),
                    inline=False,
                )
        except:
            # Card has no flavor text. Ignore
            pass
        # set the thumbnail image to the card art
        embed.set_thumbnail(url=card.image_uris()["art_crop"])
        # embed.set_image(url=card.image_uris()["small"])
        embed.set_footer(text="\U0001F58C " + card.artist())

        return embed

    @_mtg_group.command(
        description="Search for a card. e.g. /mtg ancestral recall or /mtg smokestack|v14"
    )
    async def card(self, ctx, cardname: str):
        """Fuzzy search for a card by name or name|set.
        https://scryfall.com/docs/api/cards/named
        """
        result = None
        split_cardname = cardname.split("|")
        if len(split_cardname) > 1:
            # User asked for a specific printing of this card
            try:
                print(
                    'MTG: searching for "{0}" in set "{1}"...'.format(*split_cardname),
                    end="",
                )
                card = scrython.cards.Named(
                    fuzzy=split_cardname[0], set=split_cardname[-1]
                )
                print(" Found {0}|{1}".format(card.name(), card.set_code().upper()))
                result = MagicTheGathering._build_card_embed(card)
            except scrython.foundation.ScryfallError:
                # Couldn't find the card in the set, search again by just the name
                print(" Unable to find. Searching again without set.")
        if not result:
            # No printing specified or failed to find the specified printing
            print('MTG: Searching for "{}"...'.format(split_cardname[0]), end="")
            card = scrython.cards.Named(fuzzy=split_cardname[0])
            print(" Found {0}|{1}".format(card.name(), card.set_code().upper()))
            result = MagicTheGathering._build_card_embed(card)

        await ctx.respond(embed=result)

    @_mtg_group.command(description="Show a random card.")
    async def random(self, ctx):
        """Fetch a random card and display it as an embed.
        https://scryfall.com/docs/api/cards/random
        """
        print("MTG: Showing a random card...", end="")
        card = scrython.cards.Random()
        print(" Found {0}|{1}".format(card.name(), card.set_code().upper()))
        await ctx.respond(embed=MagicTheGathering._build_card_embed(card))


def setup(bot):
    bot.add_cog(MagicTheGathering(bot))
