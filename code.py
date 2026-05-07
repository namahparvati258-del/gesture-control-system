import streamlit as st
from streamlit_webrtc import webrtc_streamer
import cv2
import mediapipe as mp
import pyautogui
import webbrowser

# Page Config
st.set_page_config(page_title="AI Gesture Controller", layout="wide")
st.title("🖐️ AI Gesture System Controller")
st.write("Dell i7 Optimized - Direct Link Mode")

# 1. Mediapipe Hand Setup (Optimized for CPU)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Global counter for frame skipping
if 'count' not in st.session_state:
    st.session_state.count = 0

def process_frame(frame):
    st.session_state.count += 1
    img = frame.to_ndarray(format="bgr24")
    img = cv2.flip(img, 1) # Mirror effect

    # Optimization: Har 3rd frame process karo
    if st.session_state.count % 3 != 0:
        return img

    # Resize image for faster processing
    h, w, _ = img.shape
    small_img = cv2.resize(img, (320, 240))
    results = hands.process(cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get Landmarks (Mapping back to original size)
            landmarks = hand_landmarks.landmark
            
            # Key Points: Index Tip (8), Index MCP (5), Thumb Tip (4)
            index_tip = landmarks[8]
            index_mcp = landmarks[5]
            thumb_tip = landmarks[4]

            # --- GESTURE LOGIC ---

            # A. SCROLL UP (Index up)
            if index_tip.y < index_mcp.y - 0.1:
                pyautogui.scroll(150)
            
            # B. SCROLL DOWN (Index down)
            elif index_tip.y > index_mcp.y + 0.1:
                pyautogui.scroll(-150)

            # C. MINIMIZE ALL (Squeeze/Fist)
            # Distance formula to detect fist
            dist = ((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)**0.5
            if dist < 0.05:
                pyautogui.hotkey('win', 'd')

            # D. OPEN CHROME ('C' Gesture - Top Right Trigger)
            # Agar index finger screen ke top right corner mein ho
            if index_tip.x > 0.8 and index_tip.y < 0.2:
                webbrowser.open("https://www.google.com")

    return img

# 2. WebRTC Streamer for Direct Link
webrtc_streamer(
    key="gesture-control",
    video_frame_callback=process_frame,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

st.sidebar.info("Tips:\n1. Index up = Scroll Up\n2. Index down = Scroll Down\n3. Fist = Minimize\n4. Top-Right Corner = Chrome")