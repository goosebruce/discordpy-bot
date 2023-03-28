import json
import discord

with open("config.json") as f:
    config = json.load(f)

pro_groups = {}


async def add_pro_group_channel(member, role) -> None:
    channel_name = f"Leads - {role.name}"
    id = 1077796703408762951
    print(member.guild.categories)
    category = discord.utils.get(member.guild.categories, id=id)
    existing_channel = discord.utils.get(category.channels, name=channel_name)
    print(existing_channel)
    if existing_channel is not None:
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


async def handle_pro_role_change(before, after) -> None:
    pro_role = discord.utils.get(after.roles, name="Pro")
    if pro_role is None:
        # Pro role was removed, remove all pro group roles from member
        for role in pro_groups.values():
            if after in role.members:
                await after.remove_roles(role)
                await remove_pro_group_channel(after, role)
        return
    if pro_role not in before.roles:
        # Pro role was added, assign member to pro group
        if "Pro Group" not in [r.name for r in after.roles]:
            pro_group_num = 1
            for role in pro_groups.values():
                if len(role.members) < 5:
                    await after.add_roles(role)
                    await add_pro_group_channel(after, role)
                    return
                else:
                    pro_group_num += 1
            new_role = await after.guild.create_role(
                name=f"Pro Group - {pro_group_num}", color=discord.Color.random()
            )
            await new_role.edit(
                position=after.guild.get_role(after.guild.id).position + 1
            )
            await after.add_roles(new_role)
            pro_groups[new_role.id] = new_role
            await add_pro_group_channel(after, new_role)


async def remove_pro_group_channel(member, role) -> None:
    channel_name = f"Leads - {role.name}"
    existing_channel = discord.utils.get(member.guild.channels, name=channel_name)
    if existing_channel:
        await member.remove_roles(existing_channel)
        await existing_channel.delete()
