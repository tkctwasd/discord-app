import discord
from datetime import datetime
import pytz

from data_service import mark_paid

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


async def paid_user(interaction, member):
    count, total = mark_paid(member.id)

    if count == 0:
        embed = discord.Embed(
            title="⚠️ Không có công nợ",
            description=f"**{member.display_name}** (<@{member.id}>) không có công nợ nào.",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="✅ Xác nhận thanh toán thành công",
        color=discord.Color.green(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(
        name="Người thanh toán",
        value=f"**{member.display_name}** (<@{member.id}>)",
        inline=False
    )
    embed.add_field(name="Số bill", value=f"**{count}** đơn", inline=True)
    embed.add_field(name="Tổng tiền", value=f"**{total:,}đ**", inline=True)
    embed.add_field(
        name="Xác nhận bởi",
        value=f"**{interaction.user.display_name}** (<@{interaction.user.id}>)",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
