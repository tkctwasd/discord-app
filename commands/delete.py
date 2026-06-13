from data_service import delete_order


async def delete_today(interaction, member):

    removed = delete_order(member.id)

    if removed == 0:

        await interaction.response.send_message(
            f"⚠️ {member.display_name} không có đơn hôm nay."
        )

        return

    await interaction.response.send_message(
        f"🗑️ Đã xoá {removed} đơn hôm nay của {member.display_name}"
    )