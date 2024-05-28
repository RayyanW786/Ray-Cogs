"""
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
"""

from __future__ import annotations

import discord
from discord.ui import View, Button
from typing import TYPE_CHECKING, Optional, Dict, Literal
from datetime import datetime, timedelta
import asyncio
from random import randint

if TYPE_CHECKING:
    from utils.context import Context


class FastClickButton(Button):
    def __init__(
            self,
            style: discord.ButtonStyle,
            label: str,
    ):
        super().__init__(
            style=style,
            label=label,
        )

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: FastClickView = self.view
        if view.ended or view.is_finished():
            await interaction.response.send_message(f"This Fastclick game is currently ending...", ephemeral=True)

            return
        if interaction.user.id in view.record:
            await interaction.response.send_message("Your response has already been recorded", ephemeral=True)
            return
        value = self.label == 'This one'
        if not value:
            await view.on_wrong_click(interaction)
            return
        view.record[interaction.user.id] = discord.utils.utcnow()
        await interaction.response.send_message(f"Your response has been recorded!", ephemeral=True)


class FastClickView(View):
    def __init__(self, ctx: Context, against: discord.Member) -> None:
        super().__init__()
        self.ctx: Context = ctx
        self.against: discord.Member = against
        self.message: Optional[discord.Message] = None
        self.message_edited_at: Optional[datetime] = None
        self.record: Dict[int, datetime] = {}
        self.listen_until: Optional[datetime] = None
        self.ended: Optional[bool] = False
        self.winner: Optional[int | str] = None
        choice = randint(0, 4)
        for x in range(5):
            if x == choice:
                self.add_item(FastClickButton(
                    discord.ButtonStyle.green,
                    "This one"
                ))
            else:
                self.add_item(FastClickButton(
                    discord.ButtonStyle.gray,
                    "Not this"
                ))

    async def on_wrong_click(self, inter: discord.Interaction) -> None:
        self.stop()
        self.ended = None
        won = self.against
        if inter.user.id != self.ctx.author.id:
            won = self.ctx.author
        await inter.response.send_message("Better luck next time!", ephemeral=True)
        await self.message.edit(
            content=f"Congratulations {won.mention} you have won!\n{inter.user.mention} Clicked the wrong button!",
            view=None,
            embed=None,
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    def calculate_record(self, person: int, _type: Literal['draw'] | bool) -> str:
        if person in self.record:
            total_seconds = int((self.record[person] - self.message_edited_at).total_seconds() * 1000)
            if _type is True:
                return f"<@{person}> won and took {total_seconds:,}ms 🥇"
            elif _type == 'draw':
                return f"<@{person}> drew and took {total_seconds:,}ms 🏆"
            else:
                return f"<@{person}> lost and took {total_seconds:,}ms 🥈"
        else:
            return f"<@{person}> did not finish in time ❌"

    async def end(self) -> None:
        self.ended = True
        local_winner = None
        for _id in self.record:
            if local_winner is None:
                local_winner = [_id, self.record[_id]]
                self.winner = _id
            else:
                if local_winner[1] == self.record[_id]:
                    self.winner = 'draw'
                elif local_winner[1] > self.record[_id]:
                    self.winner = _id

        author = self.calculate_record(
            self.ctx.author.id,
            self.winner == self.ctx.author.id if self.winner != 'draw' else self.winner
        )
        against = self.calculate_record(
            self.against.id,
            self.winner == self.against.id if self.winner != 'draw' else self.winner
        )
        if self.against.id == self.winner:
            fmt = [against, author]
        else:
            fmt = [author, against]

        await self.message.edit(
            content="\n".join(fmt),
            allowed_mentions=discord.AllowedMentions(users=True),
            view=None,
            embed=None
        )

    async def listen(self) -> None:
        self.listen_until = self.message_edited_at + timedelta(seconds=2)
        while self.listen_until and self.listen_until > discord.utils.utcnow() and not self.ended:
            if len(self.record) == 2:
                self.stop()
                await self.end()
                break
            else:
                await asyncio.sleep(0.2)
        else:
            if self.ended is not None:
                await self.end()

    async def setup(self) -> None:
        embed = discord.Embed(
            title="FastClick",
            description=(
                f"{self.ctx.author.mention} & {self.against.mention} get ready for a game of FastClick!\n"
                "- The buttons will appear shortly [random duration]"
            ),
            colour=discord.Colour.blurple(),
        )
        message = await self.ctx.send(embed=embed)
        self.message = message
        await asyncio.sleep(randint(1, 7))
        message = await message.edit(view=self)
        self.message_edited_at = message.edited_at
        if not self.message_edited_at:
            self.message_edited_at = discord.utils.utcnow()
        await self.listen()
