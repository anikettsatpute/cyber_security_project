import React from "react";
import styles from "./header.module.css";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000/logout";

const Header = ({setIsLogged}) => {

  const navigate = useNavigate();

  const logoutUser = async () => {
    try {
      const response = await fetch(API_BASE_URL, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        }
      });
      setIsLogged(false);
      navigate("/");
      console.log("logout response", response);
      
    } catch (error) {
      throw error.response?.data?.detail || "Logout failed"
    }
  }


  return (
    <header className={styles.header}>
      <div className={styles.logo}>Generic Ecommerce Chatbot</div>
      <div className={styles.auth}>
        
          <button onClick={() => navigate("/admin")} className={styles.button}>
            Admin
          </button>

          <button onClick={logoutUser} className={styles.button}>
            Logout
          </button>
      </div>
    </header>
  );
};

export default Header;
