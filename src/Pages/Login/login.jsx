import React, { useState } from "react";
import axios from "axios";
import styles from "./login.module.css";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = "http://127.0.0.1:8000"; // FastAPI backend URL

axios.interceptors.request.use(
  (config) => {
    config.withCredentials = true;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const loginUser = async (username, pass) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/login`,
      {
        user_id: username,
        password: pass,
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || "Login failed";
  }
};

const Login = ({ setIsLogged }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await loginUser(username, password);
      localStorage.setItem("token", response.access_token);
      setIsLogged(true);
      navigate("/chatbot");
      setMessage(response.message);
    } catch (err) {
      setMessage(err);
    }
  };

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleLogin}>
        <div className={styles.inputGroup}>
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className={styles.input}
            required
          />
        </div>

        <div className={styles.inputGroup}>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={styles.input}
            required
          />
        </div>

        <button type="submit" className={styles.button}>
          Login
        </button>

        <h3>Don't have an account?</h3>
        <button
          className={styles.button}
          onClick={() => {
            navigate("/register");
          }}
        >
          Register
        </button>

        {message && <div className={styles.message}>{message}</div>}
      </form>
    </div>
  );
};

export default Login;
