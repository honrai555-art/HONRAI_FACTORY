import asyncio
import os
import sys
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from bot.commands.gitpull import run_gitpull
from bot.commands.logs import get_latest_logs
from bot.commands.manga import run_manga
from bot.commands.comfy import run_comfy_test
from bot.commands.status import get_status
from bot.commands.pipeline_manga import run_pipeline_manga
from bot.commands.unity import run_unity
from bot.utils.logger import get_logger, log_exception


load_dotenv(BASE_DIR / ".env")

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
ALLOWED_CHANNEL_ID = os.getenv("ALLOWED_CHANNEL_ID", "").strip()

logger = get_logger("bot")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def _allowed_channel_id() -> int | None:
    if not ALLOWED_CHANNEL_ID:
        return None
    try:
        return int(ALLOWED_CHANNEL_ID)
    except ValueError:
        logger.error("ALLOWED_CHANNEL_ID must be numeric.")
        return None


async def send_command_result(ctx: commands.Context, title: str, body: str) -> None:
    message = f"**{title}**\n```text\n{body[:1800]}\n```"
    await ctx.reply(message, mention_author=False)


@bot.event
async def on_ready() -> None:
    logger.info("HONRAI_FACTORY Bot logged in as %s", bot.user)
    print(f"HONRAI_FACTORY Bot logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    logger.info(
        "Message received: guild_id=%s channel_id=%s author=%s content=%s",
        message.guild.id if message.guild else None,
        message.channel.id,
        message.author,
        message.content,
    )

    if message.content.strip().lower() == "ping":
        await message.reply("PONG. コマンドは `!ping` / `!status` の形で送ってください。", mention_author=False)
        return

    await bot.process_commands(message)


@bot.check
async def only_allowed_channel(ctx: commands.Context) -> bool:
    allowed_id = _allowed_channel_id()
    if allowed_id is None:
        await ctx.reply(
            "ALLOWED_CHANNEL_ID is not configured. Please update bot/.env.",
            mention_author=False,
        )
        return False

    if ctx.channel.id != allowed_id:
        logger.info(
            "Ignored command from unauthorized channel: channel_id=%s author=%s command=%s",
            ctx.channel.id,
            ctx.author,
            ctx.message.content,
        )
        return False

    return True


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    if isinstance(error, commands.CheckFailure):
        return

    log_exception(logger, "Command failed", error)
    try:
        await send_command_result(ctx, "ERROR", str(error))
    except Exception as send_error:
        log_exception(logger, "Failed to send error notification", send_error)


@bot.command(name="status")
async def status_command(ctx: commands.Context) -> None:
    logger.info("Command received: status")
    await send_command_result(ctx, "HONRAI_FACTORY STATUS", get_status())


@bot.command(name="ping")
async def ping_command(ctx: commands.Context) -> None:
    logger.info("Command received: ping")
    latency_ms = bot.latency * 1000
    await send_command_result(ctx, "PONG", f"Discord latency: {latency_ms:.0f} ms")


@bot.command(name="gitpull")
async def gitpull_command(ctx: commands.Context) -> None:
    logger.info("Command received: gitpull")
    await send_command_result(ctx, "GIT PULL", run_gitpull())


@bot.command(name="manga")
async def manga_command(ctx: commands.Context) -> None:
    logger.info("Command received: manga")
    await send_command_result(ctx, "MANGA LINE", run_manga())


@bot.command(name="comfy_test")
async def comfy_test_command(ctx: commands.Context) -> None:
    logger.info("Command received: comfy_test")
    try:
        result = run_comfy_test()
        await send_command_result(ctx, "COMFY TEST", result)
    except Exception as e:
        await send_command_result(ctx, "COMFY TEST ERROR", str(e))


@bot.command(name="pipeline_manga")
async def pipeline_manga_command(ctx: commands.Context) -> None:
    logger.info("Command received: pipeline_manga")
    try:
        result = run_pipeline_manga()
        await ctx.reply(f"✅ 漫画ライン実行完了\n```text\n{result[:1800]}\n```", mention_author=False)
    except Exception as exc:
        log_exception(logger, "pipeline_manga failed", exc)
        await ctx.reply(f"❌ 漫画ライン実行失敗\n```text\n{str(exc)[:1800]}\n```", mention_author=False)


@bot.command(name="unity")
async def unity_command(ctx: commands.Context) -> None:
    logger.info("Command received: unity")
    await send_command_result(ctx, "UNITY LINE", run_unity())


@bot.command(name="logs")
async def logs_command(ctx: commands.Context) -> None:
    logger.info("Command received: logs")
    await send_command_result(ctx, "LATEST LOGS", get_latest_logs())


@bot.command(name="restart")
async def restart_command(ctx: commands.Context) -> None:
    logger.info("Command received: restart")
    await ctx.reply("Restarting HONRAI_FACTORY Bot...", mention_author=False)
    await bot.close()

    python = sys.executable
    os.execl(python, python, *sys.argv)


@bot.command(name="help")
async def help_command(ctx: commands.Context) -> None:
    logger.info("Command received: help")
    await send_command_result(
        ctx,
        "HONRAI_FACTORY COMMANDS",
        "\n".join(
            [
                "!status   - CPU/RAM/GPU and line status",
                "!gitpull  - Run git pull in PROJECT_ROOT",
                "!manga    - Start Manga generation watcher",
                "!pipeline_manga - Run GPT -> ComfyUI -> Discord pipeline",
                "!unity    - Start Unity build script",
                "!logs     - Show latest bot and error logs",
                "!restart  - Restart the bot process",
            ]
        ),
    )


async def main() -> None:
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not configured in bot/.env")

    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        log_exception(logger, "Bot startup failed", exc)
        raise
