import discord
from discord.ui import Modal, TextInput, View, Button, Select
from datetime import datetime
import pytz

from config import ADMIN_ID
from data_service import mark_paid_by_ids, mark_pending_by_ids, unmark_pending_by_ids, record_bill

TIMEZONE = pytz.timezone('Asia/Ho_Chi_Minh')


class PaySelectView(View):

    def __init__(self, orders, image_url=None):
        super().__init__(timeout=120)
        self.orders_map = {str(o['id']): o for o in orders}
        self.selected_ids = []
        self.image_url = image_url
        self.original_interaction = None  # Set by caller after send_message

        options = [
            discord.SelectOption(
                label=f"{o['date']} - {o['price']:,}đ",
                description=(o['menu'] or '')[:50],
                value=str(o['id'])
            )
            for o in orders[:25]
        ]

        self.select = Select(
            placeholder="Chọn ngày muốn thanh toán...",
            min_values=1,
            max_values=len(options),
            options=options
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_timeout(self):
        if self.original_interaction:
            try:
                await self.original_interaction.delete_original_response()
            except Exception:
                pass

    async def on_select(self, interaction: discord.Interaction):
        self.selected_ids = self.select.values
        await interaction.response.defer()

    @discord.ui.button(label="Thanh toán", style=discord.ButtonStyle.primary, row=1)
    async def proceed(self, interaction: discord.Interaction, _: Button):

        if not self.selected_ids:
            await interaction.response.send_message(
                "⚠️ Vui lòng chọn ít nhất một ngày.",
                ephemeral=True
            )
            return

        selected = [
            self.orders_map[sid]
            for sid in self.selected_ids
            if sid in self.orders_map
        ]
        total = sum(o['price'] for o in selected)
        order_ids = [int(sid) for sid in self.selected_ids]

        await interaction.response.send_modal(
            PayConfirmModal(
                order_ids=order_ids,
                selected_orders=selected,
                total=total,
                image_url=self.image_url
            )
        )

        self.stop()
        if self.original_interaction:
            try:
                await self.original_interaction.delete_original_response()
            except Exception:
                pass


class PayConfirmModal(Modal, title="Xác nhận thanh toán"):

    content = TextInput(
        label="Nội dung",
        placeholder="Chuyển khoản tiền cơm...",
        style=discord.TextStyle.paragraph,
        required=False
    )

    def __init__(self, order_ids, selected_orders, total, image_url=None):
        super().__init__()
        self.order_ids = order_ids
        self.selected_orders = selected_orders
        self.total = total
        self.image_url = image_url

    async def on_submit(self, interaction: discord.Interaction):
        now = datetime.now(TIMEZONE)

        try:
            admin = await interaction.client.fetch_user(ADMIN_ID)
        except Exception:
            await interaction.response.send_message(
                "🚫 Không thể gửi hóa đơn. Vui lòng thử lại sau.", ephemeral=True
            )
            return

        dates_lines = "\n".join(
            f"- {o['date']} - {o['price']:,}đ"
            for o in self.selected_orders
        )
        admin_embed = discord.Embed(
            title="💰 Yêu cầu thanh toán",
            color=discord.Color.gold(),
            timestamp=now
        )
        admin_embed.add_field(
            name="Người thanh toán",
            value=f"- **{interaction.user.display_name}** (<@{interaction.user.id}>)",
            inline=False
        )
        admin_embed.add_field(name="Thanh toán các ngày", value=dates_lines, inline=False)
        admin_embed.add_field(name="Tổng tiền", value=f"- **{self.total:,}đ**", inline=True)
        admin_embed.add_field(name="Nội dung", value=f"- {self.content.value or '(không có)'}", inline=False)
        admin_embed.set_footer(text=f"Gửi lúc {now.strftime('%H:%M %d/%m/%Y')}")
        if self.image_url:
            admin_embed.set_image(url=self.image_url)

        admin_view = AdminPayView(
            user=interaction.user,
            amount=self.total,
            order_ids=self.order_ids,
            selected_orders=self.selected_orders,
            content=self.content.value,
            channel_id=interaction.channel_id
        )
        mark_pending_by_ids(self.order_ids)
        admin_message = await admin.send(embed=admin_embed, view=admin_view)

        dates_preview = "\n".join(f"- {o['date']} : {o['price']:,}đ" for o in self.selected_orders)
        confirm_embed = discord.Embed(
            title="🧾 Hóa đơn đã gửi!",
            color=discord.Color.green(),
            timestamp=now
        )
        confirm_embed.add_field(name="Thanh toán các ngày", value=dates_preview, inline=False)
        confirm_embed.add_field(name="Số tiền", value=f"- **{self.total:,}đ**", inline=True)
        confirm_embed.add_field(name="Nội dung", value=f"- {self.content.value or '(không có)'}", inline=False)
        confirm_embed.set_footer(text="Chờ xác nhận từ admin")
        if self.image_url:
            confirm_embed.set_image(url=self.image_url)

        cancel_view = PayCancelView(submit_interaction=interaction, admin_message=admin_message, order_ids=self.order_ids)
        await interaction.response.send_message(embed=confirm_embed, view=cancel_view, ephemeral=True)


class PayCancelView(View):

    def __init__(self, submit_interaction: discord.Interaction, admin_message, order_ids):
        super().__init__(timeout=180)
        self._submit_interaction = submit_interaction
        self.admin_message = admin_message
        self.order_ids = order_ids
        self.done = False

    async def on_timeout(self):
        if not self.done:
            self.done = True
            unmark_pending_by_ids(self.order_ids)
            try:
                await self._submit_interaction.delete_original_response()
            except Exception:
                pass

    # @discord.ui.button(label="↩️ Hủy yêu cầu", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, _: Button):
        self.done = True
        unmark_pending_by_ids(self.order_ids)
        try:
            await self.admin_message.edit(
                content="🚫 **Người dùng đã hủy yêu cầu thanh toán này.**",
                view=_make_disabled_view()
            )
        except Exception:
            pass
        canceled_embed = discord.Embed(
            title="↩️ Đã hủy yêu cầu thanh toán.",
            color=discord.Color.light_grey()
        )
        await interaction.response.edit_message(embed=canceled_embed, view=None)
        self.stop()


class RejectModal(Modal, title="Lý do từ chối"):

    reason = TextInput(
        label="Lý do từ chối",
        style=discord.TextStyle.paragraph,
        placeholder="Nhập lý do từ chối...",
        required=True
    )

    def __init__(self, user, amount, content, order_ids, selected_orders, channel_id, admin_message):
        super().__init__()
        self.target_user = user
        self.amount = amount
        self.content = content
        self.order_ids = order_ids
        self.selected_orders = selected_orders
        self.channel_id = channel_id
        self.admin_message = admin_message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        unmark_pending_by_ids(self.order_ids)

        record_bill(
            user_id=self.target_user.id,
            user_name=self.target_user.display_name,
            amount=self.amount,
            content=self.content,
            order_ids=self.order_ids,
            order_dates=[o['date'] for o in self.selected_orders],
            confirmed_by_id=interaction.user.id,
            confirmed_by_name=interaction.user.display_name,
            status="rejected",
            reason=self.reason.value
        )

        await self.admin_message.edit(view=_make_disabled_view())

        channel = interaction.client.get_channel(self.channel_id)
        if channel:
            now = datetime.now(TIMEZONE)
            dates_lines = "\n".join(
                f"- {o['date']} : {o['price']:,}đ"
                for o in self.selected_orders
            )
            embed = discord.Embed(
                title="🚫 Yêu cầu thanh toán bị từ chối",
                color=discord.Color.red(),
                timestamp=now
            )
            embed.add_field(
                name="Người thanh toán",
                value=f"- **{self.target_user.display_name}** (<@{self.target_user.id}>)",
                inline=False
            )
            embed.add_field(name="Các ngày thanh toán", value=dates_lines, inline=False)
            embed.add_field(name="Số tiền", value=f"- **{self.amount:,}đ**", inline=True)
            if self.content:
                embed.add_field(name="Nội dung", value=f"- {self.content}", inline=False)
            embed.add_field(name="Lý do từ chối", value=f"- {self.reason.value}", inline=False)
            embed.add_field(
                name="Từ chối bởi",
                value=f"- **{interaction.user.display_name}** (<@{interaction.user.id}>)",
                inline=True
            )
            await channel.send(f"🚫**{self.target_user.display_name}** (<@{self.target_user.id}>) đã bị từ chối yêu cầu thanh toán", embed=embed)


class AdminPayView(View):

    def __init__(self, user, amount, order_ids, selected_orders, content, channel_id):
        super().__init__(timeout=None)
        self.target_user = user
        self.amount = amount
        self.order_ids = order_ids
        self.selected_orders = selected_orders
        self.content = content
        self.channel_id = channel_id

    @discord.ui.button(label="Xác nhận", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _: Button):

        unmark_pending_by_ids(self.order_ids)
        mark_paid_by_ids(self.order_ids)

        record_bill(
            user_id=self.target_user.id,
            user_name=self.target_user.display_name,
            amount=self.amount,
            content=self.content,
            order_ids=self.order_ids,
            order_dates=[o['date'] for o in self.selected_orders],
            confirmed_by_id=interaction.user.id,
            confirmed_by_name=interaction.user.display_name,
            status="confirmed"
        )

        await interaction.response.edit_message(view=_make_disabled_view())

        channel = interaction.client.get_channel(self.channel_id)
        if channel:
            now = datetime.now(TIMEZONE)
            dates_lines = "\n".join(
                f"- {o['date']} - {o['menu']}"
                for o in self.selected_orders
            )
            embed = discord.Embed(
                title="💚 Thanh Toán Thành Công",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Người thanh toán",
                value=f"- **{self.target_user.display_name}** (<@{self.target_user.id}>)",
                inline=False
            )
            embed.add_field(
                name="Các ngày đã thanh toán",
                value=dates_lines,
                inline=False
            )
            embed.add_field(
                name="Số tiền",
                value=f"- **{self.amount:,}đ**",
                inline=False
            )
            embed.add_field(
                name="Xác nhận bởi",
                value=f"- **{interaction.user.display_name}** (<@{interaction.user.id}>)",
                inline=False
            )
            embed.add_field(
                name="Thời gian",
                value=now.strftime("- %d/%m/%Y %H:%M:%S"),
                inline=False
            )
            await channel.send(
                f"🎉 **{self.target_user.display_name}** (<@{self.target_user.id}>) "
                f"đã thanh toán thành công **{self.amount:,}đ**",
                embed=embed
            )

    @discord.ui.button(label="Từ chối", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, _: Button):
        await interaction.response.send_modal(
            RejectModal(
                user=self.target_user,
                amount=self.amount,
                content=self.content,
                order_ids=self.order_ids,
                selected_orders=self.selected_orders,
                channel_id=self.channel_id,
                admin_message=interaction.message
            )
        )


def _make_disabled_view():
    view = View()
    view.add_item(Button(label="Xác nhận", style=discord.ButtonStyle.success, disabled=True))
    view.add_item(Button(label="Từ chối", style=discord.ButtonStyle.danger, disabled=True))
    return view
