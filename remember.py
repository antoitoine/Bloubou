####################
# Required imports #
####################


import discord


#####################
# Default variables #
#####################


message = discord.Message()
guild = discord.Guild()
client = discord.Client()


###########
# Methods #
###########


# Get roles in a guild
print(guild.roles)

# Get channels in a guild
print(guild.channels)

# Add a role to a user
await message.author.add_roles(discord.utils.get(message.guild.roles, name="roleName"))

# Invite a user to a channel
for channel in guild.channels:
    if channel.name == "channelToInvite":
        link = await channel.create_invite()
        await message.channel.send(link)

# Create an admin role
await guild.create_role(name="admin", permissions=discord.Permissions(permissions=8))

# Get guilds where client is
print(client.guilds)

# Create a new guild
await client.create_guild("guildName")

# Create a text channel
await guild.create_text_channel("channelName")
