import streamlit as st
import requests
import re
import textstat
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"  # FastAPI backend
st.set_page_config(page_title="Text Morph", page_icon="🌀", layout="centered")

# ---------------- Session State ----------------
if "token" not in st.session_state:
    st.session_state["token"] = None
if "email" not in st.session_state:
    st.session_state["email"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "auth"
if "name_prefill" not in st.session_state:
    st.session_state["name_prefill"] = ""
if "age_prefill" not in st.session_state:
    st.session_state["age_prefill"] = "<18"
if "lang_prefill" not in st.session_state:
    st.session_state["lang_prefill"] = "English"
if "bio_prefill" not in st.session_state:
    st.session_state["bio_prefill"] = ""
# keep track of last-uploaded image object for preview (optional)
if "last_profile_pic" not in st.session_state:
    st.session_state["last_profile_pic"] = None

# ---------------- Helpers ----------------
def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_strong_password(password: str) -> bool:
    return (len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isupper() for c in password))

def header_nav():
    # Top navigation buttons (Profile, Dashboard, Logout)
    if st.session_state["token"]:
        cols = st.columns([1,1,1,3])
        with cols[0]:
            if st.button("Profile"):
                st.session_state["page"] = "profile"
                st.rerun()
        with cols[1]:
            if st.button("Dashboard"):
                st.session_state["page"] = "dashboard"
                st.rerun()
        with cols[2]:
            if st.button("Logout"):
                st.session_state["page"] = "auth"
                st.session_state["token"] = None
                st.session_state["email"] = None
                st.rerun()

