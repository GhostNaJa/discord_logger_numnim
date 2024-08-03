import discord
import json
import random
from discord.ext import commands
from discord import app_commands

SETTINGS_FILE = 'settings.json'

# กำหนดตัว prefix_commands และกำหนด intents ที่จำเป็น
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=discord.Intents.default())


def random_color():
    return discord.Colour(random.randint(0x000000, 0xFFFFFF))


class SetChannelCommand(app_commands.Group):
    def __init__(self, client):
        self.client = client
        super().__init__(name="set", description="Set channels for various notifications.")
        self.load_settings()

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.client.channel_id_member_remove = settings.get('channel_id_member_remove')
                self.client.channel_id_role_create = settings.get('channel_id_role_create')
                self.client.channel_id_role_update = settings.get('channel_id_role_update')
                self.client.channel_id_channel_delete = settings.get('channel_id_channel_delete')
                self.client.channel_id_role_delete = settings.get('channel_id_role_delete')
                self.client.channel_id_voice_state = settings.get('channel_id_voice_state')
                self.client.channel_id_logs_ban = settings.get('channel_id_logs_ban')
                self.client.channel_id_unban = settings.get('channel_id_unban')
                self.client.channel_id_banlist = settings.get('channel_id_banlist')
        except FileNotFoundError:
            self.client.channel_id_member_remove = None
            self.client.channel_id_role_create = None
            self.client.channel_id_role_update = None
            self.client.channel_id_channel_delete = None
            self.client.channel_id_role_delete = None
            self.client.channel_id_voice_state = None
            self.client.channel_id_logs_ban = None
            self.client.channel_id_unban = None
            self.client.channel_id_banlist = None
        except json.JSONDecodeError:
            print("Error decoding the settings file. Please ensure it's a valid JSON.")

    def save_settings(self):
        settings = {
            'channel_id_member_remove': getattr(self.client, 'channel_id_member_remove', None),
            'channel_id_role_create': getattr(self.client, 'channel_id_role_create', None),
            'channel_id_role_update': getattr(self.client, 'channel_id_role_update', None),
            'channel_id_channel_delete': getattr(self.client, 'channel_id_channel_delete', None),
            'channel_id_role_delete': getattr(self.client, 'channel_id_role_delete', None),
            'channel_id_voice_state': getattr(self.client, 'channel_id_voice_state', None),
            'channel_id_logs_ban': getattr(self.client, 'channel_id_logs_ban', None),
            'channel_id_unban': getattr(self.client, 'channel_id_unban', None),
            'channel_id_banlist': getattr(self.client, 'channel_id_banlist', None)
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)


    # ephemeral = true ทำให้ระบบตอบกลับให้เราเห็นแค่คนเดียว
    @app_commands.command(name='member_remove', description='Set the channel for member remove notifications.')
    async def member_remove(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_member_remove = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for member remove set to {channel.mention}.", ephemeral=True)


    # role update
    @app_commands.command(name='role_update', description='Set the channel for role update notifications.')
    async def role_update(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_role_update = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for role update set to {channel.mention}.", ephemeral=True)


    # channel delete
    @app_commands.command(name='channel_delete', description='Set the channel for channel delete notifications.')
    async def channel_delete(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_channel_delete = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for channel delete set to {channel.mention}.", ephemeral=True)


    # role create
    @app_commands.command(name='role_create', description='Set the channel for role create notifications.')
    async def role_create(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_role_create = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for role create set to {channel.mention}.", ephemeral=True)


    # role delete
    @app_commands.command(name='role_delete', description='Set the channel for role delete notifications.')
    async def role_delete(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_role_delete = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for role delete set to {channel.mention}.", ephemeral=True)


    # voice member join & leave
    @app_commands.command(name='voice_state', description='Set the channel for voice state notifications.')
    async def voice_state_update(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_voice_state = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for voice state set to {channel.mention}.", ephemeral=True)


    # ban log
    @app_commands.command(name='channel_ban', description='Set the channel for ban notifications.')
    async def member_logs_ban(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return
        
        self.client.channel_id_logs_ban = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for ban log set to {channel.mention}.", ephemeral=True)
    

    # unban
    @app_commands.command(name='channel_unban', description='Set the channel for unban notifications.')
    async def channel_unban(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        self.client.channel_id_unban = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for unban notifications set to {channel.mention}.", ephemeral=True)


    # banlist
    @app_commands.command(name='channel_banlist', description='Set the channel for ban_list notifications.')
    async def channel_banlist(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)
            return
        
        self.client.channel_id_banlist = channel.id
        self.save_settings()
        await interaction.response.send_message(f"Channel for banlist notification set to {channel.mention}.", ephemeral=True)
