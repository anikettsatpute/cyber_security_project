import React, { useState } from "react";
import Chatbot  from "react-chatbot-kit";
import 'react-chatbot-kit/build/main.css'
import "./chatbot.css";
import config from "./config";
import MessageParser from "./message_parser";
import ActionProvider from "./action_provider";
import Header from "../../Components/Header/header";
import Footer from "../../Components/Footer/footer";
export default function Chat_bot({setIsLogged}) {
  return (
    <>
      <Header setIsLogged={setIsLogged}/>
      <Chatbot
        config={config}
        messageParser={MessageParser}
        actionProvider={(props) => (
          <ActionProvider {...props} config={config} />
        )}
      />
      <Footer />
    </>
  );
}

