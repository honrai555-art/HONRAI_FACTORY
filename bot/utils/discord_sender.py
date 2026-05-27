from discord.ext import commands


async def send_text(ctx: commands.Context, title: str, body: str) -> None:
    await ctx.reply(f"**{title}**\n```text\n{body[:1800]}\n```", mention_author=False)
