import discord
from datetime import datetime
import pytz

from data_service import get_today_orders

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


async def export_orders(interaction):
    orders = get_today_orders()
    now = datetime.now(TIMEZONE)

    if not orders:
        embed = discord.Embed(
            title="📤 Chưa có đơn hôm nay",
            description="- Hôm nay chưa ai đặt cơm.",
            color=discord.Color.light_grey(),
            timestamp=now
        )
        await interaction.response.send_message(embed=embed)
        return

    total_money = sum(o["price"] for o in orders)
    lines = "\n".join(f"- {o['menu']}" for o in orders)

    embed = discord.Embed(
        title=f"📤 Export đơn cơm — {now.strftime('%d/%m/%Y')}",
        color=discord.Color.blurple(),
        timestamp=now
    )
    embed.add_field(name="Danh sách món", value=lines, inline=False)
    embed.add_field(name="Tổng suất", value=f"- **{len(orders)}** suất", inline=False)
    embed.add_field(name="Tổng tiền", value=f"- **{total_money:,}đ**", inline=False)

    await interaction.response.send_message(embed=embed)
