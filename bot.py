#!/usr/bin/env python3
import os
import time
import datetime
import threading
import uuid

import pytesseract
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys

load_dotenv()

class MeetBot:
    def __init__(self):
        self.options = self._prepare_chrome_options()
        self.driver = None
        
    def _prepare_chrome_options(self):
        """Set up Chrome options with all necessary arguments"""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")  # Run without GUI
        options.add_argument(f"--user-data-dir=./chrome_profile_{uuid.uuid4()}")
        
        # Media stream permissions
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--use-fake-ui-for-media-stream")
        
        # Additional permissions
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,  # 1:allow, 2:block
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.notifications": 1
        })
        
        return options
    
    def start(self):
        """Initialize the Chrome driver with prepared options"""
        print("[Selenium] Starting Chrome browser...")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
    def login_to_google(self, email, password):
        """Login to Google account"""
        print("[Google Login] Navigating to Google's login page...")
        self.driver.get("https://accounts.google.com/signin")

        # Enter email
        email_field = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='email']"))
        )
        email_field.clear()
        email_field.send_keys(email)
        self.driver.find_element(By.ID, "identifierNext").click()
        
        time.sleep(3)

        # Enter password
        password_field = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        password_field.clear()
        password_field.send_keys(password)
        self.driver.find_element(By.ID, "passwordNext").click()

        # Verify login
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'SignOutOptions')]"))
            )
            print("[Google Login] Login successful.")
        except Exception as e:
            print("[Google Login] Login might have failed:", e)
            
    def join_meeting(self, meeting_url):
        """Join the Google Meet meeting"""
        print(f"[Meeting] Navigating to meeting: {meeting_url}")
        self.driver.get(meeting_url)
        time.sleep(5)

        join_button_xpaths = [
            "//span[contains(text(), 'Join now')]/parent::button",
            "//span[contains(text(), 'Ask to join')]/parent::button",
            "//span[contains(text(), 'Join meeting')]/parent::button",
            "//button[contains(text(), 'Continue without microphone and camera')]",
            "//span[contains(text(), 'Join')]/parent::button"
        ]

        for xpath in join_button_xpaths:
            try:
                button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script("arguments[0].click();", button)
                print(f"[Meeting] Clicked: {xpath}")
                time.sleep(3)
                
                if "Ask to join" in xpath:
                    print("[Meeting] Waiting for host approval...")
                    time.sleep(10)
                
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-meeting-title]"))
                    )
                    print("[Meeting] Successfully joined the meeting")
                    return True
                except:
                    continue
                    
            except Exception as e:
                continue

        print("[Meeting] Warning: Could not confirm successful join")
        return False

    def send_to_chat(self, text):
        """
        Fallback method to send OCR text to the Meet chat
        """
        try:
            # Try to open chat if it's not already open
            chat_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Chat with everyone']"))
            )
            chat_button.click()
            time.sleep(1)
            
            # Find and use the chat input
            chat_input = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//textarea[@aria-label='Send a message to everyone']"))
            )
            chat_input.send_keys("OCR Text Update:")
            chat_input.send_keys(Keys.ENTER)
            chat_input.send_keys(text)
            chat_input.send_keys(Keys.ENTER)
            
            # Ensure the chat scrolls to the bottom
            chat_container = self.driver.find_element(By.XPATH, "//div[@aria-live='polite']")
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", chat_container)
            
            print("[Chat] Sent OCR text to chat")
        except Exception as e:
            print(f"[Chat] Error sending to chat: {str(e)}")

    def capture_and_display(self, interval=5):
        """Start the screenshot and OCR loop with improved error handling"""
        def screenshot_loop():
            last_text = ""
            consecutive_failures = 0
            
            while True:
                try:
                    # Wait for the page to be stable
                    time.sleep(2)
                    
                    # Capture screenshot
                    png_data = self.driver.get_screenshot_as_png()
                    image = Image.open(BytesIO(png_data))
                    
                    # Perform OCR
                    ocr_text = pytesseract.image_to_string(image).strip()
                    
                    # Only display if we have new, meaningful text
                    if len(ocr_text) > 10 and ocr_text != last_text:
                        self.send_to_chat(ocr_text)  # Sending OCR to chat
                        last_text = ocr_text
                        consecutive_failures = 0
                        print("[OCR] New text captured and displayed")
                    
                except Exception as e:
                    consecutive_failures += 1
                    print(f"[Screenshot Loop] Error: {str(e)}")
                    
                    # If we've failed multiple times, try to recover
                    if consecutive_failures >= 3:
                        print("[Recovery] Attempting to refresh display method...")
                        try:
                            self.send_to_chat("OCR System: Attempting to recover...")
                            consecutive_failures = 0
                        except:
                            pass
                        
                time.sleep(interval)

        thread = threading.Thread(target=screenshot_loop, daemon=True)
        thread.start()
        print("[OCR] Screenshot loop started")
        return thread

    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print("[Main] Selenium browser closed.")

def main():
    email = os.getenv("TEST_GOOGLE_EMAIL")
    password = os.getenv("TEST_GOOGLE_PASSWORD")
    
    if not (email and password):
        print("[Error] Google account credentials not provided. Exiting.")
        return
        
    meeting_url = input("Enter the Google Meet link: ")
    bot = MeetBot()
    
    try:
        bot.start()
        bot.login_to_google(email, password)
        if bot.join_meeting(meeting_url):
            bot.capture_and_display()
            while True:
                time.sleep(60)
    except KeyboardInterrupt:
        print("\n[Main] KeyboardInterrupt received. Exiting...")
    finally:
        bot.close()

if __name__ == "__main__":
    main()
