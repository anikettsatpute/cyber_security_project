import React, { useState, useRef } from "react";
import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_CHAT_API_URL || "http://127.0.0.1:8000/chat";
const KEYSTROKE_API_URL =
  process.env.REACT_APP_KEYSTROKE_API_URL || "http://127.0.0.1:8000/keystroke";

const ActionProvider = ({
  createChatBotMessage,
  setState,
  children,
  config,
}) => {
  const [keystrokeData, setKeystrokeData] = useState([]);
  const lastKeyTime = useRef(null);

  const handleKeyDown = (event) => {
    const currentTime = Date.now();
    const key = event.key;
    const interKeyDelay = lastKeyTime.current
      ? currentTime - lastKeyTime.current
      : null;

    const newKeystroke = { key, time: currentTime, interKeyDelay };
    setKeystrokeData((prevData) => {
      const threeMinutesAgo = currentTime - 3 * 60 * 1000;
      const filteredData = prevData.filter((k) => k.time >= threeMinutesAgo);
      return [...filteredData, newKeystroke];
    });

    lastKeyTime.current = currentTime;
  };

  const calculateAverageDelay = () => {
    const now = Date.now();
    const threeMinutesAgo = now - 3 * 60 * 1000;

    const recentKeystrokes = keystrokeData.filter(
      (k) => k.time >= threeMinutesAgo && k.interKeyDelay !== null
    );

    if (recentKeystrokes.length === 0) return 0;

    const totalDelay = recentKeystrokes.reduce(
      (sum, k) => sum + (k.interKeyDelay || 0),
      0
    );
    return totalDelay / recentKeystrokes.length;
  };

  const handleInput = async (message) => {
    const avgDelay = calculateAverageDelay();
    const user_input = {
      user_input: {
        entities: config.entity,
        query: message,
        avg_key_delay: !isNaN(avgDelay) && avgDelay > 0 ? avgDelay : undefined,
      },
    };

    try {
      if (user_input.user_input.avg_key_delay) {
        console.log(user_input);
        await axios.post(KEYSTROKE_API_URL, user_input, {
          headers: { "Content-Type": "application/json" },
        });
      }

      const response = await axios.post(
        API_BASE_URL,
        JSON.stringify(user_input),
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      const terminate_context = response.data.terminate_context;
      config = terminate_context
        ? { entity: {}, root_intent: null, intent: null, bot_response: null }
        : {
            ...config,
            entity: response.data.entities || {},
            root_intent: response.data.root_intent || null,
            intent: response.data.intent || null,
            bot_response: response.data.bot_response || null,
          };

      const botMessage = createChatBotMessage(response.data.bot_response);
      setState((state) => ({
        ...state,
        messages: [...state.messages, botMessage],
      }));
    } catch (error) {
      console.error("Error:", error);
    }
  };

  React.useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div>
      {React.Children.map(children, (child) => {
        return React.cloneElement(child, {
          actions: { handleInput },
        });
      })}
    </div>
  );
};

export default ActionProvider;
