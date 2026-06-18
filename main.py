import discord
from discord.ext import commands
from discord import app_commands
from commands.delete import delete_today
from commands.today import today_orders
from commands.export import export_orders

from config import (
    TOKEN,
    ADMIN_ROLE,
    ID_SERVER
)

from commands.menu import FoodModal
from commands.debt import (
    my_debt,
    all_debt
)
from commands.paid import (
    paid_user
)
import asyncio

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.tree.command(
    name="menu",
    description="Đặt cơm"
)
async def menu(
    interaction: discord.Interaction
):
    await interaction.response.send_modal(
        FoodModal()
    )


@bot.tree.command(
    name="mydebt",
    description="Xem công nợ cá nhân"
)
async def mydebt(
    interaction: discord.Interaction
):
    await my_debt(interaction)


@bot.tree.command(
    name="debt",
    description="Xem công nợ toàn bộ"
)
async def debt(
    interaction: discord.Interaction
):

    if not any(
        role.name == ADMIN_ROLE
        for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            "Không có quyền",
            ephemeral=True
        )
        return

    await all_debt(interaction)


@bot.tree.command(
    name="paid",
    description="Xác nhận thanh toán"
)
async def paid(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not any(
        role.name == ADMIN_ROLE
        for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            "Không có quyền",
            ephemeral=True
        )
        return

    await paid_user(
        interaction,
        member
    )

@bot.tree.command(
    name="delete",
    description="Xoá đơn hôm nay"
)
async def delete(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not any(
        role.name == ADMIN_ROLE
        for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            "Không có quyền",
            ephemeral=True
        )
        return

    await delete_today(
        interaction,
        member
    )

@bot.tree.command(
    name="today",
    description="Xem đơn cơm hôm nay"
)
async def today(
    interaction: discord.Interaction
):
    await today_orders(interaction)

@bot.tree.command(
    name="export",
    description="Xem đơn cơm hôm nay"
)
async def export(
    interaction: discord.Interaction
):
    await export_orders(interaction)


# @bot.event
# async def on_ready():

#     await bot.tree.sync()

#     print(
#         f"Bot online: {bot.user}"
#     )

GUILD_ID = ID_SERVER

@bot.event
async def on_ready():

    guild = discord.Object(id=GUILD_ID)

    bot.tree.copy_global_to(guild=guild)

    synced = await bot.tree.sync(guild=guild)
    
    print(f"✅ Bot online: {bot.user}")
    print(f"✅ Bot ID: {bot.user.id}")
    print(f"✅ Connected to {len(bot.guilds)} servers")
    print(f"Synced {len(synced)} commands")

async def load_cogs():
    print("[2/4] Đang load notifications...")
    await bot.load_extension('notifications')
    print("[3/4] Load notifications thành công!")


async def main():
    print("[START] Khởi động bot...")
    async with bot:
        print("[1/4] Đã vào async with bot")
        await load_cogs()
        print("[4/4] Đang đăng nhập Discord...")
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down (KeyboardInterrupt).")
    except Exception as e:
        print(f"Unhandled exception: {e}")
