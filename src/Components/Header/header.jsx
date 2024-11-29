import React from "react";
import styles from "./header.module.css";

const Header = ({ isLoggedIn, onLoginToggle }) => {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>MyLogo</div>
      <div className={styles.auth}>
        {isLoggedIn ? (
          <button onClick={onLoginToggle} className={styles.button}>
            Logout
          </button>
        ) : (
          <button onClick={onLoginToggle} className={styles.button}>
            Login
          </button>
        )}
      </div>
    </header>
  );
};

export default Header;
