import React from "react";
import Header from "../../Components/Header/header";
import Footer from "../../Components/Footer/footer";
import { useNavigate } from "react-router-dom";
import styles from "./admin.module.css";

const API_BASE_URL = "http://127.0.0.1:8000/admin";

export default function Admin() {

    const navigate = useNavigate();


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

                if (!response.ok) {
                    navigate("/");
                }

            })
            .catch((error) => {
                console.error("Error:", error);
                navigate("/");
            });

            
    }, []);

    const get_login_data = () => {
        fetch(API_BASE_URL + "/login", {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            }
        })
            .then((response) => {
                console.log("response", response);
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }

    return (
        <>
            <Header />
            <div className={styles.tableContainer}>
                {/* Table 1: UserID and Rating */}
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>UserID</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>User1</td>
                            <td className={`${styles.rating} ${styles.high}`}>9</td>
                        </tr>
                        <tr>
                            <td>User2</td>
                            <td className={`${styles.rating} ${styles.medium}`}>6</td>
                        </tr>
                        <tr>
                            <td>User3</td>
                            <td className={`${styles.rating} ${styles.low}`}>3</td>
                        </tr>
                    </tbody>
                </table>

                {/* Table 2: IP List */}
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>192.168.1.1</td>
                        </tr>
                        <tr>
                            <td>10.0.0.2</td>
                        </tr>
                        <tr>
                            <td>172.16.0.3</td>
                        </tr>
                    </tbody>
                </table>

                {/* Table 3: Keystroke Table */}
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>UserID</th>
                            <th>Keystrokes</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>User1</td>
                            <td>120</td>
                        </tr>
                        <tr>
                            <td>User2</td>
                            <td>150</td>
                        </tr>
                        <tr>
                            <td>User3</td>
                            <td>80</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <Footer />
        </>
    );
}