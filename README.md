## Fake News Detection App

Interactive Kivy desktop app that lets users log in, paste a news snippet, and receive a trust assessment powered by Google Gemini plus optional text-to-speech playback. MongoDB stores user credentials, while gTTS and Pygame provide narration.

---

### What It Does
- Screens: Home, Login, Sign-up, Main analyzer, About page.
- Auth: Credentials saved in MongoDB (`fake_news_detection_app.users`).
- Detection: Sends the user prompt to `models/gemini-2.5-flash`, asking for a *True/False* verdict with a short justification.
- Voice feedback: gTTS synthesizes the response, Pygame plays it inline.

---

### How It Works (High Level)
1. `main.py` loads secrets from `.env`, configures Gemini, and wires up all Kivy screens.
2. `Database` helper connects to the local MongoDB instance and handles `register_user` / `validate_user`.
3. When the user submits text on `MainScreen`, `get_ai_response()` calls Gemini and `text_to_speech()` plays the answer.
4. UI navigation is handled by a `ScreenManager`; each screen has its own layout/background assets in the repo.

---

### Requirements
- Python 3.11+ (matches the bundled `myenv`)
- MongoDB running locally on `mongodb://localhost:27017`
- Google Gemini API access (create an API key)
- System packages for Kivy, SDL, and Pygame (install via OS package manager if prompted)

Python deps are listed in `requirements.txt`. Install them via:
```
pip install -r requirements.txt
```

---

### Run & Init Instructions
> These steps assume macOS/Linux. On Windows, swap `source` with `myenv\Scripts\activate`.

1. **Clone & enter**
   ```
   git clone <repo-url>
   cd Fake_News_Detection_
   ```
2. **Create / reuse the virtual env**
   ```
   python3 -m venv myenv      # skip if you want to reuse the bundled env
   source myenv/bin/activate
   pip install -U pip
   pip install -r requirements.txt
   ```
3. **Init runtime secrets**  
   Create `.env` in the project root containing **exactly**:
   ```
   GOOGLE_API_KEY=your-gemini-key
   ```
   Replace `your-gemini-key` with the actual Gemini API key; the app exits early if this value is missing or blank.
4. **Start MongoDB**  
   Ensure `mongod` is running: `brew services start mongodb-community` (or your distro-specific command).
5. **Run the app**
   ```
   python main.py
   ```
   The GUI window opens with the Home screen. Create an account, log in, and paste news text on the main screen to trigger an AI verdict plus optional audio narration.

---

### Troubleshooting tips
- *API key error*: check `.env` and that the terminal is inside the root before running `python main.py`.
- *Mongo connection refused*: start MongoDB or update the URI in `Database`.
- *Audio device busy*: Pygame needs access to the default output; close competing apps or change the device via OS settings.

---

### Future ideas
- Ship a `requirements.txt` and packaged installer.
- Add role-based dashboards for admins to audit predictions.
- Cache model decisions and expose basic analytics.

