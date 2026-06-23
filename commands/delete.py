import discord
from datetime import datetime
import pytz

from data_service import delete_order

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


async def delete_today(interaction, member):
    removed = delete_order(member.id)

    if removed == 0:
        embed = discord.Embed(
            title="⚠️ Không có đơn để xoá",
            description=f"- **{member.display_name}** (<@{member.id}>) không có đơn hôm nay.",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(
        title="🗑️ Đã xoá đơn hôm nay",
        color=discord.Color.red(),
        timestamp=datetime.now(TIMEZONE)
    )
    embed.add_field(
        name="Người dùng",
        value=f"- **{member.display_name}** (<@{member.id}>)",
        inline=False
    )
    embed.add_field(name="Số đơn đã xoá", value=f"- **{removed}** đơn", inline=False)
    embed.add_field(
        name="Thực hiện bởi",
        value=f"- **{interaction.user.display_name}** (<@{interaction.user.id}>)",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
