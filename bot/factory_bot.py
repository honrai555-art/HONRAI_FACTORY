import asyncio
import os
import subprocess
import sys
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from bot.commands.blender import run_blender
from bot.commands.comfy import run_comfy_test
from bot.commands.gitpull import run_gitpull
from bot.commands.logs import get_latest_logs
from bot.commands.manga import run_manga
from bot.commands.pipeline_manga import run_pipeline_manga
from bot.commands.status import get_status
from bot.commands.unity import run_unity
from bot.commands.world import format_world_summary, parse_world_instruction, run_world_request
from bot.utils.env_check import format_env_report, validate_env
from bot.utils.logger import get_logger, log_exception

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, encoding="utf-8-sig")

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
ALLOWED_CHANNEL_ID = os.getenv("ALLOWED_CHANNEL_ID", "").strip()

RESTART_EXIT_CODE = 10

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


def _validate_startup() -> None:
    if not intents.message_content:
        warning = (
            "message_content intent is disabled. "
            "Prefix commands such as !help will not work. "
            "Enable it in the Discord Developer Portal."
        )
        logger.warning(warning)
        print(f"WARNING: {warning}", file=sys.stderr)

    env_result = validate_env(project_dir=PROJECT_DIR)
    if env_result.warnings or env_result.missing_recommended:
        report = format_env_report(env_result)
        logger.warning("Environment check:\n%s", report)
        print(f"WARNING:\n{report}", file=sys.stderr)

    if not env_result.ok:
        report = format_env_report(env_result)
        logger.error("Required environment variables are missing:\n%s", report)
        print(f"ERROR:\n{report}", file=sys.stderr)
        raise RuntimeError("Required environment variables are missing. See logs/bot.log")


def _spawn_restart_process() -> None:
    env = os.environ.copy()
    env.pop("HONRAI_WATCHDOG", None)

    popen_kwargs: dict = {
        "cwd": str(PROJECT_DIR),
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    if sys.platform == "win32":
        popen_kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )

    subprocess.Popen(
        [sys.executable, str(BASE_DIR / "factory_bot.py")],
        **popen_kwargs,
    )
    logger.info("Spawned replacement bot process.")


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
        return True

    if ctx.channel.id != allowed_id:
        logger.info(
            "Ignored command from unauthorized channel: channel_id=%s author=%s command=%s",
            ctx.channel.id,
            ctx.author,
            ctx.message.content,
        )
        await ctx.reply(
            "このチャンネルでは Bot コマンドを受け付けていません。\n"
            f"ALLOWED_CHANNEL_ID={allowed_id} のチャンネルで実行してください。",
            mention_author=False,
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


@bot.command(name="blender")
async def blender_command(ctx: commands.Context) -> None:
    logger.info("Command received: blender")
    await send_command_result(ctx, "BLENDER LINE", run_blender())


@bot.command(name="world")
async def world_command(ctx: commands.Context, *, instruction: str = "") -> None:
    logger.info("Command received: world content=%s", instruction)

    if not instruction.strip():
        await send_command_result(
            ctx,
            "WORLD",
            "Usage: !world 火山の街道 鳥居 溶岩 宿場町 橋 ホンライくん",
        )
        return

    try:
        preview = parse_world_instruction(instruction)
    except ValueError as exc:
        await send_command_result(ctx, "WORLD ERROR", str(exc))
        return

    await ctx.reply(
        "**world request accepted**\n"
        f"```text\n{format_world_summary(preview)}\n```",
        mention_author=False,
    )

    try:
        await asyncio.to_thread(run_world_request, preview)
    except Exception as exc:
        log_exception(logger, "world build failed", exc)
        await send_command_result(ctx, "WORLD BUILD ERROR", str(exc))


@bot.command(name="logs")
async def logs_command(ctx: commands.Context) -> None:
    logger.info("Command received: logs")
    await send_command_result(ctx, "LATEST LOGS", get_latest_logs())


@bot.command(name="restart")
async def restart_command(ctx: commands.Context) -> None:
    logger.info("Command received: restart by %s", ctx.author)
    await ctx.reply("Restarting HONRAI_FACTORY Bot...", mention_author=False)

    await asyncio.sleep(1.5)

    under_watchdog = os.environ.get("HONRAI_WATCHDOG") == "1"
    if under_watchdog:
        logger.info("Restart requested under watchdog. Exiting for supervisor restart.")
    else:
        logger.info("Restart requested without watchdog. Spawning replacement process.")
        _spawn_restart_process()

    try:
        await bot.close()
    except Exception as exc:
        log_exception(logger, "Error while closing bot for restart", exc)

    os._exit(RESTART_EXIT_CODE)


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
                "!unity    - Build Unity world from world_request.json",
                "!blender  - Optimize FBX, export glTF, auto-import to Unity",
                "!world    - Update world_request.json and build Unity world",
                "!logs     - Show latest bot and error logs",
                "!restart  - Restart the bot process",
            ]
        ),
    )


async def main() -> None:
    _validate_startup()

    if not TOKEN:
        message = (
            "DISCORD_TOKEN is not configured in bot/.env. "
            "Set a valid token and restart the bot."
        )
        logger.error(message)
        print(f"ERROR: {message}", file=sys.stderr)
        raise RuntimeError(message)

    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    exit_code = 0
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as exc:
        log_exception(logger, "Bot startup failed", exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)
