import json
import discord

with open("config.json") as f:
    config = json.load(f)


async def add_basic_group_channel(member, role) -> None:
    channel_name = f"leads-{role.name}"
    id = config["basic_group_category_id"]
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


async def handle_basic_role_change(before, after) -> None:
    print("member change event triggered")
    print(before.roles)
    print(after.roles)
    basic_role = discord.utils.get(after.roles, name="Basic")
    if basic_role is None:
        # basic role was removed, remove all basic group roles from member
        for role in after.roles:
            if role.name.startswith(config["basic_role_pre"]):
                print(f"Removing {role} from {after}")
                await after.remove_roles(role)
        return
    if basic_role not in before.roles:
        # basic role was added, assign member to basic group
        if config["basic_role_pre"] not in [r.name for r in after.roles]:
            print("Member does not have basic group role")
            # add a loop at all groups that start with the basic role pre and count members in each group, if any are less than 5, assign the role to the member
            roles = [
                r
                for r in after.guild.roles
                if r.name.startswith(config["basic_role_pre"])
            ]
            need_new_role = False
            for role in roles:
                if len(role.members) < config["max_basic_members_per_group"]:
                    await after.add_roles(role)
                    print(f"Added {role} to")
                    await add_basic_group_channel(after, role)
                    return
                else:
                    need_new_role = True
            if need_new_role:
                group_num = len(roles) + 1
                new_role = await after.guild.create_role(
                    name=f"{config['basic_role_pre']}{group_num}",
                    color=discord.Color.random(),
                )
                await new_role.edit(
                    position=after.guild.get_role(after.guild.id).position + 1
                )
                await after.add_roles(new_role)
                await add_basic_group_channel(after, new_role)

        else:
            print("Member already has basic group role")

    else:
        print("Member already has basic role")
