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
