import React from "react";
import Header from "../../Components/Header/header";
import Footer from "../../Components/Footer/footer";
import { useNavigate } from "react-router-dom";
import styles from "./admin.module.css";

const API_BASE_URL = "http://127.0.0.1:8000/admin";
const API_ANALYTICS_URL = "http://127.0.0.1:8000/loginAnomalies";

export default function Admin() {

    const navigate = useNavigate();
    const [loginAnomalies, setLoginAnomalies] = React.useState([]);
    const [ipAnomalies, setIpAnomalies] = React.useState([]);


    // const setLoginAnomaliesData = (data) => {
    //     setLoginAnomalies(data);
    // };

    // const setIpAnomaliesData = (data) => {
    //     setIpAnomalies(data);
    // }
    

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

    
    React.useEffect(() => {

        fetch(API_ANALYTICS_URL, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            }
        })
            .then((response) => {
                console.log("response", response);


                   // response : 
                // {
                //     "anomalies_users": [
                //         {
                //             "user_id": 20101,
                //             "anomaly_score_user_id": -0.10221721795326133
                //         }
                //     ],
                //     "anomalies_ips": [
                //         {
                //             "ip_address": "127.0.0.1",
                //             "anomaly_score_ip_address": -0.021573861973326225
                //         },
                //         {
                //             "ip_address": "127.0.0.1",
                //             "anomaly_score_ip_address": -0.0206776723383576
                //         }
                //     ]
                // }

                response.json().then((data) => {
                    console.log("data", data);

                    const loginAnomaliesData = data.anomalies_users.map((user) => {
                        return {
                            id: user.user_id,
                            userID: user.user_id,
                            rating: user.anomaly_score_user_id
                        };
                    });

                    const ipAnomaliesData = data.anomalies_ips.map((ip) => {
                        return {
                            id: ip.ip_address,
                            ipAddress: ip.ip_address,
                            rating: ip.anomaly_score_ip_address
                        };
                    });

                    //  take maximum rating of same user id

                    const loginAnomaliesDataMap = new Map();
                    loginAnomaliesData.forEach((loginAnomaly) => {
                        if (loginAnomaliesDataMap.has(loginAnomaly.userID)) {
                            if (loginAnomaliesDataMap.get(loginAnomaly.userID) < loginAnomaly.rating) {
                                loginAnomaliesDataMap.set(loginAnomaly.userID, loginAnomaly.rating);
                            }
                        } else {
                            loginAnomaliesDataMap.set(loginAnomaly.userID, loginAnomaly.rating);
                        }
                    });

                    // take maximum rating of same ip address
                    const ipAnomaliesDataMap = new Map();
                    ipAnomaliesData.forEach((ipAnomaly) => {
                        if (ipAnomaliesDataMap.has(ipAnomaly.ipAddress)) {
                            if (ipAnomaliesDataMap.get(ipAnomaly.ipAddress) < ipAnomaly.rating) {
                                ipAnomaliesDataMap.set(ipAnomaly.ipAddress, ipAnomaly.rating);
                            }
                        } else {
                            ipAnomaliesDataMap.set(ipAnomaly.ipAddress, ipAnomaly.rating);
                        }
                    });

                    // convert map to array and take absolute value of rating multiplied by 100
                    setLoginAnomalies(Array.from(loginAnomaliesDataMap).map(([key, value]) => {
                        return {
                            id: key,
                            userID: key,
                            rating: Math.abs(value) * 100
                        };
                    }));
                    setIpAnomalies(Array.from(ipAnomaliesDataMap).map(([key, value]) => {
                        return {
                            id: key,
                            ipAddress: key,
                            rating: Math.abs(value) * 100
                        };
                    }));
                });

            })
            .catch((error) => {
                console.error("Error:", error);
            });

            
    }, []);

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
                        {loginAnomalies.map((loginAnomaly) => (
                            <tr key={loginAnomaly.id}>
                                <td
                                    className={
                                        loginAnomaly.rating > 10.13 ? styles.low : 
                                        loginAnomaly.rating > 10 ? styles.medium :
                                        styles.high
                                    }
                                >{loginAnomaly.userID}</td>
                                <td
                                    className={
                                        loginAnomaly.rating > 10.13 ? styles.low : 
                                        loginAnomaly.rating > 10 ? styles.medium :
                                        styles.high
                                    }
                                >{loginAnomaly.rating}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Table 2: IP List */}
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ipAnomalies.map((ipAnomaly) => (
                            <tr key={ipAnomaly.id}>
                                <td  className={
                                    ipAnomaly.rating > 2.067 ? styles.low : 
                                    styles.high
                                }>{ipAnomaly.ipAddress}</td>
                                <td className={
                                    ipAnomaly.rating > 2.067 ? styles.low : 
                                    styles.high
                                }>{ipAnomaly.rating}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Table 3: Keystroke Table */}
                {/* <table className={styles.table}>
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
                </table> */}
            </div>
            <Footer />
        </>
    );
}