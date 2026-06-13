from data_service import mark_paid


async def paid_user(
    interaction,
    member
):
    count, total = mark_paid(
        member.id
    )

    await interaction.response.send_message(
        f"✅ Đã xác nhận thanh toán\n\n"
        f"User: {member.display_name}\n"
        f"Số bill: {count}\n"
        f"Tổng: {total:,}đ"
    )