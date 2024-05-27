MIT License

Copyright (c) 2024 Rayyan Warraich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

from __future__ import annotations

import discord
from discord.ext import commands
from typing import TYPE_CHECKING
from utils.checks import custom_check  # this is my own enable / disable system 
from discord.app_commands import guild_only
from .views import FastClickView

if TYPE_CHECKING:
    from bot import PhantomGuard
    from utils.context import Context


class Fun(commands.Cog):
    """ Fun commands """

    def __init__(self, bot: PhantomGuard) -> None:
        self.bot: PhantomGuard = bot

    @guild_only()
    @custom_check()
    @commands.hybrid_command(name="fastclick")
    async def fastclick(self, ctx: Context, against: discord.Member) -> None:
        """ Play a game of Fastclick against another user.
            Fastclick is a game which based of your reaction time will decide weather you win or loose!
            5 Buttons are shown, where you must click the green one as fast as you possibly can.
            Clicking on the wrong button will lead to an automatic loss.
         """
        if ctx.author.id == against.id:
            await ctx.reply("You cannot play against yourself lol", ephemeral=True)
            return
        if against.bot:
            await ctx.reply("You cannot play against a bot...", ephemeral=True)
            return

        value = await ctx.prompt(
            (
                f"{against.mention}, {ctx.author.mention} challenges you to a game of Fastclick!\n"
                f"Press Confirm to continue."
            ),
            author_id=against.id,
            am=discord.AllowedMentions(users=[against]),
            ephemeral=True
        )
        if not value:
            await ctx.reply(f"{against.mention} has declined your request for a game of Fastclick!")
            return

        view = FastClickView(ctx, against)
        await view.setup()
