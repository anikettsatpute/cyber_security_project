import React from 'react';
import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000/chat"; // FastAPI backend URL

const ActionProvider = ({ createChatBotMessage, setState, children, config }) => {
  const handleInput = async (message) => {

    // create query for API

    var user_input = {
      user_input : {
        entities: config.entity,
        query: message
      }
    }
    if (config.root_intent) {
      user_input.user_input.root_intent = config.root_intent;
    }
    if (config.intent) {
      user_input.user_input.intent = config.intent;
    }
    if (config.bot_response) {
      user_input.user_input.bot_response = config.bot_response;
    }
    user_input = JSON.stringify(user_input);
    console.log("user_input", user_input);
    const response = await axios.post(API_BASE_URL, user_input, {
      headers: {
        "Content-Type": "application/json",
      }
    });
    console.log("response", response);
    const terminate_context = response.data.terminate_context;

    const botMessage = createChatBotMessage(response.data.bot_response);
    if (terminate_context) {
      config.entity = {};
      config.root_intent = null;
      config.intent = null;
      config.bot_response = null;
    }
    else {
      config.entity = response.data.entities;
      config.root_intent = response.data.root_intent;
      config.intent = response.data.intent;
      config.bot_response = response.data.bot_response;
    }

    console.log("config", config);
    

    const state = setState((state) => ({
      ...state,
      messages: [...state.messages, botMessage],
    }

    ));
    console.log("state", state);
  };

  return (
    <div>
      {React.Children.map(children, (child) => {
        return React.cloneElement(child, {
          actions: {
            handleInput: handleInput
          },
        });
      })}
    </div>
  );
};



export default ActionProvider;