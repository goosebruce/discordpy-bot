import json
import discord

with open("config.json") as f:
    config = json.load(f)


async def add_pro_group_channel(member, role) -> None:
    channel_name = f"leads-{role.name}"
    id = 1077796703408762951
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


async def handle_pro_role_change(before, after) -> None:
    print("member change event triggered")
    print(before.roles)
    print(after.roles)
    pro_role = discord.utils.get(after.roles, name="Pro")
    if pro_role is None:
        # Pro role was removed, remove all pro group roles from member
        for role in after.roles:
            if role.name.startswith(config["pro_role_suffix"]):
                print(f"Removing {role} from {after}")
                await after.remove_roles(role)
        return
    if pro_role not in before.roles:
        # Pro role was added, assign member to pro group
        if config["pro_role_suffix"] not in [r.name for r in after.roles]:
            print("Member does not have pro group role")
            # add a loop at all groups that start with the pro role suffix and count members in each group, if any are less than 5, assign the role to the member
            roles = [
                r
                for r in after.guild.roles
                if r.name.startswith(config["pro_role_suffix"])
            ]
            need_new_role = False
            for role in roles:
                if len(role.members) < 5:
                    await after.add_roles(role)
                    print(f"Added {role} to")
                    await add_pro_group_channel(after, role)
                    return
                else:
                    need_new_role = True
            if need_new_role:
                pro_group_num = len(roles) + 1
                new_role = await after.guild.create_role(
                    name=f"{config['pro_role_suffix']}{pro_group_num}",
                    color=discord.Color.random(),
                )
                await new_role.edit(
                    position=after.guild.get_role(after.guild.id).position + 1
                )
                await after.add_roles(new_role)
                await add_pro_group_channel(after, new_role)

        else:
            print("Member already has pro group role")

    else:
        print("Member already has pro role")
