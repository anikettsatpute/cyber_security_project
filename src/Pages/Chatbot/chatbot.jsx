import React from "react";
import Chatbot  from "react-chatbot-kit";
import { styles } from "./chatbot.module.css";
import config from "./config";
import MessageParser from "./message_parser";
import ActionProvider from "./action_provider";
import 'react-chatbot-kit/build/main.css'

import Header from "../../Components/Header/header";
import Footer from "../../Components/Footer/footer";
export default function Chat_bot() {
  return (
    <>
      <Header />
      <h1>Chatbot</h1>

      <Chatbot
        config={config}
        messageParser={MessageParser}
        actionProvider={ActionProvider}
      />

      <Footer />
    </>
  );
}

