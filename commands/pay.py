import discord
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
import pytz

from config import ADMIN_ID
from data_service import mark_paid_by_amount

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


class PayModal(Modal, title="Thanh toán công nợ"):

    amount = TextInput(
        label="Số tiền (VNĐ)",
        placeholder="100000",
        required=True
    )

    content = TextInput(
        label="Nội dung",
        placeholder="Chuyển khoản tiền cơm tháng 6",
        style=discord.TextStyle.paragraph,
        required=False
    )

    image_url = TextInput(
        label="Link ảnh chuyển khoản (không bắt buộc)",
        placeholder="https://...",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        try:
            amount_int = int(
                self.amount.value
                .replace(",", "")
                .replace(".", "")
                .strip()
            )
            if amount_int <= 0:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Số tiền không hợp lệ.",
                ephemeral=True
            )
            return

        now = datetime.now(TIMEZONE)

        await interaction.response.send_message(
            f"✅ Hóa đơn đã gửi!\n\n"
            f"Số tiền: **{amount_int:,}đ**\n"
            f"Nội dung: {self.content.value or '(không có)'}\n\n"
            f"⏳ Chờ xác nhận từ admin...",
            ephemeral=True
        )

        try:
            admin = await interaction.client.fetch_user(ADMIN_ID)
        except Exception:
            return

        embed = discord.Embed(
            title="💰 Yêu cầu thanh toán",
            color=discord.Color.blue(),
            timestamp=now
        )
        embed.add_field(
            name="👤 Người dùng",
            value=f"**{interaction.user.display_name}** (<@{interaction.user.id}>)",
            inline=False
        )
        embed.add_field(
            name="💵 Số tiền",
            value=f"**{amount_int:,}đ**",
            inline=True
        )
        embed.add_field(
            name="📝 Nội dung",
            value=self.content.value or "(không có)",
            inline=False
        )
        embed.set_footer(text=f"Gửi lúc {now.strftime('%H:%M %d/%m/%Y')}")

        if self.image_url.value.strip():
            embed.set_image(url=self.image_url.value.strip())

        view = AdminPayView(
            user=interaction.user,
            amount=amount_int,
            channel_id=interaction.channel_id
        )

        await admin.send(embed=embed, view=view)


class RejectModal(Modal, title="Lý do từ chối"):

    reason = TextInput(
        label="Lý do từ chối",
        style=discord.TextStyle.paragraph,
        placeholder="Nhập lý do từ chối...",
        required=True
    )

    def __init__(self, user, amount, channel_id, admin_message):
        super().__init__()
        self.target_user = user
        self.amount = amount
        self.channel_id = channel_id
        self.admin_message = admin_message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        disabled_view = _make_disabled_view()
        await self.admin_message.edit(view=disabled_view)

        channel = interaction.client.get_channel(self.channel_id)
        if channel:
            await channel.send(
                f"❌ <@{self.target_user.id}> - Yêu cầu thanh toán **{self.amount:,}đ** đã bị **từ chối**.\n"
                f"📌 Lý do: {self.reason.value}"
            )


class AdminPayView(View):

    def __init__(self, user, amount, channel_id):
        super().__init__(timeout=None)
        self.target_user = user
        self.amount = amount
        self.channel_id = channel_id

    @discord.ui.button(label="✅ Xác nhận", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _button: Button):

        mark_paid_by_amount(self.target_user.id, self.amount)

        disabled_view = _make_disabled_view()
        await interaction.response.edit_message(view=disabled_view)

        channel = interaction.client.get_channel(self.channel_id)
        if channel:
            now = datetime.now(TIMEZONE)
            embed = discord.Embed(
                title="💚 Thanh Toán Thành Công",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Người thanh toán",
                value=f"**{self.target_user.display_name}** (<@{self.target_user.id}>)",
                inline=False
            )
            embed.add_field(
                name="Số tiền",
                value=f"**{self.amount:,}đ**",
                inline=False
            )
            embed.add_field(
                name="Xác nhận bởi",
                value=f"**{interaction.user.display_name}** (<@{interaction.user.id}>)",
                inline=False
            )
            embed.add_field(
                name="Thời gian",
                value=now.strftime("%d/%m/%Y %H:%M:%S"),
                inline=False
            )
            await channel.send(
                f"🎉 **{self.target_user.display_name}** (<@{self.target_user.id}>) "
                f"đã thanh toán thành công **{self.amount:,}đ** ✅",
                embed=embed
            )

    @discord.ui.button(label="❌ Từ chối", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, _button: Button):
        modal = RejectModal(
            user=self.target_user,
            amount=self.amount,
            channel_id=self.channel_id,
            admin_message=interaction.message
        )
        await interaction.response.send_modal(modal)


def _make_disabled_view():
    view = View()
    confirm_btn = Button(
        label="✅ Xác nhận",
        style=discord.ButtonStyle.success,
        disabled=True
    )
    reject_btn = Button(
        label="❌ Từ chối",
        style=discord.ButtonStyle.danger,
        disabled=True
    )
    view.add_item(confirm_btn)
    view.add_item(reject_btn)
    return view
