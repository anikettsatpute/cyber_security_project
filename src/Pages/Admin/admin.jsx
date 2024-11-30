import React from "react";
import Header from "../../Components/Header/header";
import Footer from "../../Components/Footer/footer";
import { useNavigate } from "react-router-dom";

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

    return (
        <>
            <Header />
            <div>

            </div>
            <Footer />
        </>
    );
}