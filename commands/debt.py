from data_service import (
    get_user_debts,
    get_all_debts
)


async def my_debt(interaction):

    debts = get_user_debts(
        interaction.user.id
    )

    if not debts:
        await interaction.response.send_message(
            "✅ Không có công nợ",
            ephemeral=True
        )
        return

    total = 0
    lines = []

    for debt in debts:

        total += debt["price"]

        lines.append(
            f"- {debt['date']} - {debt['price']:,}đ"
        )

    await interaction.response.send_message(
        "📋 Công nợ của bạn\n\n"
        + "\n".join(lines)
        + f"\n\nTổng: **{total:,}đ**",
        ephemeral=True
    )


async def all_debt(interaction):

    debts = get_all_debts()

    if not debts:
        await interaction.response.send_message(
            "Không có công nợ"
        )
        return

    total = 0
    lines = []

    for user_id, info in debts.items():

        total += info["money"]

        lines.append(
            f"- **{info['user_name']}** (<@{user_id}>): {info['money']:,}đ"
        )

    await interaction.response.send_message(
        "📊 Công nợ hiện tại\n\n"
        + "\n".join(lines)
        + f"\n\nTổng: **{total:,}đ**"
    )