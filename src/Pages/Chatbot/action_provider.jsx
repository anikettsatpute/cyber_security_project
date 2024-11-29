import React from 'react';

const ActionProvider = ({ createChatBotMessage, setState, children }) => {
  const handleInput = (message) => {
    const botMessage = createChatBotMessage("Hello, how can I help?");

    setState((state) => ({
      ...state,
      messages: [...state.messages, botMessage],
    }));

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