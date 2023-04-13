import json
import discord
import aiohttp
import os

with open("config.json") as f:
    config = json.load(f)


async def add_pro_group_channel(member, role) -> None:
    channel_name = f"leads-{role.name}"
    id = config["pro_group_category_id"]
    print(member.guild.categories)
    category = discord.utils.get(member.guild.categories, id=id)
    existing_channel = discord.utils.get(category.channels, name=channel_name)
    print(category.channels)
    print(existing_channel)
    if existing_channel is None:
        if role is not None:
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False
                ),
                role: discord.PermissionOverwrite(
                    read_messages=True, send_messages=False
                ),
            }
            new_channel = await category.create_text_channel(
                name=channel_name, overwrites=overwrites
            )
            print(f"New channel: {new_channel} created")
    else:
        print(f"Channel already exists:{channel_name}")


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


async def handle_pro_role_change(before, after) -> None:
    print("member change event triggered")
    print(before.roles)
    print(after.roles)
    pro_role = discord.utils.get(after.roles, name="Pro")
    if pro_role is None:
        # pro role was removed, remove all pro group roles from member
        for role in after.roles:
            if role.name.startswith(config["pro_role_pre"]):
                print(f"Removing {role} from {after}")
                await after.remove_roles(role)
        return

    if pro_role not in before.roles:
        # pro role was added, assign member to pro group
        # Replace this block with the Bubble API call
        api_key = os.environ["bubble_api_key"]
        user_id = str(after.id)
        lead_group = await fetch_lead_group(api_key, user_id)

        if lead_group:
            # Use the lead_group name retrieved from the Bubble API
            role = discord.utils.get(after.guild.roles, name=lead_group)
            if not role:
                # If the role doesn't exist, create it
                role = await after.guild.create_role(
                    name=lead_group, color=discord.Color.random()
                )
                await role.edit(
                    position=after.guild.get_role(after.guild.id).position + 1
                )
                print(f"New role '{lead_group}' created")

            await after.add_roles(role)
            await add_pro_group_channel(after, role)
        else:
            print("Unable to fetch lead group from Bubble API")

    else:
        print("Member already has pro role")
