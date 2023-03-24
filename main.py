# This example requires the 'message_content' privileged intents

import os
import discord
from discord.ext import commands
from events import pro_groups

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

pro_groups.client = client


@client.event
async def on_ready():
    print('Bot is ready')


@client.event
async def on_member_update(before, after):
    await pro_groups.handle_pro_role_change(before, after)


@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

client.run(os.environ["DISCORD_TOKEN"])
