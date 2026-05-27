require('dotenv').config();

const { REST, Routes } = require('discord.js');
const fs = require('node:fs');
const path = require('node:path');

const token = process.env.DISCORD_TOKEN;
const clientId = process.env.DISCORD_CLIENT_ID;
const guildId = process.env.DISCORD_GUILD_ID;

if (!token || !clientId || !guildId) {
  console.error(
    '[deploy-commands] .env に DISCORD_TOKEN / DISCORD_CLIENT_ID / DISCORD_GUILD_ID を設定してください',
  );
  process.exit(1);
}

const commandsPath = path.join(__dirname, 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter((file) => file.endsWith('.js'));

const commands = commandFiles.map((file) => {
  const command = require(path.join(commandsPath, file));
  return command.data.toJSON();
});

const rest = new REST({ version: '10' }).setToken(token);

(async () => {
  try {
    console.log(`[deploy-commands] ${commands.length} 件のコマンドを guild に登録します…`);

    await rest.put(Routes.applicationGuildCommands(clientId, guildId), {
      body: commands,
    });

    console.log('[deploy-commands] 登録完了（開発サーバーのみ）');
  } catch (error) {
    console.error('[deploy-commands] 登録失敗:', error);
    process.exit(1);
  }
})();
