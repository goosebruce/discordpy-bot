import os
import discord
from discord.ext import commands

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse

from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Text
from discord import Interaction
from discord.ext.commands import is_owner, Context

from events import basic_groups, pro_groups, private_groups


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix="!")


# if slash command isn't in a cog
@client.tree.command(
    description="Shows the server rules"
)  # removed the name param because it will raise an error as it is the same that the async function
async def rules(interaction: discord.Interaction) -> None:
    rules = (
        "1. Don't say bad words",
        "2. Respect other people",
        "3. You mustn't speak loud in voice channels",
    )
    await interaction.response.send_message(f"{rules}")


@client.command()
@is_owner()
async def sync(ctx: Context) -> None:
    synced = await client.tree.sync()
    await ctx.reply("{} commands synced".format(len(synced)))


@client.event
async def on_ready():
    print("Bot is ready")


@client.event
async def on_member_update(before, after):
    basic_role = discord.utils.get(after.guild.roles, name="Basic")
    pro_role = discord.utils.get(after.guild.roles, name="Pro")
    private_role = discord.utils.get(after.guild.roles, name="Private")
    if (basic_role in after.roles and basic_role not in before.roles) or (
        basic_role in before.roles and basic_role not in after.roles
    ):
        await basic_groups.handle_basic_role_change(before, after)
    elif (pro_role in after.roles and pro_role not in before.roles) or (
        pro_role in before.roles and pro_role not in after.roles
    ):
        await pro_groups.handle_pro_role_change(before, after)
    elif (private_role in after.roles and private_role not in before.roles) or (
        private_role in before.roles and private_role not in after.roles
    ):
        await private_groups.handle_private_role_change(before, after)
    else:
        print("No notable role changed")


client.run(os.environ["DISCORD_TOKEN"])
