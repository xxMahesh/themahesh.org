# QR Code Notepad

A simple web-based notepad application that allows you to create notes and share them via QR codes. Perfect for continuing your work across different devices.

## Features

- Create and edit notes
- Auto-save functionality (every 30 seconds)
- Generate QR codes for easy sharing
- Access notes from any device
- Real-time synchronization
- Mobile-friendly interface

## Setup

1. Make sure you have Python 3.7+ installed on your system.

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Start writing your note in the text area
2. Click "Share Note" to generate a QR code
3. Scan the QR code with your mobile device to continue editing on the go
4. Changes are automatically saved every 30 seconds
5. You can also manually save changes using the "Save Changes" button

## Notes

- The application stores notes in memory, so they will be lost when the server is restarted
- For production use, you should implement a proper database
- Make sure your mobile device and computer are on the same network to access the notes 