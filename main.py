import os
import dotenv
import discord
import random
from discord.ext import commands, tasks
from itertools import cycle
from commands.set_channel import SetChannelCommand
from myserver import server_on

# การดึงค่ามาใช้
dotenv.load_dotenv()
token = os.getenv('TOKEN')

# ตรวจสอบว่าค่าของ token ไม่เป็น None
if not token:
    raise ValueError("No TOKEN found. Please check your .env file.")

# กำหนดตัว prefix_commands และกำหนด intents ที่จำเป็น
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.bans = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

status_play = cycle(["โล้นต้า", "ควยเตอร์", "ควยโจ"])  # status ข้อความ

def random_color():
    return random.randint(0, 0xFFFFFF) # การสุ่มสี

@tasks.loop(seconds=5)
async def change_bot_status():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(next(status_play)))

@client.event
async def on_ready():
    change_bot_status.start()
    await client.change_presence(status=discord.Status.do_not_disturb)
    print(client.user,"is ready")
    try:
        client.tree.add_command(SetChannelCommand(client))
        synced_commands = await client.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occurred: ", e)


# member leave
@client.event
async def on_member_remove(member):
    if hasattr(client, 'channel_id_member_remove'):
        channel = client.get_channel(client.channel_id_member_remove)
        if channel:
            text = f"{member.mention} has left the server!"
            await channel.send(text)


# role create
@client.event
async def on_guild_role_create(role):
    if hasattr(client, 'channel_id_role_create'):
        channel = client.get_channel(client.channel_id_role_create)
        if channel:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    user_create = entry.user
                    break
                else:
                    user_create = None
                    
            embed = discord.Embed(
                title='Role Created',
                description='A role has been created!',
                timestamp=discord.utils.utcnow(),
                color=random_color()
            )
            embed.add_field(name="Role Name", value=role.name, inline=False)
            embed.add_field(name="Role ID", value=role.id, inline=False)
            embed.add_field(name="Created By", value=user_create.mention if user_create else "Unknown", inline=False)
            

            if user_create and user_create.avatar:
                embed.set_author(name=user_create.display_name, icon_url=user_create.avatar.url)
            else:
                embed.set_author(name=user_create.display_name if user_create else "Unknown")

            await channel.send(embed=embed)
            

#เงื่อนไขเกี่ยวกับ permission
latest_role_update_timestamp = {}

def compare_permissions(before, after):
    permissions_before = set(perm for perm, value in before if value)
    permissions_after = set(perm for perm, value in after if value)

    added = permissions_after - permissions_before
    removed = permissions_before - permissions_after

    return added, removed

# role update
@client.event
async def on_guild_role_update(before, after):
    if client.channel_id_role_update:
        channel = client.get_channel(client.channel_id_role_update)
        if channel:
            #print(f"on_guild_role_update called for role: {before.name} to {after.name}")
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
                if entry.target.id == after.id:
                    if (entry.created_at.timestamp() > latest_role_update_timestamp.get(after.id, 0)):
                        latest_role_update_timestamp[after.id] = entry.created_at.timestamp()
                        user_update = entry.user

                        embed = discord.Embed(
                            title="Role Updated",
                            description=f"A role has been updated!",
                            timestamp=discord.utils.utcnow(),
                            color=random_color()
                        )

                        embed.add_field(name="Role Name (Old)", value=before.name, inline=False)
                        embed.add_field(name="Role Name (New)", value=after.name, inline=False)
                        embed.add_field(name="Role ID", value=after.id, inline=False)

                        # add & remove perm
                        added_permissions, removed_permissions = compare_permissions(before.permissions, after.permissions)
                        if added_permissions:
                            embed.add_field(name="Added Permissions", value='\n'.join([f"`+ {perm}`" for perm in added_permissions]))

                        if added_permissions:
                            embed.add_field(name="\u200b", value="\u200b")

                        if removed_permissions:
                            embed.add_field(name="Removed Permissions", value='\n'.join([f"`- {perm}`" for perm in removed_permissions]))

                        embed.add_field(name="Updated By", value=user_update.mention if user_update else "Unknown", inline=False)

                        if user_update and user_update.avatar:
                            embed.set_author(name=user_update.display_name, icon_url=user_update.avatar.url)
                        else:
                            embed.set_author(name=user_update.display_name if user_update else "Unknown")

                        await channel.send(embed=embed)
                    break
            

