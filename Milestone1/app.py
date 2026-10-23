
import re
import sqlite3
import hashlib
import os
import smtplib
import secrets
import time
import html

from email.message import EmailMessage
from contextlib import closing

import bcrypt
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Infosys Portal | Secure Access",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_NAME = "infosys_portal.db"

OTP_EXPIRY_SECONDS = 300
OTP_RESEND_COOLDOWN = 30
OTP_MAX_ATTEMPTS = 5


# =========================================================
# DATABASE
# =========================================================
def get_connection():
    return sqlite3.connect(DB_NAME, timeout=10)


def init_db():
    with closing(get_connection()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        }

        if "sec_q" not in columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN sec_q TEXT"
            )

        if "sec_a_hash" not in columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN sec_a_hash TEXT"
            )

        conn.commit()


# =========================================================
# PASSWORD HELPERS
# =========================================================
def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def validate_password(password):
    if len(password.encode("utf-8")) > 72:
        return False, "Password must not exceed 72 UTF-8 bytes."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if any(char.isspace() for char in password):
        return False, "Password must not contain spaces or whitespace."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter (A-Z)."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter (a-z)."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number (0-9)."

    if not re.search(r"[^A-Za-z0-9\s]", password):
        return False, "Password must contain at least one special character, such as @, #, or !."

    return True, "Password meets all requirements."


