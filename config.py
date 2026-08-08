import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ==========================================
# 參考價值門檻設定 (Threshold Filters)
# ==========================================
MIN_NIGHT_VOLUME = 300       # 夜盤成交量 > 300 口
MIN_NIGHT_RATIO = 40.0       # 夜盤量佔比 > 40%
MIN_FOREIGN_NET = 1000       # 外資多空淨額絕對值 > 1000 口

# ==========================================
# 郵件 SMTP 設定 (Email Configuration)
# ==========================================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")

# ==========================================
# 台灣期貨交易所 API & Web Endpoints
# ==========================================
TAIFEX_DAILY_MARKET_URL = "https://www.taifex.com.tw/cht/3/futDailyMarketReport"
TAIFEX_MAJOR_INSTITUTIONS_URL = "https://www.taifex.com.tw/cht/3/futContractsDate"
