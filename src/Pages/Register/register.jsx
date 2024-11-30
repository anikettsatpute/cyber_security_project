import React from "react";
import styles from "./register.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";
const API_BASE_URL = "http://127.0.0.1:8000"


const registerUser = async (username, password, name, email, address, phone) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/register`, {
      user_id: username,
      password: password,
      name: name,
      email: email,
      address: address,
      phone_number: phone
    }, {
      headers: {
        "Content-Type": "application/json",
      }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data?.detail || "Registration failed";
  }
}

export default function Register({setIsLogged}) {
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [name, setName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [address, setAddress] = React.useState("");
  const [phone, setPhone] = React.useState("");
  const [message, setMessage] = React.useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await registerUser(username, password, name, email, address, phone);
      setIsLogged(true);
      navigate("/chatbot");
      setMessage(response.message);
    } catch (err) {
      setMessage(err);
    }
  }

  return (
    <div className={styles.container}>
    <h1>Register</h1>
    <form className={styles.form} onSubmit={handleRegister}>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="text"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="text"
        placeholder="Address"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        className={styles.input}
        required
      />
      <input
        type="text"
        placeholder="Phone"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        className={styles.input}
        required
      />
      <button
        type="submit"
        className={styles.button}
      >
        Register
      </button>
    </form>
    {message && <p>{message}</p>}
  </div>
      );
}