# ---------------- AUTH ----------------
if st.session_state["page"] == "auth":
    st.title("User Authentication")
    st.write("Welcome! Please register or login to continue.")
    tab1, tab2 = st.tabs(["🔑 Register", "🚪 Login"])

    with tab1:
        st.subheader("Create a new account")
        name = st.text_input("Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")

        if st.button("Register"):
            if not name.strip():
                st.error("❌ Name cannot be empty")
            elif not is_valid_email(email):
                st.error("❌ Please enter a valid email")
            elif not is_strong_password(password):
                st.error("❌ Password must be ≥8 chars, include a number and an uppercase letter")
            else:
                payload = {"name": name, "email": email, "password": password}
                try:
                    r = requests.post(f"{API_URL}/register", json=payload)
                    if r.status_code == 200:
                        st.success("✅ Registration successful! You can now log in.")
                    else:
                        st.error(f"❌ {r.json().get('detail', 'Error occurred')}")
                except Exception as e:
                    st.error(f"Server error: {e}")

    with tab2:
        st.subheader("Login to your account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not is_valid_email(email):
                st.error("❌ Enter a valid email")
            elif not password:
                st.error("❌ Password cannot be empty")
            else:
                try:
                    r = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                    if r.status_code == 200:
                        st.session_state["token"] = r.json()["access_token"]
                        st.session_state["email"] = email
                        # try to prefill profile if exists
                        try:
                            pr = requests.get(f"{API_URL}/profile/{email}")
                            if pr.status_code == 200:
                                data = pr.json()
                                st.session_state["name_prefill"] = data.get("name", "")
                                st.session_state["age_prefill"] = data.get("age_group", "<18")
                                st.session_state["lang_prefill"] = data.get("language_pref", "English")
                                st.session_state["bio_prefill"] = data.get("bio", "") or ""
                                # leave user at dashboard if profile exists
                                st.session_state["page"] = "dashboard"
                            else:
                                st.session_state["page"] = "profile"
                        except Exception:
                            st.session_state["page"] = "profile"
                        st.rerun()
                    else:
                        st.error(f"❌ {r.json().get('detail', 'Invalid credentials')}")
                except Exception as e:
                    st.error(f"Server error: {e}")

# ---------------- PROFILE ----------------
elif st.session_state["page"] == "profile":
    header_nav()
    st.title("👤 Profile Management")
    st.write("Update your details below:")

    # --- Form inputs ---
    name = st.text_input("Name", value=st.session_state.get("name_prefill", ""), key="profile_name")
    age_group = st.selectbox(
        "Age Group",
        ["<18", "18-25", "26-35", "36-50", "50+"],
        index=["<18","18-25","26-35","36-50","50+"].index(st.session_state.get("age_prefill", "26-35")),
        key="profile_age"
    )
    language_pref = st.selectbox(
        "Preferred Language",
        ["English", "Telugu", "Hindi", "Tamil", "Other"],
        index=["English","Telugu","Hindi","Tamil","Other"].index(st.session_state.get("lang_prefill", "English")),
        key="profile_lang"
    )
    bio = st.text_area("Bio", value=st.session_state.get("bio_prefill", ""), key="profile_bio")

    # Show existing profile pic if available
    if st.session_state.get("profile_pic_url"):
        st.image(
            st.session_state["profile_pic_url"],
            caption="Profile Picture",
            use_container_width=False,
            width=200  # ✅ fixed size for consistency
        )

    # File uploader for updating profile picture
    profile_pic = st.file_uploader("Upload New Profile Picture", type=["jpg", "png", "jpeg"])

    if st.button("Save Profile"):
        if not name.strip():
            st.error("❌ Name cannot be empty")
        elif len(bio) > 500:
            st.error("❌ Bio cannot exceed 500 characters")
        else:
            payload = {
                "name": name,
                "age_group": age_group,
                "language_pref": language_pref,
                "bio": bio,
                "email": st.session_state["email"]
            }
            files = {}
            if profile_pic:
                files["profile_pic"] = (profile_pic.name, profile_pic.getvalue(), profile_pic.type)

            try:
                r = requests.post(f"{API_URL}/profile", data=payload, files=files)
                if r.status_code == 200:
                    st.success("✅ Profile saved successfully!")

                    saved = r.json()

                    # update session state with returned values
                    st.session_state["name_prefill"] = saved["name"]
                    st.session_state["age_prefill"] = saved["age_group"]
                    st.session_state["lang_prefill"] = saved["language_pref"]
                    st.session_state["bio_prefill"] = saved["bio"] or ""
                    st.session_state["profile_pic_url"] = saved.get("profile_pic_url")  # ✅ persist pic URL

                    # ✅ Show updated profile block
                    st.subheader("📌 Saved Profile")

                    if st.session_state.get("profile_pic_url"):
                        st.image(
                            st.session_state["profile_pic_url"],
                            caption="Profile Picture",
                            use_container_width=False,
                            width=200  # ✅ fixed size
                        )

                    st.markdown(f"**Name:** {saved['name']}")
                    st.markdown(f"**Age Group:** {saved['age_group']}")
                    st.markdown(f"**Language:** {saved['language_pref']}")
                    st.markdown(f"**Bio:** {saved['bio'] or ''}")

                else:
                    st.error(f"❌ {r.json().get('detail')}")
            except Exception as e:
                st.error(f"Server error: {e}")


# ---------------- DASHBOARD ----------------
elif st.session_state["page"] == "dashboard":
    header_nav()
    st.title("📊 Dashboard & Readability Analysis")

    uploaded_file = st.file_uploader("📂 Upload Document", type=["txt"])
    text_input = st.text_area("Or paste text here:")

    # pick content from file or text input
    content = ""
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8")
        except Exception:
            # if decode fails, try raw bytes -> string
            content = str(uploaded_file.read())
    elif text_input.strip():
        content = text_input.strip()

    # Use content (either file or pasted text)
    if st.button("🔎 Analyze Text"):
        if not content:
            st.warning("⚠️ Please upload or paste some text before analyzing.")
        else:
            # Compute readability scores
            flesch_kincaid = textstat.flesch_kincaid_grade(content)
            gunning_fog = textstat.gunning_fog(content)
            smog_index = textstat.smog_index(content)

            # Show scores in 3 colored boxes
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Flesch-Kincaid", round(flesch_kincaid, 2))
            with col2:
                st.metric("Gunning Fog", round(gunning_fog, 2))
            with col3:
                st.metric("SMOG Index", round(smog_index, 2))

            # Scale values relative to the max score (no hard 100 cap)
            raw_values = [flesch_kincaid, gunning_fog, smog_index]
            # avoid division by zero / negative weirdness: use max(abs()) if needed
            max_val = max(raw_values) if max(raw_values) > 0 else 1
            values = [(v / max_val) * 100 for v in raw_values]

            categories = ["Beginner", "Intermediate", "Advanced"]
            colors = ["#4CAF50", "#FFC107", "#F44336"]

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(8,5))
            bars = ax.bar(categories, values, color=colors)
            ax.set_ylim(0, 120)
            ax.set_ylabel("Score (normalized %)")
            ax.set_title("Readability Levels")

            # Add values on top of bars (show original score + percentage)
            for bar, raw, val in zip(bars, raw_values, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        f"{raw:.2f} ({val:.1f}%)", ha='center', fontsize=10, fontweight="bold")

            st.pyplot(fig)
