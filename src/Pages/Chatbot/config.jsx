import { createChatBotMessage } from 'react-chatbot-kit';

const config = {
  initialMessages: [createChatBotMessage(`Hello! How can I help you today?`)],
  entity: {},
  root_intent: null,
  intent: null,
  bot_response: null,
};

export default config;