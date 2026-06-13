import discord
from discord.ext import tasks, commands
from datetime import datetime, time
import pytz

from config import ID_CHANNEL_NOTIFICATION, ID_CHANNEL_REPORT
from data_service import get_all_debts


class NotificationsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone('Asia/Ho_Chi_Minh') 
        self.daily_food_notification.start()
        self.weekly_report_notification.start()
    
    @tasks.loop(minutes=1)
    async def daily_food_notification(self):
        now_dt = datetime.now(self.timezone)
        current_time = now_dt.time()

        # Check every minute; send at 10:00 AM
        if current_time.hour == 16 and current_time.minute == 6:
            channel = self.bot.get_channel(ID_CHANNEL_NOTIFICATION)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(ID_CHANNEL_NOTIFICATION)
                except Exception:
                    channel = None
            if channel:
                embed = discord.Embed(
                    title="🍽️ Đặt Cơm Hôm Nay",
                    description="Đến giờ đặt cơm rồi! Hãy sử dụng lệnh `/menu` để đặt cơm",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="⏰ Thời gian",
                    value="10:00 AM",
                    inline=False
                )
                embed.set_footer(text="Thông báo tự động hàng ngày")
                await channel.send(embed=embed)
    
    @daily_food_notification.before_loop
    async def before_daily_food(self):
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=1)
    async def weekly_report_notification(self):
        now = datetime.now(self.timezone)
        is_friday = now.weekday() == 5
        current_time = now.time()

        # Check every minute; send at 14:00 on Fridays
        if is_friday and current_time.hour == 16 and current_time.minute == 23:
            channel = self.bot.get_channel(ID_CHANNEL_REPORT)
            if channel is None:
                try:
                    channel = await self.bot.fetch_channel(ID_CHANNEL_REPORT)
                except Exception:
                    channel = None
            if channel:
                
                debts = get_all_debts()
                embed = discord.Embed(
                    title="📊 Báo Cáo Công Nợ Tuần",
                    description="Dùng `/mydebt` để xem chi tiết",
                    color=discord.Color.green()
                )
                
                if debts:
                    total = sum(debts.values())
                    
                    debt_lines = []
                    for user_name, amount in sorted(debts.items(), key=lambda x: x[1], reverse=True):
                        debt_lines.append(f"- **{user_name}**: {amount:,}đ")
                    
                    debt_text = "\n".join(debt_lines)
                    if len(debt_text) > 1024:
                        for i in range(0, len(debt_lines), 10):
                            chunk = debt_lines[i:i+10]
                            embed.add_field(
                                name="Công nợ" if i == 0 else "‎",
                                value="\n".join(chunk),
                                inline=False
                            )
                    else:
                        embed.add_field(
                            name="",
                            value=debt_text,
                            inline=False
                        )
                    
                    embed.add_field(
                        name="📌 Tổng cộng",
                        value=f"**{total:,}đ**",
                        inline=False
                    )
                else:
                    embed.description = "✅ Không có công nợ"
                
                embed.set_footer(text="Báo cáo tự động hàng tuần - Thứ 6 lúc 14:00")
                await channel.send(embed=embed)
    
    @weekly_report_notification.before_loop
    async def before_weekly_report(self):
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        self.daily_food_notification.cancel()
        self.weekly_report_notification.cancel()

async def setup(bot):
    await bot.add_cog(NotificationsCog(bot))

print("✅ Scheduled tasks started")