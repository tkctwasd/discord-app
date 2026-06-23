import discord
from datetime import datetime
import pytz

from data_service import get_user_debts, get_all_debts

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


async def my_debt(interaction):
    debts = get_user_debts(interaction.user.id)

    if not debts:
        embed = discord.Embed(
            title="✅ Không có công nợ",
            description="Bạn đã thanh toán hết rồi!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    total = sum(d["price"] for d in debts)
    lines = "\n".join(
        f"• {d['date']} — **{d['price']:,}đ**"
        for d in debts
    )

    embed = discord.Embed(
        title="💳 Công nợ của bạn",
        color=discord.Color.blue(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(
        name="Người dùng",
        value=f"- **{interaction.user.display_name}** (<@{interaction.user.id}>)",
        inline=False
    )
    embed.add_field(name="Chi tiết", value=lines, inline=False)
    embed.add_field(name="Tổng nợ", value=f"- **{total:,}đ** ({len(debts)} ngày)", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


async def all_debt(interaction):
    debts = get_all_debts()

    if not debts:
        embed = discord.Embed(
            title="✅ Không có công nợ",
            description="Tất cả mọi người đã thanh toán hết!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        return

    grand_total = sum(info["money"] for info in debts.values())
    lines = "\n".join(
        f"- **{info['user_name']}** (<@{user_id}>): **{info['money']:,}đ**"
        for user_id, info in debts.items()
    )

    embed = discord.Embed(
        title="📒 Công nợ hiện tại",
        color=discord.Color.orange(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(name="Chi tiết", value=lines, inline=False)
    embed.add_field(
        name=" Tổng cộng",
        value=f"- **{grand_total:,}đ** ({len(debts)} người)",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
