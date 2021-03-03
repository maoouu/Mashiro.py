import asyncio
from discord.ext import commands
from hentai import Hentai, Format, Sort, Utils
from requests.models import HTTPError
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
            pages = str(doujin.num_pages)
            hentai_id = str(doujin.id)
            link = "||" + doujin.url + "||"
            tag = (getattr(i, 'name') for i in doujin.tag)
            content_list = (
                f'**Hentai ID**: {hentai_id}',
                f'**Thumbnail**: {doujin.thumbnail}',
                f'** English Title**: {english if english else "none"}',
                f'**Japanese Title**: {japanese if japanese else "none"}',
                f'**Pages**: {pages}',
                f'**Tags**: {", ".join(tag)}',
                f'**Link**: {link}'
            )
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
            nukes = (str(Utils.get_random_id()) for i in range(items))
            await message.edit(content=f'Here you go: `{", ".join(nukes)}`')
        else:
            await message.edit(content=f'Cannot generate [{items}] amount of nuke codes.')

    @commands.command()
    async def read(self, ctx, nuke_code):
        """ Read doujin here on Discord. """
        message = await ctx.send("Loading sauce...")

        if Hentai.exists(nuke_code):
            doujin = Hentai(nuke_code)
            buttons = ("⏪", "◀", "⏹", "▶", "⏩")
            current = 0
            images = tuple(doujin.image_urls)
            max_pages = doujin.num_pages
            await message.edit(content=f'Opening *{doujin.title(Format.Pretty)}*...')
            view = await ctx.send(images[current])
            page_info = await ctx.send(f'Page: {str(current + 1)}/{str(max_pages)}')

            for button in buttons:
                await view.add_reaction(button)

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=90.0, check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons)
                except asyncio.TimeoutError:
                    await view.edit(content="**Doujin has timed out.**")
                    del images
                    await page_info.delete()
                    break
                else:
                    previous_page = current
                    switcher = {
                        "⏪": 0,
                        "◀": current - 1 if current > 0 else current,
                        "⏹": -1,
                        "▶": current + 1 if current < max_pages - 1 else current,
                        "⏩": max_pages - 1
                    }
                    current = switcher[reaction.emoji]
                    if current != previous_page:
                        if current == -1:
                            await view.edit(content="**Doujin has been closed.**")
                            del images
                            await page_info.delete()
                            break
                        else:
                            await view.edit(content=images[current])
                            await page_info.edit(content=f'Page: {str(current + 1)}/{str(max_pages)}')
        else:
            await message.edit(content="The sauce you want to read does not exist. 🤷‍♂️")

    @commands.command(aliases=["gs"])
    async def getsauce(self, ctx, flag, *query):
        """ Fetches the first 25 nuke codes that match this query 

            [Sorting Flags]
            -a = Popular all-time 
            -y = Popular this year
            -w = Popular this week (default)
            -m = Popular this month
            -t = Popular today
            -r = Most Recent
        """
        category = {
            "-a": [Sort.Popular, "popular all-time"],
            "-y": [Sort.PopularYear, "popular this year"],
            "-w": [Sort.PopularWeek, "popular this week"],
            "-m": [Sort.PopularMonth, "popular this month"],
            "-t": [Sort.PopularToday, "popular today"],
            "-r": [Sort.Date, "most recent"]
        }
        default = [Sort.PopularWeek, "popular this week"]
        new_query = flag  # in case flag is a query
        flag = flag if flag in category else None
        try:
            sort_by = category.get(flag, default)
            if flag == None:
                new_query = new_query + " " + " ".join(query)
            else:
                new_query = " ".join(query)
            message = await ctx.send(f'Fetching *"{new_query}"*...')
            nukes = (str(doujin.id) for doujin in Utils.search_by_query(
                new_query, sort=sort_by[0]))
            await message.edit(content=f'Here you go ({sort_by[1]}): `{", ".join(nukes)}`')
        except HTTPError:
            await message.edit(content=f"Couldn't find the sauce you're looking for. 🤷‍♂️")


def setup(bot):
    bot.add_cog(NSFW(bot))
