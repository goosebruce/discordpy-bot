import json
import discord
import aiohttp
import os

with open("config.json") as f:
    config = json.load(f)


async def fetch_lead_group(api_key, user_id):
    async with aiohttp.ClientSession() as session:
        url = f"https://app.upsourcelabs.com/version-test/api/1.1/wf/getleadgroup?discord_id={user_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(data["response"]["lead group"])
                return data["response"]["lead group"]

            else:
                print(f"Error fetching lead group: {response.status}")
                return None


async def add_private_group_channel(member) -> None:
    api_key = os.environ["bubble_api_key"]
    user_id = str(member.id)
    lead_group = await fetch_lead_group(api_key, user_id)

    lead_channel_name = f"leads - {lead_group}"
    feedback_channel_name = f"feedback-{lead_group}"
    id = config["private_group_category_id"]
    category = discord.utils.get(member.guild.categories, id=id)
    existing_lead_channel = discord.utils.get(category.channels, name=lead_channel_name)
    existing_feedback_channel = discord.utils.get(
        category.channels, name=feedback_channel_name
    )
    if existing_lead_channel is None:
        # make channel that only the user can read but not everyone with the role
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(
                read_messages=True, send_messages=False
            ),
        }
        new_channel = await category.create_text_channel(
            name=lead_channel_name, overwrites=overwrites
        )
        print(f"New channel: {new_channel} created")
    else:
        print(f"Channel already exists:{lead_channel_name}")
    if existing_feedback_channel is None:
        # make channel that only the user can read but not everyone with the role
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        new_channel = await category.create_text_channel(
            name=feedback_channel_name, overwrites=overwrites
        )
        print(f"New channel: {new_channel} created")
    else:
        print(f"Channel already exists:{feedback_channel_name}")


async def handle_private_role_change(before, after) -> None:
    print("member change event triggered")
    private_role = discord.utils.get(after.roles, name="Private")
    if private_role is None:
        # private role was removed, remove all private group roles from member
        for channel in after.guild.channels:
            if channel.name.startswith(config["private_group_pre"]):
                print(f"Removing {channel} from {after}")
                # remove user permissions from the channel and change channel name to "priv-leads-removed"
                await channel.set_permissions(after, overwrite=None)
                await channel.edit(name=config["priv-leads-removed"])
                return
    if private_role not in before.roles:
        await add_private_group_channel(after)
    else:
        print("Member already has private role")
