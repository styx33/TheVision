import logging
from telegram import Bot

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        if not bot_token or not chat_id:
            logging.warning('Telegram bot token or chat id not provided; notifications disabled.')
            self.bot = None
        else:
            self.bot = Bot(token=bot_token)

    def alert(self, token, score, reasons):
        text = self._format_message(token, score, reasons)
        logging.info('ALERT: %s', text.replace('\n',' | '))
        if self.bot:
            try:
                self.bot.send_message(chat_id=self.chat_id, text=text, disable_web_page_preview=True)
            except Exception as e:
                logging.exception('Failed to send Telegram message: %s', e)

    def _format_message(self, token, score, reasons):
        name = token.get('name') or token.get('symbol') or 'UNKNOWN'
        symbol = token.get('symbol','')
        url = token.get('url') or token.get('token_url') or token.get('address','')
        marketcap = token.get('marketcap','?')
        vol = token.get('volume','?')
        tx = token.get('tx_per_min','?')
        holders = token.get('holders','?')
        lines = [
            f'🔥 Meme Coin gefunden! Score: {score:.1f}/10',
            f'Name: {name} ({symbol})',
            f'MarketCap: {marketcap} | Volume: {vol} | Tx/min: {tx} | Holders: {holders}',
            f'Gründe: {", ".join(reasons[:5])}',
            f'Link: {url}'
        ]
        return '\n'.join(lines)

class DemoNotifier:
    def alert(self, token, score, reasons):
        text = self._format_message(token, score, reasons)
        print('--- DEMO ALERT ---')
        print(text)
        print('--- END DEMO ---')

    def _format_message(self, token, score, reasons):
        name = token.get('name') or token.get('symbol') or 'UNKNOWN'
        symbol = token.get('symbol','')
        url = token.get('url') or token.get('token_url') or token.get('address','')
        marketcap = token.get('marketcap','?')
        vol = token.get('volume','?')
        tx = token.get('tx_per_min','?')
        holders = token.get('holders','?')
        lines = [
            f'🔥 Meme Coin gefunden! Score: {score:.1f}/10',
            f'Name: {name} ({symbol})',
            f'MarketCap: {marketcap} | Volume: {vol} | Tx/min: {tx} | Holders: {holders}',
            f'Gründe: {", ".join(reasons[:5])}',
            f'Link: {url}'
        ]
        return '\n'.join(lines)
