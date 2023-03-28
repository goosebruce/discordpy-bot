import json
import discord

with open("config.json") as f:
    config = json.load(f)


async def add_private_group_channel(member) -> None:
    lead_channel_name = f"{config['priv-leads-removed']}-leads-{member.name}"
    feedback_channel_name = f"{config['priv-leads-removed']}-feedback-{member.name}"
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
