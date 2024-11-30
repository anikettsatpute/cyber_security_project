# Secure AI-Powered Customer Service Chatbot for E-commerce

## Contributors

- Satpute Aniket Tukaram
- Harshit Pant
- Mahin Bansal

## Overview

- Develop a secure, AI-powered customer service chatbot for an e-commerce platform, focusing on protecting customer data, preventing security breaches, and providing safe, automated customer support.s

## Tech Stack

- Frontend: ReactJS
- Backend: FastAPI
- Database: SQLite

## Features

- Secure login and registration system
- Secure chatbot for customer service
- Flagging of malicious logins and keystrokes
- Secured authentication and authorization

## Installation

1. Clone the repository
    - `git clone https://github.com/anikettsatpute/cyber_security_project.git`
    - `cd cyber_security_project`
2. Install the required dependencies
    - `pip install -r requirements.txt`
    - `npm install`
3. Run the backend server
    - `cd backend`
    - `source venv/bin/activate`
    - `uvicorn main:app --reload`
4. Run the frontend server
    - `npm start`
5. Visit `localhost:3000` in your browser

## Routes

- `/`: login page
- `/register`: registration page
- `/chatbot`: chatbot page
- `/admin`: admin page

## File Structure

- Database: `backend/ecommerce.db`
- Controllers: `backend/controller.py`
- Models: `backend/models.py`
- Main: `backend/main.py`
- AI Model: `backend/AIModels/final_model.py`


## API Endpoints

- `/login`: POST request to login
- `/register`: POST request to register
- `/chatbot`: POST request to chatbot
- `/admin`: GET request to admin
- `/loginAnomalies`: GET request to get login anomalies
- `/keystroke`: GET request to get keystroke anomalies
- `/logout`: GET request to logout

## Cookies

- HTTPOnly cookies are used for session management
- Secure and SameSite cookies are used for security
- The cookies contain access tokens created from user_id and timestamp

## Screenshots

- Register Page
![Login Page](./public/screenshots/register.png)

- Login Page
![Login Page](./public/screenshots/login.png)

- Chatbot Page
![Chatbot Page](./public/screenshots/chatbot.png)

- Admin Page
![Admin Page](./public/screenshots/admin.png)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ReactJS Documentation](https://reactjs.org/)
- [SQLite Documentation](https://www.sqlite.org/index.html)
- [Secure Cookies](https://owasp.org/www-community/HttpOnly)
