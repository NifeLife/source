import discord
from discord.ext import commands
from discord import app_commands, ui

# Inisialisasi bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Event saat bot siap
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# 1. Command untuk membuat embed sistem laporan
@bot.tree.command(name="setup_ticket", description="Setup the ticket system")
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ticket Report",
        description=(
            "Bantu kami menjaga komunitas ini tetap aman! Laporkan segala bentuk aktivitas yang mencurigakan, seperti:\n"
            "- Scamming\n"
            "- Penipuan\n"
            "- Phishing\n"
            "- Spam\n"
            "- Pelecehan\n\n"
            "Sertakan bukti seperti screenshot dan link profil agar kami dapat menindaklanjuti laporan Anda."
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Powered by your bot")
    
    view = TicketView()
    await interaction.response.send_message(embed=embed, view=view)

# 2. View dengan tombol untuk membuka tiket
class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Open a ticket!", style=discord.ButtonStyle.red, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        category_name = "Tickets"
        category = discord.utils.get(guild.categories, name=category_name)

        if not category:
            category = await guild.create_category(category_name)

        ticket_channel_name = f"ticket-{interaction.user.name.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=ticket_channel_name)

        if existing_channel:
            await interaction.response.send_message(
                f"You already have an open ticket: {existing_channel.mention}", ephemeral=True
            )
        else:
            ticket_channel = await guild.create_text_channel(
                ticket_channel_name, category=category,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
            )
            await ticket_channel.send(
                f"Hello {interaction.user.mention}, our team will assist you shortly. "
                "Please describe your issue here.",
                view=TicketManagementView()
            )
            await interaction.response.send_message(
                f"Your ticket has been created: {ticket_channel.mention}", ephemeral=True
            )

# 3. View untuk tombol pengelolaan tiket
class TicketManagementView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Close", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        if "ticket" in channel.name:
            await channel.delete(reason="Ticket closed by user")
        else:
            await interaction.response.send_message(
                "This command can only be used in a ticket channel.", ephemeral=True
            )

    @ui.button(label="Claim", style=discord.ButtonStyle.green, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            f"Ticket claimed by {interaction.user.mention}.", ephemeral=False
        )

    @ui.button(label="Close With Reason", style=discord.ButtonStyle.blurple, custom_id="close_with_reason")
    async def close_with_reason(self, interaction: discord.Interaction, button: ui.Button):
        modal = CloseReasonModal()
        await interaction.response.send_modal(modal)

# 4. Modal untuk memberikan alasan penutupan tiket
class CloseReasonModal(ui.Modal, title="Close Ticket with Reason"):
    reason = ui.TextInput(label="Reason for closing", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.send(f"Ticket closed with reason: {self.reason.value}")
        await interaction.channel.delete(reason="Ticket closed with reason provided by user.")

# Menjalankan bot
bot.run("YOUR_BOT_TOKEN")
