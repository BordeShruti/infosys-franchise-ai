# 🔐 SecureAuth — User Authentication System

**Infosys Springboard Internship 7.0 | Milestone 1**

A secure, user-friendly authentication web application built using Python and Streamlit.

## ✨ Features

- 👤 User Registration and Login
- 🔒 Secure Password Hashing using bcrypt
- 🔑 Password Strength Validation
- ❓ Security Question-Based Password Recovery
- 📧 Email OTP Verification
- ⏳ OTP Expiry and Attempt Limits
- 🗄️ SQLite Database
- 🎨 Modern Authentication Interface
- 🛡️ JWT Authentication and Admin Dashboard *(if implemented)*

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| SQLite | User database |
| bcrypt | Password and security-answer hashing |
| PyJWT | JWT authentication, if implemented |
| Gmail SMTP / `smtplib` | Email OTP delivery |
| `hashlib` | Cryptographic digest generation |
| `secrets` | Secure OTP generation |
| Plotly | Dashboard visualizations, if implemented |
| Streamlit Option Menu | Navigation, if implemented |
| pyngrok | Public application tunneling |
| Google Colab | Notebook-based development |
| Git and GitHub | Version control and project hosting |

## 📸 Project Screenshots

### 1. Login Page
![Login Page](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Login%20Page.png)

### 2. Account Creation
![Account Create](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Account%20Create.png)

### 3. Password Recovery
![Password Recovery](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Reset%20Password%20-Via%20security%20code%20and%20otp.png)

### 4. Security Code Verification
![Security Code Verification](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Verify%20OTP%20%28security%20code%29.png)

### 5. Email OTP Verification
![Email OTP Verification](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Verify%20Email%20%28OTP%29.png)

### 6. OTP Email
![OTP on Email](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/OTP%20on%20email.png)

### 7. Reset Password
![Reset Password](https://raw.githubusercontent.com/BordeShruti/infosys-franchise-ai/main/Milestone1/images/Reset%20Password.png)



## ⚙️ Setup and Execution

### 1. Install Dependencies

In Google Colab, run:

```python
%pip install -q streamlit bcrypt pyjwt pyngrok
```

Install `plotly` and `streamlit-option-menu` only if your code uses them.

### 2. Configure Google Colab Secrets

Open the **Secrets** panel in Google Colab and add the required credentials.

| Secret | Purpose |
|---|---|
| `EMAIL_ADDRESS` | Sender Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password |
| `NGROK_AUTHTOKEN` | ngrok authentication token |
| `JWT_SECRET` | JWT signing key, if implemented |
| `ADMIN_PASSWORD` | Admin password, if implemented |

Enable notebook access for each secret your code requires.

### 3. Load Secrets

```python
import os
from google.colab import userdata

required_secrets = [
    "EMAIL_ADDRESS",
    "EMAIL_PASSWORD",
    "NGROK_AUTHTOKEN",
]

for key in required_secrets:
    os.environ[key] = userdata.get(key)
```

Load `JWT_SECRET` and `ADMIN_PASSWORD` similarly if required by your implementation.

**Security:** Never hardcode or upload passwords, email credentials, JWT secrets, or ngrok tokens to GitHub.

### 4. Run the Application

Execute the notebook cells in order. If your notebook starts Streamlit through ngrok, open the generated HTTPS URL.

### Run Locally (Alternative)

If you have an `app.py` file:

```bash
python -m pip install streamlit bcrypt pyjwt pyngrok
streamlit run app.py
```

Open the local URL displayed in your terminal.

## 🔒 Security Highlights

- Password and security-answer hashing
- Password complexity validation
- OTP verification and expiry checks
- Parameterized SQL queries
- Secret management through environment variables or Colab Secrets
- JWT expiry and role-based access, if implemented

## 🎯 Learning Outcomes

- Authentication and user management
- Password recovery using security questions and email OTP
- SQLite database operations
- Secure credential handling
- Streamlit web application development
- Basic application security practices


⭐ If you find this project useful, consider starring the repository!