# ลบ channel
@client.event
async def on_guild_channel_delete(channel):
    if hasattr(client, 'channel_id_channel_delete'):
        log_channel = client.get_channel(client.channel_id_channel_delete)
        if log_channel:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    user_delete = entry.user
                    break
                else:
                    user_delete = None

            embed = discord.Embed(
                title="Channel Deleted",
                description="A channel has been deleted!",
                timestamp=discord.utils.utcnow(),
                color=random_color()
            )

            embed.add_field(name="Channel Name", value=channel.name, inline=False)
            embed.add_field(name="Channel ID", value=channel.id, inline=False)
            embed.add_field(name="Deleted By", value=user_delete.mention if user_delete else "Unknown", inline=False)

            if user_delete and user_delete.avatar:
                embed.set_author(name=user_delete.display_name, icon_url=user_delete.avatar.url)
            else:
                embed.set_author(name=user_delete.display_name if user_delete else "Unknown")

            await log_channel.send(embed=embed)


# ลบ role
@client.event
async def on_guild_role_delete(role):
    if hasattr(client, 'channel_id_role_delete'):
        channel = client.get_channel(client.channel_id_role_delete)
        if channel:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    user_delete = entry.user
                    break
                else:
                    user_delete = None
                    
            embed = discord.Embed(
                title='Role Deleted',
                description='A role has been deleted!',
                timestamp=discord.utils.utcnow(),
                color=random_color()
            )
            embed.add_field(name="Role Name", value=role.name, inline=False)
            embed.add_field(name="Role ID", value=role.id, inline=False)
            embed.add_field(name="Deleted By", value=user_delete.mention if user_delete else "Unknown", inline=False)
            

            if user_delete and user_delete.avatar:
                embed.set_author(name=user_delete.display_name, icon_url=user_delete.avatar.url)
            else:
                embed.set_author(name=user_delete.display_name if user_delete else "Unknown")

            await channel.send(embed=embed)


# voice state
@client.event
async def on_voice_state_update(member, before, after):
    if hasattr(client, 'channel_id_voice_state'):
        channel = client.get_channel(client.channel_id_voice_state)
        
        if channel:
            # สร้าง Embed ใหม่
            embed = discord.Embed(
                timestamp=discord.utils.utcnow(), 
                color=random_color()
                )

            if before.channel is None and after.channel is not None:
                # เข้าสู่ voice channel
                embed.add_field(name="Voice State Update", value=f"{member.mention} joined voice channel!")
                embed.add_field(name="Channel Name", value=f"{after.channel.mention} ({after.channel.name})", inline=False)
                embed.add_field(name="Channel ID", value=f"`{after.channel.id}`", inline=False)

                if member.avatar:
                    embed.set_author(name=f"{member.name} ({member.display_name})", icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name if member.mention else "Unknown")

                embed.add_field(name="Reported By", value=client.user.mention if client.user else "Unknown", inline=False)

                await channel.send(embed=embed)

            elif before.channel is not None and after.channel is None:
                # ออกจาก voice channel
                embed.add_field(name="Voice State Update", value=f"{member.mention} left voice channel!")
                embed.add_field(name="Channel Name", value=f"{before.channel.mention} ({before.channel.name})", inline=False)
                embed.add_field(name="Channel ID", value=f"`{before.channel.id}`", inline=False)

                if member.avatar:
                    embed.set_author(name=f"{member.name} ({member.display_name})", icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name if member.mention else "Unknown")

                embed.add_field(name="Reported By", value=client.user.mention if client.user else "Unknown", inline=False)
            
                await channel.send(embed=embed)

            elif before.channel is not None and after.channel is not None and before.channel != after.channel:
                # ย้าย voice channel
                embed.add_field(name="Voice State Update", value=f"{member.mention} moved voice channel!")
                embed.add_field(name="Channel Moved", value=f"From {before.channel.mention} ({before.channel.name}) To {after.channel.mention} ({after.channel.name})", inline=False)
                embed.add_field(name="Channel ID", value=f"`{before.channel.id}`", inline=False)

                if member.avatar:
                    embed.set_author(name=f"{member.name} ({member.display_name})", icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name if member.mention else "Unknown")

                embed.add_field(name="Reported By", value=client.user.mention if client.user else "Unknown", inline=False)

                await channel.send(embed=embed)


async def create_banlist_embed(guild: discord.Guild) -> discord.Embed:
    embed = discord.Embed(
        title="List of Banned",
        color=random_color()
    )
    
    banned_users = []
    async for ban_entry in guild.bans():
        banned_users.append(ban_entry.user)
    
    if not banned_users:
        embed.description = "No users are currently banned."
    else:
        for user in banned_users:
            embed.add_field(
                name="•―――――――――――――――•",
                value=f"{user.mention} ({user.name}#{user.discriminator})\nReason : {ban_entry.reason}\n`ID : {user.id}`",
                inline=False
            )
    
    return embed

