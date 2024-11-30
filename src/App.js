import "./App.css";
import Login from "./Pages/Login/login";
import Register from "./Pages/Register/register";
import Chat_bot from "./Pages/Chatbot/chatbot";
import Admin from "./Pages/Admin/admin";
import React from "react";
import { BrowserRouter as Router, Route,Navigate, Routes, useNavigate } from "react-router-dom";
import Header from "./Components/Header/header";
import Footer from "./Components/Footer/footer";
const API_BASE_URL = "http://127.0.0.1:8000/protected";

function App() {
  const [isLogged, setIsLogged] = React.useState(false);
  // fetch cookies to check if user is logged in
  React.useEffect(() => {
    
    fetch(API_BASE_URL, {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      }
    })
    .then((response) => {
      console.log("response", response);
      
      if (response.ok) {
        console.log("response.ok", response.ok);
        
        setIsLogged(true);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      setIsLogged(false);
    });
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={isLogged ? <Navigate to="/chatbot" /> : <Login setIsLogged={setIsLogged} />} />
        <Route path="/chatbot"
          element={isLogged ? <Chat_bot setIsLogged={setIsLogged}/> : <Navigate to="/" />}
        />
        <Route path="/register" element={<Register setIsLogged={setIsLogged} />} />
        <Route path="/admin" element={<Admin/>} />
      </Routes>
    </Router>
  );
}

export default App;
