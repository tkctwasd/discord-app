from data_service import get_today_orders


async def export_orders(interaction):

    orders = get_today_orders()

    if not orders:

        await interaction.response.send_message(
            "📭 Hôm nay chưa có ai đặt cơm."
        )
        return

    total_money = 0

    lines = []

    for index, order in enumerate(orders, start=1):

        total_money += order["price"]

        lines.append(
            f"   - {order['menu']}"
        )

    await interaction.response.send_message(
        "🍱 Đơn cơm hôm nay\n\n"
        + "\n\n".join(lines)
        + f"\n\nTổng suất: {len(orders)}"
        + f"\nTổng tiền: {total_money:,}đ"
    )


    