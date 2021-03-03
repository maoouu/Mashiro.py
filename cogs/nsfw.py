import asyncio
import discord

from discord.ext import commands
from hentai import Hentai, Format, Sort, Utils
from utils import default


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.alex_api_token = self.config["alexflipnote_api"]

    @commands.command(aliases=['sc'])
    async def sauce(self, ctx, nuke_code):
        """ What's behind that nuke code? """
        message = await ctx.send("Extracting sauce from nuke code... 👨‍💻")

        if Hentai.exists(nuke_code):
            doujin = Hentai(nuke_code)
            english = doujin.title()
            japanese = doujin.title(Format.Japanese)
            pages = str(len(doujin.pages))
            link = "||" + Hentai._URL + nuke_code + "||"
            tag = [getattr(i, 'name') for i in doujin.tag]
            content_list = [
                f'**Thumbnail**: {doujin.thumbnail}',
                f'** English Title**: {english if english else "none"}',
                f'**Japanese Title**: {japanese if japanese else "none"}',
                f'**Pages**: {pages}',
                f'**Tags**: {", ".join(tag)}',
                f'**Link**: {link}'
            ]
            await message.edit(content="\n".join(content_list))
        else:
            await message.edit(content="The sauce you are looking for does not exist. 🤷‍♂️")

    @commands.command(aliases=["rs", "rdmsauce"])
    async def randomsauce(self, ctx):
        """ Get a random sauce for shits and giggles """
        await ctx.send("Getting a random sauce...")
        await self.sauce(ctx, nuke_code=str(Utils.get_random_id()))

    @commands.command(aliases=["rn", "rdmnuke"])
    async def randomnuke(self, ctx, items: int):
        """ Get random nuke codes for shits and giggles. (Max limit is configurable) """
        message = await ctx.send(f"Gathering [{items}] nuke code/s...")

        if 1 <= items <= self.config["max_limit"]:
            nukes = [str(Utils.get_random_id()) for i in range(items)]
            await message.edit(content=f'Here you go: `{", ".join(nukes)}`')
        else:
            await message.edit(content=f'Cannot generate [{items}] amount of nuke codes.')

    @commands.command(aliases=[''])
    async def read(self, ctx, nuke_code):
        """ Read doujin here on Discord. """
        message = await ctx.send("Loading sauce...")

        if Hentai.exists(nuke_code):
            doujin = Hentai(nuke_code)
            buttons = ["⏪", "◀", "⏹", "▶", "⏩"]
            current = 0
            await message.edit(content=f'Opening *{doujin.title(Format.Pretty)}*...')
            view = await ctx.send(content=doujin.image_urls[current])
            page_info = await ctx.send(content=f'Page: {str(current + 1)}/{str(len(doujin.pages))}')

            for button in buttons:
                await view.add_reaction(button)

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0, check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons)

                except asyncio.TimeoutError:
                    await view.edit(content="**Message Timed Out.**")
                    await page_info.delete()
                    break

                else:
                    previous_page = current

                    def flip_page(current, emoji):
                        switcher = {
                            "⏪": 0,
                            "◀": current - 1 if current > 0 else current,
                            "⏹": -1,
                            "▶": current + 1 if current < len(doujin.pages) - 1 else current,
                            "⏩": len(doujin.pages) - 1
                        }
                        return switcher.get(emoji, current)

                    current = flip_page(current, reaction.emoji)

                    if current != previous_page:
                        if current is -1:
                            await view.edit(content="**Doujin has been closed.**")
                            await page_info.delete()
                            break
                        else:
                            for button in buttons:
                                await view.add_reaction(button)
                            await view.edit(content=doujin.image_urls[current])
                            await page_info.edit(content=f'Page: {str(current + 1)}/{str(len(doujin.pages))}')

        else:
            await message.edit(content="The sauce you want to read does not exist. 🤷‍♂️")

    @commands.command(aliases=["gs"])
    async def getsauce(self, ctx, *, query):
        """ Fetches the first 25 nuke codes that match this query """
        message = await ctx.send(f'Fetching *"{query}"*...')
        query = query.strip().split()
        nukes = [str(doujin.id) for doujin in Utils.search_by_query(
            query, sort=Sort.PopularWeek)]

        await message.edit(content=f'Here you go: `{", ".join(nukes)}`')


def setup(bot):
    bot.add_cog(NSFW(bot))
