PulseSniper Alert v0.4 — Webserver-enabled (Flask) package
---------------------------------------------------------

This package is ready for Replit. It runs a small Flask webserver at '/' so uptime services
(e.g. UptimeRobot) can ping it and keep the Repl awake.

How it works:
- main.py starts a background thread running the scanner (polling Dexscreener)
- Flask serves a health endpoint at '/' and '/health' returning JSON
- Replit will provide a public URL you can use with UptimeRobot to ping every 5-25 minutes

Quick start on Replit:
1. Import this ZIP into Replit (Create App -> Python -> Upload files or upload ZIP and extract).
2. Open Shell and run: pip install -r requirements.txt
3. Set the Run command to: python main.py
4. Click Run. The console should show "PulseSniper Alert v0.4 starting (mode=live)..."
5. Use the Replit-provided web URL (shown on the right as your app URL) in UptimeRobot to ping every 5 minutes.

Security note:
- config.json contains your Telegram token. Keep the ZIP private.
- If you want me to remove the token after you verify the bot works, tell me and I'll delete the configured ZIP from my environment.
