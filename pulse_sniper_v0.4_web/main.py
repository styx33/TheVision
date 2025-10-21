import threading, time, json, logging, os
from flask import Flask, jsonify
from scanner import Scanner
from notifier import TelegramNotifier, DemoNotifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def load_config(path='config.json'):
    with open(path, 'r') as f:
        return json.load(f)

app = Flask(__name__)
cfg = load_config()
notifier = DemoNotifier() if cfg.get('mode','live') == 'demo' else TelegramNotifier(cfg.get('telegram_bot_token'), cfg.get('telegram_chat_id'))
scanner = Scanner(cfg, notifier)
running = True

@app.route('/')
def index():
    return jsonify({"status":"ok","mode": cfg.get('mode','live')})

@app.route('/health')
def health():
    return jsonify({"status":"ok","time": int(time.time())})

def scanner_loop():
    logging.info('Scanner thread started')
    try:
        while running:
            try:
                scanner.poll_once()
            except Exception as e:
                logging.exception('Scanner error: %s', e)
            time.sleep(cfg.get('poll_interval_seconds', 20))
    except Exception as e:
        logging.exception('Scanner stopped unexpectedly: %s', e)

def main():
    global running
    logging.info('PulseSniper Alert v0.4 starting (mode=%s)...', cfg.get('mode'))
    t = threading.Thread(target=scanner_loop, daemon=True)
    t.start()
    port = int(os.environ.get('PORT', 8000))
    # start flask (blocking)
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
