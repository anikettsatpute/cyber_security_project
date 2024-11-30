import "./App.css";
import Login from "./Pages/Login/login";
import Register from "./Pages/Register/register";
import Chat_bot from "./Pages/Chatbot/chatbot";
import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
  useNavigate,
} from "react-router-dom";

function App() {
  const [isLogged, setIsLogged] = React.useState(false);

  return (
    // <Router>
    //   <Routes>
    //     <Route path="/" element={<Login setIsLogged={setIsLogged} />} />
    //     <Route
    //       path="/chatbot"
    //       element={isLogged ? <Chat_bot /> : <Navigate to="/" />}
    //     />
    //   </Routes>
    // </Router>
    <>
      <Chat_bot />
    </>
    // <>
    //   <Login />
    // </>
  );
}

export default App;
