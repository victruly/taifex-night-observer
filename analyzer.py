import config

class MarketAnalyzer:
    """台指期夜盤與外資多空劇本分析器"""
    
    def __init__(self, market_data, foreign_data):
        self.market_data = market_data
        self.foreign_data = foreign_data

    def analyze(self):
        # 1. 基礎數據讀取
        night_vol = self.market_data.get('tx_near_night_volume', 0)
        night_ratio = self.market_data.get('tx_near_night_ratio', 0.0)
        night_change = self.market_data.get('night_change', 0.0)
        
        # 優先使用未平倉多空淨額，若為 0 則參考當日交易淨額
        foreign_net = self.foreign_data.get('foreign_net_oi', 0)
        if foreign_net == 0:
            foreign_net = self.foreign_data.get('foreign_trade_net', 0)

        # 2. 三大參考價值條件檢測 (Threshold Checks)
        cond_vol = night_vol > config.MIN_NIGHT_VOLUME
        cond_ratio = night_ratio > config.MIN_NIGHT_RATIO
        cond_foreign = abs(foreign_net) > config.MIN_FOREIGN_NET

        # 參考價值評級
        valid_count = sum([cond_vol, cond_ratio, cond_foreign])
        if valid_count == 3:
            credibility_level = "高參考價值 (極具代表性)"
            credibility_badge = "HIGH"
        elif valid_count == 2:
            credibility_level = "中高參考價值 (具良好參考性)"
            credibility_badge = "MEDIUM"
        elif valid_count == 1:
            credibility_level = "中偏低參考價值 (部分條件未達標)"
            credibility_badge = "LOW"
        else:
            credibility_level = "低參考價值 (訊號較薄弱)"
            credibility_badge = "WEAK"

        # 3. 4 種大盤走向劇本判斷
        is_night_up = night_change > 0
        is_foreign_positive = foreign_net > 0

        if is_night_up and is_foreign_positive:
            scenario_name = "開高走高"
            scenario_emoji = "🟢"
            opening_direction = "開盤上漲"
            intraday_trend = "後續持續上漲 (多頭強勢突破)"
            description = "夜盤順勢收漲，且外資多空淨額站在多方，多頭氣勢強勁，開高後持續向上攻堅。"
        elif is_night_up and not is_foreign_positive:
            scenario_name = "開高走低"
            scenario_emoji = "🟡"
            opening_direction = "開盤上漲"
            intraday_trend = "後續拉回下跌 (開高誘多洗盤)"
            description = "夜盤受國際市場帶動收漲，但外資籌碼偏空壓頂，開高後易逢高賣壓吐回，注意誘多洗盤。"
        elif not is_night_up and not is_foreign_positive:
            scenario_name = "開低走低"
            scenario_emoji = "🔴"
            opening_direction = "開盤下跌"
            intraday_trend = "後續持續下跌 (空頭主導向下)"
            description = "夜盤受壓收跌，且外資籌碼亦站在空方，空頭主導盤勢，開低後恐持續下探尋找支撐。"
        else: # not is_night_up and is_foreign_positive
            scenario_name = "開低走高"
            scenario_emoji = "🔵"
            opening_direction = "開盤下跌"
            intraday_trend = "後續拉回上漲 (開低誘空洗盤反彈)"
            description = "夜盤跟隨國際拉回收跌，但外資籌碼偏多護盤，開低後易吸引買盤低接反彈，走開低走高行情。"

        return {
            'scenario_name': scenario_name,
            'scenario_emoji': scenario_emoji,
            'opening_direction': opening_direction,
            'intraday_trend': intraday_trend,
            'description': description,
            'credibility_level': credibility_level,
            'credibility_badge': credibility_badge,
            'threshold_checks': {
                'night_volume': {'val': night_vol, 'target': config.MIN_NIGHT_VOLUME, 'pass': cond_vol},
                'night_ratio': {'val': night_ratio, 'target': config.MIN_NIGHT_RATIO, 'pass': cond_ratio},
                'foreign_net': {'val': foreign_net, 'target': config.MIN_FOREIGN_NET, 'pass': cond_foreign}
            },
            'raw_market': self.market_data,
            'raw_foreign': self.foreign_data
        }
