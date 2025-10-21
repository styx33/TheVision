def score_token(token, cfg):
    """Return (score: float, reasons: list[str])"""
    reasons = []
    score = 0.0
    tx = float(token.get('tx_per_min') or 0)
    vol = float(token.get('volume') or 0)
    mcap = float(token.get('marketcap') or 0)
    holders = int(token.get('holders') or 0)

    # Momentum (0-3)
    if tx >= cfg.get('min_tx_per_min', 50) and vol >= cfg.get('min_volume', 20000):
        score += 3; reasons.append('Momentum strong')
    elif tx >= cfg.get('min_tx_per_min', 30) or vol >= cfg.get('min_volume', 10000):
        score += 1.5; reasons.append('Momentum medium')
    else:
        reasons.append('Weak momentum')

    # Marketcap (0-2)
    if cfg.get('min_marketcap',0) <= mcap <= cfg.get('max_marketcap',999999999):
        score += 2; reasons.append('Marketcap in range')
    else:
        reasons.append('Marketcap out of range')

    # Holders (0-2)
    if holders >= cfg.get('min_holders',120):
        score += 2; reasons.append('Good holder growth')
    elif holders >= 50:
        score += 1; reasons.append('Some holders')
    else:
        reasons.append('Few holders')

    # Basic safety (0-3)
    if token.get('has_social'):
        score += 1; reasons.append('Social link present')
    if token.get('lp_locked'):
        score += 2; reasons.append('LP appears locked or large')

    # cap to 10
    if score > 10: score = 10
    return score, reasons