@client.tree.command(name='banlist', description='..')
async def ban_list(interaction: discord.Interaction):
    guild = interaction.guild
    embed = await create_banlist_embed(guild)
    await interaction.response.send_message(embed=embed, ephemeral=False)

@client.event
async def on_member_ban(guild: discord.Guild, member: discord.Member):
    if hasattr(client, 'channel_id_logs_ban') and hasattr(client, 'channel_id_banlist'):
        channel_logs = client.get_channel(client.channel_id_logs_ban)
        channel_banlist = client.get_channel(client.channel_id_banlist)

        # สร้าง embed สำหรับข้อมูลการแบน
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            logs_entry = entry
            created_at = logs_entry.created_at.strftime("%d/%m/%Y")
            if logs_entry.target == member:
                embed = discord.Embed(
                    description=f'{member.mention} was banned ({created_at})',
                    timestamp=discord.utils.utcnow(),
                    color=random_color()
                )
                embed.add_field(name="User Information", value=f'{member.name}#{member.discriminator} ({member.display_name})', inline=False)
                embed.add_field(name="Reason", value=logs_entry.reason, inline=False)
                embed.add_field(name="User ID", value=f"`{member.id}`")
                embed.add_field(name="Banned By", value=logs_entry.user.mention if logs_entry.user else "Unknown", inline=False)

                if member.avatar:
                    embed.set_author(name=f"{member.name} ({member.display_name})", icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name if member.mention else "Unknown")

                if channel_logs:
                    await channel_logs.send(embed=embed)

                if channel_banlist:
                    banned_users_embed = await create_banlist_embed(guild)
                    await channel_banlist.send(embed=banned_users_embed)
                else:
                    print("Channel for ban list is not set")
        
                    # await channel.send(f'{logs_entry.user.mention} has just banned {logs_entry.target.mention} (The time is {created_at}), reason is {logs_entry.reason}')


# unban
@client.tree.command(name="unban", description="..")
async def unban(interaction: discord.Interaction, user_id: str):
    # ตรวจสอบสิทธิ์ผู้ใช้
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    guild = interaction.guild
    channel = client.get_channel(client.channel_id_unban)
    channel_banlist = client.get_channel(client.channel_id_banlist)
    
    if not channel:
        await interaction.response.send_message("Unban notification channel is not set.", ephemeral=True)
        return

    if not user_id.isdigit():
        await interaction.response.send_message("Please provide a valid integer for user ID.", ephemeral=True)
        return
    
    await interaction.response.defer()

    try:
        user_id = int(user_id)

        # ดึงรายการการแบน
        async for ban_entry in guild.bans():
            if ban_entry.user.id == user_id:
                # ปลดแบนผู้ใช้
                await guild.unban(ban_entry.user)

                # สร้าง embed ข้อความ
                embed = discord.Embed(
                    description=f"{ban_entry.user.mention} has been unbanned.",
                    timestamp=discord.utils.utcnow(),
                    color=random_color()
                )
                embed.add_field(name="User Information", value=(f'{ban_entry.user.name}#{ban_entry.user.discriminator} ({ban_entry.user.display_name})'), inline=False)
                embed.add_field(name="User ID", value=f"{ban_entry.user.id}")
                embed.add_field(
                    name="Unbanned BY", 
                    value=f"{interaction.user.mention}", inline=False
                )

                if ban_entry.user.avatar:
                    embed.set_author(name=f"{ban_entry.user.name} ({ban_entry.user.display_name})", icon_url=ban_entry.user.avatar.url)
                else:
                    embed.set_author(name=ban_entry.user.display_name if ban_entry.user.mention else "Unknown")

                await channel.send(embed=embed)
                # ส่งข้อความตอบสนองที่สำเร็จ
                await interaction.followup.send("unbanned has been successfully.", ephemeral=True)

                if channel_banlist:
                    banned_users_embed = await create_banlist_embed(guild)
                    await channel_banlist.send(embed=banned_users_embed)
                else:
                    print("Channel for ban list is not set")
                return
            
        
        await interaction.followup.send("User not found in the banned list.", ephemeral=True)

    except discord.Forbidden:
        # ส่งข้อความตอบสนองข้อผิดพลาด
        await interaction.followup.send("I don't have permission to unban this user.", ephemeral=True)
    except Exception:
        # ส่งข้อความตอบสนองข้อผิดพลาด
        await interaction.followup.send("An unexpected error occurred.", ephemeral=True)


server_on()

client.run(token)
