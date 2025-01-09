const { Telegraf } = require('telegraf');
const { Octokit } = require('@octokit/rest');
const fs = require('fs').promises;

// Initialize bot and GitHub client
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

const REPO_OWNER = 'nobuhibiki';
const REPO_NAME = 'nobujournal';
const JOURNAL_FILE = 'journal.json';

async function saveEntry(entry) {
  try {
    // Get current file if it exists
    let currentContent;
    try {
      const { data } = await octokit.repos.getContent({
        owner: REPO_OWNER,
        repo: REPO_NAME,
        path: JOURNAL_FILE,
      });
      currentContent = JSON.parse(Buffer.from(data.content, 'base64').toString());
    } catch (e) {
      currentContent = { entries: [] };
    }

    // Add new entry
    currentContent.entries.push({
      ...entry,
      timestamp: new Date().toISOString(),
    });

    // Update or create file
    await octokit.repos.createOrUpdateFileContents({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: JOURNAL_FILE,
      message: 'Add journal entry',
      content: Buffer.from(JSON.stringify(currentContent, null, 2)).toString('base64'),
      sha: currentContent.sha,
    });

    return true;
  } catch (error) {
    console.error('Error saving entry:', error);
    return false;
  }
}

// Command handlers
bot.command('start', async (ctx) => {
  await ctx.reply(
    'Welcome to your GitHub-based Journal Bot! 📝\n\n' +
    'Just send me any message and I\'ll save it to your private GitHub repo.\n' +
    'Use /view to see recent entries\n' +
    'Use /mood [emotion] to log your current mood'
  );
});

bot.command('mood', async (ctx) => {
  const mood = ctx.message.text.split('/mood ')[1];
  if (!mood) {
    await ctx.reply('Please specify your mood: /mood [emotion]');
    return;
  }

  const success = await saveEntry({
    type: 'mood',
    content: mood,
    userId: ctx.from.id,
  });

  if (success) {
    await ctx.reply(`Mood "${mood}" recorded! 🎭`);
  } else {
    await ctx.reply('Sorry, there was an error saving your mood 😕');
  }
});

bot.command('view', async (ctx) => {
  try {
    const { data } = await octokit.repos.getContent({
      owner: REPO_OWNER,
      repo: REPO_NAME,
      path: JOURNAL_FILE,
    });

    const journal = JSON.parse(Buffer.from(data.content, 'base64').toString());
    const userEntries = journal.entries
      .filter(entry => entry.userId === ctx.from.id)
      .slice(-5);

    if (userEntries.length === 0) {
      await ctx.reply('No entries found.');
      return;
    }

    const message = userEntries
      .map(entry => {
        const date = new Date(entry.timestamp).toLocaleString();
        return `📅 ${date}\n${entry.content}\n`;
      })
      .join('\n');

    await ctx.reply(`Your recent entries:\n\n${message}`);
  } catch (error) {
    await ctx.reply('Sorry, there was an error retrieving your entries 😕');
  }
});

// Handle regular messages
bot.on('text', async (ctx) => {
  if (ctx.message.text.startsWith('/')) return;

  const success = await saveEntry({
    type: 'entry',
    content: ctx.message.text,
    userId: ctx.from.id,
  });

  if (success) {
    await ctx.reply('Entry saved! 📝');
  } else {
    await ctx.reply('Sorry, there was an error saving your entry 😕');
  }
});
