const { SlashCommandBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ping')
    .setDescription('Bot の応答速度を確認します'),
  async execute(interaction) {
    const sent = await interaction.reply({
      content: 'Pong! 計測中…',
      fetchReply: true,
    });

    const latency = sent.createdTimestamp - interaction.createdTimestamp;
    const apiLatency = Math.round(interaction.client.ws.ping);

    await interaction.editReply(
      `Pong!\nBot 応答: ${latency}ms\nAPI: ${apiLatency}ms`,
    );
  },
};
