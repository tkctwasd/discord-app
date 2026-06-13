import discord

from data_service import create_order


class FoodModal(discord.ui.Modal, title="Đặt cơm"):

    menu = discord.ui.TextInput(
        label="Món ăn",
        placeholder="Cơm rang, gà, cần tỏi"
    )

#     price = discord.ui.TextInput(
#         label="Giá tiền",
#         default="30000"
#     )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        try:
            price = int(str(30000))
        except:
            await interaction.response.send_message(
                "Giá tiền không hợp lệ",
                ephemeral=True
            )
            return

        confirm_message = None
        if self.menu:
            confirm_message = (
                f"Món: {self.menu}\n"
                f"Giá: {price:,}đ"
            )

        order, updated = create_order(
            interaction.user,
            str(self.menu),
            price,
            message=confirm_message
        )

        if updated:
            await interaction.response.send_message(
                f"✏️ Đã cập nhật đơn hôm nay\n\n"
                f"Tên: {order['user_name']}\n"
                f"Món: {order['menu']}\n"
                f"Giá: {order['price']:,}đ"
            )

        else:
            await interaction.response.send_message(
                f"✅ Đã ghi nhận đơn\n\n"
                f"Tên: {order['user_name']}\n"
                f"Món: {order['menu']}\n"
                f"Giá: {order['price']:,}đ"
            )