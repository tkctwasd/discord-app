import discord
from datetime import datetime
import pytz

from data_service import create_order

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


class FoodModal(discord.ui.Modal, title="Đặt cơm"):

    menu = discord.ui.TextInput(
        label="Món ăn",
        placeholder="Cơm rang, gà, cần tỏi"
    )

    async def on_submit(self, interaction: discord.Interaction):
        price = 30000
        confirm_message = f"Món: {self.menu}\nGiá: {price:,}đ"

        order, updated = create_order(
            interaction.user,
            str(self.menu),
            price,
            message=confirm_message
        )

        now = datetime.now(TIMEZONE)

        if updated:
            embed = discord.Embed(
                title="✏️ Đã cập nhật đơn hôm nay",
                color=discord.Color.orange(),
                timestamp=now
            )
        else:
            embed = discord.Embed(
                title="🍚 Đã ghi nhận đơn",
                color=discord.Color.green(),
                timestamp=now
            )

        embed.add_field(
            name="Người đặt",
            value=f"- **{order['user_name']}** (<@{order['user_id']}>)",
            inline=False
        )
        embed.add_field(name="Món", value=f"- {order['menu']}", inline=False)
        embed.add_field(name="Giá", value=f"- **{order['price']:,}đ**", inline=False)
        embed.set_footer(text=now.strftime("%d/%m/%Y %H:%M"))

        await interaction.response.send_message(embed=embed)
