import requests, time, logging, random, os
from utils import score_token

class Scanner:
    def __init__(self, cfg, notifier):
        self.cfg = cfg
        self.notifier = notifier
        self.seen = set()
        self.last_alert_minute = 0
        self.alerts_this_minute = 0

    def _fetch_with_retry(self, url, headers=None, attempts=2):
        backoff = self.cfg.get('retry_backoff_seconds', 5)
        for i in range(attempts):
            try:
                r = requests.get(url, headers=headers, timeout=8)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                logging.warning('Fetch failed (attempt %s): %s', i+1, e)
                time.sleep(backoff * (i+1))
        return None

    def _fetch_from_dexscreener(self):
        url = self.cfg.get('dexscreener_url')
        data = self._fetch_with_retry(url)
        if not data:
            return []
        # dex structure can vary; handle defensively
        items = []
        if isinstance(data, dict):
            if 'pairs' in data:
                items = data.get('pairs', [])
            elif 'data' in data:
                items = data.get('data', [])
            else:
                items = data.get('tokens') or data.get('listings') or []
        elif isinstance(data, list):
            items = data
        normalized = []
        for it in items:
            try:
                normalized.append(self._normalize_dexscreener_item(it))
            except Exception as e:
                logging.debug('Normalization failed for item: %s', e)
        return normalized

    def _normalize_dexscreener_item(self, it):
        name = it.get('name') or it.get('token','')
        symbol = it.get('symbol') or ''
        address = it.get('address') or it.get('tokenAddress') or it.get('id') or ''
        marketcap = float(it.get('marketCap') or it.get('marketcap') or it.get('market_cap', 0) or 0)
        volume = float(it.get('volume') or it.get('realVolume') or it.get('txVolume') or 0)
        tx = float(it.get('txsPerMin') or it.get('tx_per_min') or it.get('txPerMin') or 0)
        holders = int(it.get('holders') or it.get('uniqueHolders') or it.get('unique_holders') or 0)
        url = it.get('url') or it.get('pairUrl') or ''
        has_social = bool(it.get('twitter') or it.get('social') or False)
        lp_locked = bool(it.get('liquidityLocked') or it.get('lp_locked') or False)
        return {
            'name': name,
            'symbol': symbol,
            'address': address,
            'marketcap': marketcap,
            'volume': volume,
            'tx_per_min': tx,
            'holders': holders,
            'url': url,
            'has_social': has_social,
            'lp_locked': lp_locked
        }

    def poll_once(self):
        listings = []
        if self.cfg.get('mode','live') == 'demo':
            import json, os
            path = os.path.join(os.path.dirname(__file__), 'demo_data.json')
            try:
                with open(path,'r') as f:
                    listings = json.load(f)
            except Exception as e:
                logging.warning('Could not load demo data: %s', e)
                listings = []
        else:
            if self.cfg.get('dexscreener_enabled', True):
                listings += self._fetch_from_dexscreener()

        random.shuffle(listings)
        now_min = int(time.time() // 60)
        if now_min != self.last_alert_minute:
            self.last_alert_minute = now_min
            self.alerts_this_minute = 0

        for token in listings:
            token_id = token.get('address') or token.get('symbol') + '|' + token.get('name','')
            if token_id in self.seen:
                continue
            score, reasons = score_token(token, self.cfg)
            if score >= self.cfg.get('score_threshold', 7.0):
                if self.alerts_this_minute < self.cfg.get('max_parallel_alerts_per_minute', 3):
                    self.notifier.alert(token, score, reasons)
                    self.alerts_this_minute += 1
                    self.seen.add(token_id)
                else:
                    logging.info('Rate limit reached for alerts this minute.')
            else:
                logging.debug('Token %s scored %.2f (below threshold)', token.get('symbol'), score)
