import urllib.request
import urllib.parse
import re
import json
from datetime import datetime
import config

class TAIFEXFetcher:
    """台灣期貨交易所數據擷取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def fetch_night_and_day_market(self):
        """
        擷取當日台指期 (TX) 近月與全月之日盤、夜盤行情與成交量數據
        """
        # 1. 抓取盤後 (夜盤) 市場數據
        night_data = self._query_daily_market_report(market_code='1')
        
        # 2. 抓取一般 (日盤) 市場數據
        day_data = self._query_daily_market_report(market_code='0')
        
        # 3. 嘗試 Yahoo 股市作為夜盤即時行情備用/補充來源
        yahoo_data = self._query_yahoo_stock_wtfx()
        
        # 整合資訊
        result = {
            'tx_near_night_volume': night_data.get('near_volume', 0) or yahoo_data.get('night_volume', 0),
            'tx_near_day_volume': day_data.get('near_volume', 0),
            'tx_total_night_volume': night_data.get('total_volume', 0) or yahoo_data.get('night_volume', 0),
            'tx_total_day_volume': day_data.get('total_volume', 0),
            'night_last_price': night_data.get('near_last_price', 0) or yahoo_data.get('last_price', 0),
            'night_change': night_data.get('near_change', 0.0) or yahoo_data.get('change', 0.0),
            'night_change_pct': night_data.get('near_change_pct', 0.0) or yahoo_data.get('change_pct', 0.0),
            'day_settlement_price': day_data.get('near_settlement', 0) or yahoo_data.get('previous_close', 0),
            'query_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        # 計算夜盤量佔比 (%)
        near_total = result['tx_near_day_volume'] + result['tx_near_night_volume']
        result['tx_near_night_ratio'] = round((result['tx_near_night_volume'] / near_total * 100), 2) if near_total > 0 else 0.0
        
        total_all = result['tx_total_day_volume'] + result['tx_total_night_volume']
        result['tx_total_night_ratio'] = round((result['tx_total_night_volume'] / total_all * 100), 2) if total_all > 0 else result['tx_near_night_ratio']
        
        return result

    def _query_daily_market_report(self, market_code='0'):
        """查詢期交所 futDailyMarketReport"""
        url = config.TAIFEX_DAILY_MARKET_URL
        try:
            req = urllib.request.Request(f"{url}?queryType=2&marketCode={market_code}&dateSharing=1", headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
            near_volume = 0
            total_volume = 0
            near_last_price = 0
            near_change = 0.0
            near_change_pct = 0.0
            near_settlement = 0

            # 抓取表格行
            for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE):
                tds = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.DOTALL | re.IGNORECASE)
                clean = [re.sub(r'<[^>]+>|\s+', ' ', td).strip() for td in tds]
                clean = [c for c in clean if c]
                
                if len(clean) >= 9 and clean[0] == 'TX':
                    # clean[1]: 到期月份 (如 202608)
                    # clean[5]: 最後成交價
                    # clean[6]: 漲跌價
                    # clean[7]: 漲跌%
                    # clean[8] 或 clean[9]: 成交量 / 結算價
                    try:
                        price_str = clean[5].replace(',', '')
                        chg_str = clean[6].replace('▲', '').replace('▼', '').replace(',', '')
                        chg_pct_str = clean[7].replace('▲', '').replace('▼', '').replace('%', '').replace(',', '')
                        
                        # 成交量及結算價 Parsing
                        vol = 0
                        settle = 0
                        for val in clean[8:]:
                            val_clean = val.replace(',', '')
                            if val_clean.isdigit():
                                num = int(val_clean)
                                if num > 10000 and settle == 0:
                                    settle = num
                                elif num > 0 and vol == 0:
                                    vol = num
                                    
                        total_volume += vol
                        
                        # 近月第一筆 TX 記錄
                        if near_last_price == 0 and price_str.replace('.', '').isdigit():
                            near_last_price = float(price_str)
                            near_change = float(chg_str) if '▼' not in clean[6] else -float(chg_str)
                            near_change_pct = float(chg_pct_str) if '▼' not in clean[7] else -float(chg_pct_str)
                            near_volume = vol
                            near_settlement = settle
                    except Exception:
                        pass
                        
            return {
                'near_volume': near_volume,
                'total_volume': total_volume,
                'near_last_price': near_last_price,
                'near_change': near_change,
                'near_change_pct': near_change_pct,
                'near_settlement': near_settlement
            }
        except Exception as e:
            print(f"[Fetcher] Query daily market error (code={market_code}):", e)
            return {}

    def _query_yahoo_stock_wtfx(self):
        """從 Yahoo 股市備用抓取 WTX& (台指期夜盤)"""
        url = "https://tw.stock.yahoo.com/quote/WTX%26"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
            vol_match = re.search(r'\"volume\"\s*:\s*\"([0-9,]+)\"', html)
            price_match = re.search(r'\"price\"\s*:\s*\{\"raw\":\"([0-9\.]+)\"', html)
            prev_match = re.search(r'\"previousClose\"\s*:\s*([0-9\.]+)', html)
            
            last_price = float(price_match.group(1)) if price_match else 0
            prev_close = float(prev_match.group(1)) if prev_match else 0
            vol = int(vol_match.group(1).replace(',', '')) if vol_match else 0
            chg = round(last_price - prev_close, 2) if (last_price and prev_close) else 0
            chg_pct = round((chg / prev_close) * 100, 2) if prev_close > 0 else 0
            
            return {
                'night_volume': vol,
                'last_price': last_price,
                'previous_close': prev_close,
                'change': chg,
                'change_pct': chg_pct
            }
        except Exception as e:
            print("[Fetcher] Yahoo fallback query error:", e)
            return {}

    def fetch_foreign_net_position(self):
        """
        擷取期交所三大法人未沖銷部位 (futContractsDate) 外資多空淨額 (口數)
        """
        url = config.TAIFEX_MAJOR_INSTITUTIONS_URL
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
            foreign_net_oi = 0      # 未平倉多空淨額 (口數)
            foreign_trade_net = 0   # 當日交易多空淨額 (口數)
            
            # 解析 TD/TR
            for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE):
                tds = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', tr, re.DOTALL | re.IGNORECASE)
                clean = [re.sub(r'<[^>]+>|\s+', ' ', td).strip() for td in tds]
                clean = [c for c in clean if c]
                
                # 台指期 TX 第一行列為外資時
                if len(clean) >= 12 and '外資' in clean[0]:
                    # clean[5]: 交易多空淨額口數
                    # clean[11]: 未平倉多空淨額口數
                    try:
                        trade_net_str = clean[5].replace(',', '')
                        oi_net_str = clean[11].replace(',', '')
                        
                        foreign_trade_net = int(trade_net_str)
                        foreign_net_oi = int(oi_net_str)
                        break
                    except Exception:
                        pass
                        
            return {
                'foreign_net_oi': foreign_net_oi,
                'foreign_trade_net': foreign_trade_net
            }
        except Exception as e:
            print("[Fetcher] Query foreign net position error:", e)
            return {'foreign_net_oi': 0, 'foreign_trade_net': 0}