# =========================================================
# SECURITY ANSWER HELPERS
# =========================================================
def hash_security_answer(answer):
    normalized = answer.strip().casefold().encode("utf-8")
    digest = hashlib.sha256(normalized).digest()

    return bcrypt.hashpw(
        digest,
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_security_answer_hash(answer, stored_hash):
    if not stored_hash or not answer.strip():
        return False

    normalized = answer.strip().casefold().encode("utf-8")
    digest = hashlib.sha256(normalized).digest()

    try:
        return bcrypt.checkpw(
            digest,
            stored_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


# =========================================================
# EMAIL OTP — SEND EMAIL
# =========================================================
def send_otp_email(email, otp):
    smtp_host = os.getenv(
        "SMTP_HOST", "smtp.gmail.com"
    ).strip()

    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
    sender_email = os.getenv(
        "SMTP_FROM", smtp_user
    ).strip()

    try:
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError:
        return False, "SMTP_PORT must be a valid port number."

    if not smtp_user or not smtp_password or not sender_email:
        return False, (
            "Email settings are missing. Configure SMTP_USER, "
            "SMTP_PASSWORD and SMTP_FROM in your terminal."
        )
    # Create email message
    message = EmailMessage()
    message["Subject"] = "Infosys Portal | Password Reset OTP"
    message["From"] = sender_email
    message["To"] = email

    # Plain-text version for email clients that do not support HTML
    message.set_content(
        f"""Hello,

Your Infosys Portal password reset OTP is: {otp}

This OTP is valid for 5 minutes.
You have a maximum of 5 verification attempts.

Do not share this OTP with anyone.

If you did not request a password reset, please ignore this email.

Regards,
Infosys Portal Security Team
"""
    )

    # HTML email template
    message.add_alternative(
        f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infosys Portal Password Reset</title>
</head>

<body style="margin:0; padding:0; background-color:#f3f6fb;
             font-family:Arial,Helvetica,sans-serif; color:#263650;">

    <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
           style="background-color:#f3f6fb; padding:30px 12px;">
        <tr>
            <td align="center">

                <table role="presentation" width="100%" cellspacing="0"
                       cellpadding="0"
                       style="max-width:560px; background:#ffffff;
                              border:1px solid #e1e8f2;
                              border-radius:14px; overflow:hidden;">

                    <!-- Header -->
                    <tr>
                        <td align="center"
                            style="background:#245bd6; padding:28px 20px;">
                            <div style="font-size:28px; color:#ffffff;
                                        font-weight:bold;">
                                ✦ Infosys Portal
                            </div>

                            <div style="font-size:13px; color:#e7efff;
                                        margin-top:8px;">
                                Secure Account Access
                            </div>
                        </td>
                    </tr>

                    <!-- Email content -->
                    <tr>
                        <td style="padding:30px 26px;">

                            <h2 style="margin:0 0 18px; color:#173b78;
                                       font-size:23px;">
                                Password Reset Request
                            </h2>

                            <p style="font-size:15px; line-height:1.7;">
                                Hello,
                            </p>

                            <p style="font-size:15px; line-height:1.7;">
                                We received a request to reset your
                                Infosys Portal password. Use the
                                verification code below to continue.
                            </p>

                            <!-- OTP box -->
                            <div style="background:#f0f5ff;
                                        border:1px solid #d6e4ff;
                                        border-radius:12px;
                                        padding:24px 12px;
                                        text-align:center;
                                        margin:24px 0;">

                                <div style="font-size:12px;
                                            color:#61718b;
                                            letter-spacing:2px;
                                            margin-bottom:12px;">
                                    YOUR VERIFICATION CODE
                                </div>

                                <div style="font-size:34px;
                                            font-weight:bold;
                                            letter-spacing:8px;
                                            color:#245bd6;">
                                    {otp}
                                </div>

                                <div style="font-size:13px;
                                            color:#61718b;
                                            margin-top:12px;">
                                    This code expires in 5 minutes
                                </div>
                            </div>

                            <!-- Security reminder -->
                            <div style="background:#fff8e8;
                                        border-left:4px solid #e9a23b;
                                        padding:14px;
                                        margin:22px 0;
                                        border-radius:5px;">

                                <p style="margin:0; font-size:13px;
                                          line-height:1.7; color:#79551a;">
                                    <strong>Security reminder</strong><br>
                                    You have a maximum of 5 verification
                                    attempts. Never share this OTP with
                                    anyone.
                                </p>
                            </div>

                            <p style="font-size:14px; line-height:1.7;">
                                If you did not request a password reset,
                                please ignore this email. Your password
                                will not change unless the reset process
                                is completed.
                            </p>

                            <p style="font-size:14px; line-height:1.7;
                                      margin-top:24px;">
                                Regards,<br>
                                <strong style="color:#173b78;">
                                    Infosys Portal Security Team
                                </strong>
                            </p>

                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td align="center"
                            style="background:#f8faff;
                                   border-top:1px solid #e7edf6;
                                   padding:18px 15px;">

                            <p style="font-size:11px; color:#8491a5;
                                      line-height:1.7; margin:0;">
                                Automated security notification.
                                Please do not reply to this email.
                            </p>

                            <p style="font-size:11px; color:#8491a5;
                                      margin:6px 0 0;">
                                © Infosys Portal · Secure Authentication
                            </p>

                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>
""",
        subtype="html",
    )

    # Send email through Gmail SMTP
    try:
        with smtplib.SMTP(
            smtp_host, smtp_port, timeout=20
        ) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(message)

        return True, "OTP sent to your registered email address."

    except smtplib.SMTPAuthenticationError:
        print("OTP email error: Gmail authentication failed.")
        return False, (
            "Gmail authentication failed. Check your email address "
            "and Google App Password."
        )

    except (OSError, smtplib.SMTPException) as exc:
        print(
            f"OTP email delivery failed: "
            f"{type(exc).__name__}: {exc}"
        )
        return False, (
            "Unable to send the OTP. Check the terminal for details "
            "and verify your SMTP settings."
        )

# =========================================================
# EMAIL OTP — CREATE AND STORE OTP HASH
# =========================================================
def create_and_send_otp(email):
    now = time.time()
    last_sent = st.session_state.get("otp_last_sent_at", 0)

    if now - last_sent < OTP_RESEND_COOLDOWN:
        remaining = max(
            1,
            OTP_RESEND_COOLDOWN - int(now - last_sent)
        )
        return False, (
            f"Please wait {remaining} seconds before requesting another OTP."
        )

    otp = f"{secrets.randbelow(1_000_000):06d}"

    success, message = send_otp_email(email, otp)

    if not success:
        return False, message

    # Store only a hash of the OTP, not the original code.
    st.session_state.otp_hash = hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()

    st.session_state.otp_created_at = time.time()
    st.session_state.otp_last_sent_at = time.time()
    st.session_state.otp_attempts = 0
    st.session_state.reset_verified = False

    return True, message


# =========================================================
# EMAIL OTP — VERIFY OTP
# =========================================================
def verify_email_otp(entered_otp):
    otp_hash = st.session_state.get("otp_hash")
    created_at = st.session_state.get("otp_created_at", 0)
    attempts = st.session_state.get("otp_attempts", 0)

    if not otp_hash:
        return False, "No active OTP. Please request a new OTP."

    if time.time() - created_at > OTP_EXPIRY_SECONDS:
        st.session_state.otp_hash = None
        return False, "OTP expired. Please request a new one."

    if attempts >= OTP_MAX_ATTEMPTS:
        st.session_state.otp_hash = None
        return False, "Too many attempts. Please request a new OTP."

    if not entered_otp.isdigit() or len(entered_otp) != 6:
        return False, "Enter all 6 digits of the OTP."

    st.session_state.otp_attempts += 1

    entered_hash = hashlib.sha256(
        entered_otp.encode("utf-8")
    ).hexdigest()

    if secrets.compare_digest(entered_hash, otp_hash):
        st.session_state.otp_hash = None
        st.session_state.reset_verified = True
        return True, "Email OTP verified successfully."

    return False, "Incorrect OTP. Please try again."


# =========================================================
# USER FUNCTIONS
# =========================================================
def create_user(username, email, password, question, answer):
    password_hash = hash_password(password)
    answer_hash = hash_security_answer(answer)

    try:
        with closing(get_connection()) as conn:
            conn.execute("""
                INSERT INTO users
                    (username, email, password_hash, sec_q, sec_a_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (
                username.strip(),
                email.strip().lower(),
                password_hash,
                question,
                answer_hash,
            ))
            conn.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."


def authenticate_user(login_id, password):
    with closing(get_connection()) as conn:
        row = conn.execute("""
            SELECT username, email, password_hash
            FROM users
            WHERE username = ? COLLATE NOCASE
               OR email = ? COLLATE NOCASE
        """, (
            login_id.strip(),
            login_id.strip()
        )).fetchone()

    if not row:
        return None

    username, email, password_hash = row

    try:
        valid = bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        valid = False

    if valid:
        return {
            "username": username,
            "email": email
        }

    return None


def get_security_question(email):
    with closing(get_connection()) as conn:
        row = conn.execute("""
            SELECT sec_q
            FROM users
            WHERE email = ? COLLATE NOCASE
        """, (email.strip(),)).fetchone()

    return row[0] if row else None


def verify_security_answer(email, answer):
    with closing(get_connection()) as conn:
        row = conn.execute("""
            SELECT sec_a_hash
            FROM users
            WHERE email = ? COLLATE NOCASE
        """, (email.strip(),)).fetchone()

    if not row:
        return False

    return verify_security_answer_hash(answer, row[0])


def update_password(email, new_password):
    password_hash = hash_password(new_password)

    with closing(get_connection()) as conn:
        cursor = conn.execute("""
            UPDATE users
            SET password_hash = ?
            WHERE email = ? COLLATE NOCASE
        """, (
            password_hash,
            email.strip()
        ))

        conn.commit()
        return cursor.rowcount > 0


# =========================================================
# INITIALIZATION
# =========================================================
init_db()

DEFAULT_STATE = {
    "user": None,
    "auth_view": "login",
    "reset_email": "",
    "reset_question": "",
    "reset_verified": False,
    "flash_message": "",
    "flash_type": "success",
    "otp_hash": None,
    "otp_created_at": 0.0,
    "otp_last_sent_at": 0.0,
    "otp_attempts": 0,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CSS — BLUE AND WHITE PORTAL DESIGN
# =========================================================
st.markdown("""
<style>
    .stApp {
        background: #f5f8fc;
        color: #172b4d;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 680px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .brand {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .brand-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 54px;
        height: 54px;
        border-radius: 16px;
        background: #e7efff;
        color: #245bd6;
        font-size: 29px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .brand-name {
        color: #173b78;
        font-size: 27px;
        font-weight: 750;
        letter-spacing: -0.5px;
    }

    .brand-caption {
        color: #71809a;
        font-size: 13px;
        margin-top: 5px;
    }

    .portal-card {
        background: white;
        border: 1px solid #e1e8f2;
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 10px 35px rgba(35, 70, 125, 0.07);
    }

    .page-title {
        color: #173b78;
        font-size: 27px;
        font-weight: 750;
        margin-bottom: 5px;
    }

    .page-subtitle {
        color: #748198;
        font-size: 14px;
        margin-bottom: 20px;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e1e8f2;
        border-radius: 16px;
        padding: 22px;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label {
        color: #263d60;
        font-weight: 600;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 9px;
        border-color: #d9e2ef;
        min-height: 43px;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #3478f6;
        box-shadow: 0 0 0 1px #3478f6;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 9px;
        min-height: 43px;
        font-weight: 650;
        border: 1px solid #d9e2ef;
    }

    div[data-testid="stFormSubmitButton"] > button {
        background: #245bd6;
        color: white;
        border-color: #245bd6;
        width: 100%;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #194bb7;
        border-color: #194bb7;
        color: white;
    }

    .security-note {
        color: #71809a;
        font-size: 12px;
        text-align: center;
        margin-top: 16px;
    }

    .portal-footer {
        text-align: center;
        color: #8290a5;
        font-size: 12px;
        padding-top: 22px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# REUSABLE UI
# =========================================================
def render_brand():
    st.markdown("""
        <div class="brand">
            <div class="brand-logo">✦</div>
            <div class="brand-name">Infosys Portal</div>
            <div class="brand-caption">Secure access to your account</div>
        </div>
    """, unsafe_allow_html=True)


def render_heading(title, subtitle):
    st.markdown(
        f"""
        <div class="page-title">{html.escape(title)}</div>
        <div class="page-subtitle">{html.escape(subtitle)}</div>
        """,
        unsafe_allow_html=True
    )


def show_flash_message():
    message = st.session_state.flash_message

    if message:
        message_type = st.session_state.flash_type

        if message_type == "error":
            st.error(message)
        elif message_type == "warning":
            st.warning(message)
        else:
            st.success(message)

        st.session_state.flash_message = ""


def go_to(view):
    st.session_state.auth_view = view
    st.rerun()


def show_footer():
    st.markdown("""
        <div class="portal-footer">
            © Infosys Portal · Secure Authentication
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# BRAND HEADER
# =========================================================
render_brand()
show_flash_message()


# =========================================================
# AUTHENTICATED HOME PAGE
# =========================================================
if st.session_state.user:
    user = st.session_state.user

    render_heading(
        "Welcome back!",
        "You have successfully signed in to your account."
    )

    st.markdown(
        '<div class="portal-card">',
        unsafe_allow_html=True
    )
    st.markdown("### Account details")
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("Sign Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.auth_view = "login"
        st.session_state.reset_email = ""
        st.session_state.reset_question = ""
        st.session_state.reset_verified = False
        st.session_state.otp_hash = None
        st.session_state.otp_attempts = 0
        st.session_state.flash_message = (
            "You have signed out successfully."
        )
        st.session_state.flash_type = "success"
        st.rerun()


# =========================================================
# SIGNUP PAGE
# =========================================================
elif st.session_state.auth_view == "signup":
    render_heading(
        "Create your account",
        "Enter your details to register for secure access."
    )

    with st.form("signup_form"):
        username = st.text_input(
            "Username",
            placeholder="Choose a username"
        )

        email = st.text_input(
            "Email address",
            placeholder="you@example.com"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password"
        )

        confirm_password = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Enter your password again"
        )

        st.markdown("---")
        st.markdown("**Password recovery details**")

        security_question = st.selectbox(
            "Security question",
            [
                "What is your pet's name?",
                "What city were you born in?",
                "What is your favourite school subject?",
            ]
        )

        security_answer = st.text_input(
            "Security answer",
            type="password",
            placeholder="Enter an answer you will remember"
        )

        submitted = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

    if submitted:
        username = username.strip()
        email = email.strip().lower()

        if not username or not email or not password or not confirm_password:
            st.error("Please complete all required fields.")

        elif len(username) < 3:
            st.error("Username must contain at least 3 characters.")

        elif len(username) > 50:
            st.error("Username must be 50 characters or fewer.")

        elif not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        ):
            st.error("Please enter a valid email address.")

        elif not validate_password(password)[0]:
            st.error(validate_password(password)[1])

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif not security_answer.strip():
            st.error("Please enter your security answer.")

        elif len(security_answer.strip()) > 200:
            st.error("Security answer must be 200 characters or fewer.")

        else:
            success, message = create_user(
                username,
                email,
                password,
                security_question,
                security_answer
            )

            if success:
                st.session_state.auth_view = "login"
                st.session_state.flash_message = message
                st.session_state.flash_type = "success"
                st.rerun()
            else:
                st.error(message)

    if st.button(
        "Already have an account? Sign in",
        use_container_width=True
    ):
        go_to("login")


# =========================================================
# LOGIN PAGE
# =========================================================
elif st.session_state.auth_view == "login":
    render_heading(
        "Sign in",
        "Use your username or email to access your account."
    )

    with st.form("login_form"):
        login_id = st.text_input(
            "Username or email",
            placeholder="Enter username or email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True
        )

    if submitted:
        if not login_id.strip() or not login_password:
            st.error("Please enter your username/email and password.")
        else:
            authenticated_user = authenticate_user(
                login_id,
                login_password
            )

            if authenticated_user:
                st.session_state.user = authenticated_user
                st.session_state.flash_message = ""
                st.rerun()
            else:
                st.error("Invalid username/email or password.")

    if st.button("Forgot Password?", use_container_width=True):
        st.session_state.reset_email = ""
        st.session_state.reset_question = ""
        st.session_state.reset_verified = False
        st.session_state.otp_hash = None
        st.session_state.otp_attempts = 0
        go_to("forgot")

    if st.button(
        "Create a new account",
        use_container_width=True
    ):
        go_to("signup")

    st.markdown(
        '<div class="security-note">'
        '🔒 Your password is stored using bcrypt hashing.'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# FORGOT PASSWORD — EMAIL LOOKUP
# =========================================================
elif st.session_state.auth_view == "forgot":
    render_heading(
        "Forgot password?",
        "Choose how you want to recover your account."
    )

    with st.form("forgot_email_form"):
        recovery_email = st.text_input(
            "Registered email",
            value=st.session_state.reset_email,
            placeholder="you@example.com"
        )

        col1, col2 = st.columns(2)

        with col1:
            security_submitted = st.form_submit_button(
                "Via Security Question",
                use_container_width=True
            )

        with col2:
            otp_submitted = st.form_submit_button(
                "Via OTP",
                use_container_width=True
            )

    if security_submitted or otp_submitted:
        recovery_email = recovery_email.strip().lower()

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            recovery_email
        ):
            st.error("Please enter a valid email address.")

        else:
            question = get_security_question(recovery_email)

            if not question:
                st.error(
                    "No account with that email was found, "
                    "or its security question has not been configured."
                )

            elif security_submitted:
                st.session_state.reset_email = recovery_email
                st.session_state.reset_question = question
                st.session_state.reset_verified = False
                st.session_state.otp_hash = None
                go_to("security_verify")

            elif otp_submitted:
                st.session_state.reset_email = recovery_email
                st.session_state.reset_verified = False

                success, message = create_and_send_otp(
                    recovery_email
                )

                if success:
                    st.session_state.flash_message = message
                    st.session_state.flash_type = "success"
                    go_to("otp_verify")
                else:
                    st.error(message)

    if st.button("Back to Sign In", use_container_width=True):
        st.session_state.reset_email = ""
        st.session_state.reset_verified = False
        st.session_state.otp_hash = None
        go_to("login")


# =========================================================
# FORGOT PASSWORD — OTP VERIFICATION
# =========================================================
elif st.session_state.auth_view == "otp_verify":
    if not st.session_state.reset_email or not st.session_state.otp_hash:
        st.warning("Please request an OTP before continuing.")
        if st.button("Return to Forgot Password"):
            go_to("forgot")
    else:
        render_heading(
            "Verify your email",
            "Enter the 6-digit OTP sent to your registered email."
        )

        st.info(
            f"OTP sent to: {st.session_state.reset_email}"
        )

        # A new key is used for each newly generated OTP.
        # This clears the old input automatically after a resend.
        otp_widget_key = (
            f"otp_input_{int(st.session_state.otp_created_at)}"
        )

        otp_input = st.text_input(
            "Enter your 6-digit OTP",
            key=otp_widget_key,
            max_chars=6,
            placeholder="Enter OTP",
            help="Enter the 6 digits from your email."
        )

        digit_count = sum(char.isdigit() for char in otp_input)
        st.caption(f"{digit_count}/6 digits entered")

        if st.button("Verify OTP", use_container_width=True):
            if len(otp_input) != 6 or not otp_input.isdigit():
                st.error("Please enter all 6 digits of your OTP.")
            else:
                success, message = verify_email_otp(otp_input)

                if success:
                    st.session_state.flash_message = message
                    st.session_state.flash_type = "success"
                    go_to("reset_password")
                else:
                    st.error(message)

        last_sent = st.session_state.otp_last_sent_at
        seconds_since_send = time.time() - last_sent

        remaining = max(
            0,
            OTP_RESEND_COOLDOWN - int(seconds_since_send)
        )

        if remaining > 0:
            st.caption(
                f"You can resend the OTP in {remaining} seconds."
            )

        if st.button(
            "Resend OTP",
            use_container_width=True,
            disabled=(remaining > 0)
        ):
            success, message = create_and_send_otp(
                st.session_state.reset_email
            )

            if success:
                st.session_state.flash_message = message
                st.session_state.flash_type = "success"
                go_to("otp_verify")
            else:
                st.error(message)

        if st.button("← Cancel", use_container_width=True):
            st.session_state.otp_hash = None
            st.session_state.otp_attempts = 0
            st.session_state.reset_email = ""
            st.session_state.reset_verified = False
            go_to("login")


# =========================================================
# FORGOT PASSWORD — SECURITY QUESTION
# =========================================================
elif st.session_state.auth_view == "security_verify":
    render_heading(
        "Verify your identity",
        "Answer the security question you selected during signup."
    )

    st.info(
        f"**Security question:** "
        f"{st.session_state.reset_question}"
    )

    with st.form("security_answer_form"):
        recovery_answer = st.text_input(
            "Your security answer",
            type="password",
            placeholder="Enter your answer"
        )

        submitted = st.form_submit_button(
            "Verify Answer",
            use_container_width=True
        )

    if submitted:
        if not recovery_answer.strip():
            st.error("Please enter your security answer.")

        elif verify_security_answer(
            st.session_state.reset_email,
            recovery_answer
        ):
            st.session_state.reset_verified = True
            st.session_state.otp_hash = None
            st.session_state.flash_message = (
                "Security answer verified successfully."
            )
            st.session_state.flash_type = "success"
            go_to("reset_password")

        else:
            st.error("Incorrect security answer. Please try again.")

    if st.button("Back", use_container_width=True):
        st.session_state.reset_verified = False
        go_to("forgot")


# =========================================================
# FORGOT PASSWORD — SET NEW PASSWORD
# =========================================================
elif st.session_state.auth_view == "reset_password":
    if (
        not st.session_state.reset_verified
        or not st.session_state.reset_email
    ):
        st.session_state.auth_view = "forgot"
        st.rerun()

    render_heading(
        "Reset your password",
        "Choose a new password for your account."
    )

    with st.form("reset_password_form"):
        new_password = st.text_input(
            "New password",
            type="password",
            placeholder="Enter a new password"
        )

        confirm_new_password = st.text_input(
            "Confirm new password",
            type="password",
            placeholder="Re-enter your new password"
        )

        submitted = st.form_submit_button(
            "Update Password",
            use_container_width=True
        )

    if submitted:
        if not new_password or not confirm_new_password:
            st.error("Please fill in both password fields.")

        elif not validate_password(new_password)[0]:
            st.error(validate_password(new_password)[1])

        elif new_password != confirm_new_password:
            st.error("Passwords do not match.")

        else:
            updated = update_password(
                st.session_state.reset_email,
                new_password
            )

            if updated:
                st.session_state.reset_email = ""
                st.session_state.reset_question = ""
                st.session_state.reset_verified = False
                st.session_state.otp_hash = None
                st.session_state.otp_attempts = 0
                st.session_state.auth_view = "login"
                st.session_state.flash_message = (
                    "Password updated successfully. Please sign in."
                )
                st.session_state.flash_type = "success"
                st.rerun()
            else:
                st.error(
                    "Could not update the password. Please try again."
                )

    if st.button("Cancel password reset", use_container_width=True):
        st.session_state.reset_email = ""
        st.session_state.reset_question = ""
        st.session_state.reset_verified = False
        st.session_state.otp_hash = None
        go_to("login")


# =========================================================
# FOOTER
# =========================================================
show_footer()
