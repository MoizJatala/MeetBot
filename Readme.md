# MeetBot

MeetBot is an automated Google Meet assistant that can log into a Google account, join a specified meeting, capture on-screen text using OCR (Optical Character Recognition), and send extracted text to the chat. This project utilizes Selenium for browser automation and Tesseract OCR for text extraction.

## Features
- **Automated Google login** using Selenium.
- **Google Meet joining capabilities** with various joining options.
- **OCR-based text extraction** from meeting screens using Tesseract.
- **Chat integration** to send extracted text to the Google Meet chat.
- **Error handling and recovery mechanisms** to ensure stability.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Google Chrome (latest version)
- ChromeDriver (managed via `webdriver-manager`)
- Tesseract OCR (must be installed separately)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project directory with the following credentials:
```
TEST_GOOGLE_EMAIL=your_email@gmail.com
TEST_GOOGLE_PASSWORD=your_password
```

### Git Ignore
Create a `.gitignore` file and add the following lines to exclude sensitive and unnecessary files:
```
.env
.venv
```

## Usage

1. **Run the MeetBot script:**
   ```bash
   python meetbot.py
   ```
2. **Enter the Google Meet link** when prompted.
3. **The bot will:**
   - Log into your Google account.
   - Join the specified meeting.
   - Start capturing screen text using OCR.
   - Send extracted text to the chat automatically.

### Exiting the Bot
Press `CTRL+C` to terminate the script safely.

## File Structure
```
MeetBot/
│── meetbot.py       # Main bot script
│── requirements.txt # Dependencies
│── .env             # Environment variables (not included in repo)
│── .gitignore       # Git ignore file
│── README.md        # Project documentation
```

## Dependencies
The following Python packages are used in this project:
```bash
selenium
webdriver-manager
pillow
tesseract
python-dotenv
```

## Troubleshooting
- **Google Login Issues:** Ensure the credentials in the `.env` file are correct.
- **ChromeDriver Errors:** Run `pip install --upgrade webdriver-manager`.
- **Tesseract OCR Issues:** Ensure Tesseract is installed and added to your system's PATH.
- **Meet Joining Fails:** The bot tries different methods to join; if it fails, ensure the meeting link is correct.

## License
This project is open-source under the MIT License.

## Contribution
Feel free to submit pull requests for improvements or bug fixes!

