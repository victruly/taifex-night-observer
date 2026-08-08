import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config

class ReportMailer:
    """HTML 郵件格式化與 SMTP 發送器"""
    
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.username = config.MAIL_USERNAME
        self.password = config.MAIL_PASSWORD
        self.receiver = config.RECEIVER_EMAIL

    def generate_html_content(self, analysis_result):
        res = analysis_result
        m = res['raw_market']
        f = res['raw_foreign']
        chk = res['threshold_checks']
        
        date_str = m.get('query_date', datetime.now().strftime("%Y-%m-%d"))
        
        # 漲跌圖示與顏色
        chg = m.get('night_change', 0.0)
        chg_color = "#e53e3e" if chg > 0 else ("#38a169" if chg < 0 else "#718096")
        chg_sign = "+" if chg > 0 else ""
        
        # 門檻檢查 Badges
        vol_badge = "✅ 通過 (>300口)" if chk['night_volume']['pass'] else f"⚠️ 未達標 ({chk['night_volume']['val']}口)"
        ratio_badge = "✅ 通過 (>40%)" if chk['night_ratio']['pass'] else f"⚠️ 未達標 ({chk['night_ratio']['val']}%)"
        foreign_badge = "✅ 通過 (|淨額|>1000)" if chk['foreign_net']['pass'] else f"⚠️ 未達標 ({chk['foreign_net']['val']}口)"
        
        foreign_val = chk['foreign_net']['val']
        foreign_color = "#e53e3e" if foreign_val > 0 else ("#38a169" if foreign_val < 0 else "#718096")
        foreign_sign = "+" if foreign_val > 0 else ""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台指期夜盤與外資劇本每日觀測報告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f7fafc;
            color: #2d3748;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 650px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }}
        .header {{
            background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
            color: #ffffff;
            padding: 24px 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .header p {{
            margin: 6px 0 0 0;
            font-size: 13px;
            color: #cbd5e0;
        }}
        .card {{
            margin: 20px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f8fafc;
            border-left: 6px solid #3182ce;
        }}
        .scenario-box {{
            background: #ffffff;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin: 20px;
            text-align: center;
        }}
        .scenario-title {{
            font-size: 26px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #1a202c;
        }}
        .scenario-desc {{
            font-size: 15px;
            color: #4a5568;
            line-height: 1.6;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        .table th, .table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #edf2f7;
            font-size: 14px;
        }}
        .table th {{
            background-color: #edf2f7;
            color: #4a5568;
            font-weight: 600;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background-color: #c6f6d5; color: #22543d; }}
        .badge-warning {{ background-color: #feebc8; color: #744210; }}
        .footer {{
            padding: 15px 30px;
            background-color: #edf2f7;
            font-size: 12px;
            color: #718096;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 台指期夜盤與外資劇本觀測週報</h1>
            <p>報告生成時間：{date_str} 06:20 AM (TW Local Time)</p>
        </div>

        <div class="scenario-box">
            <div style="font-size: 13px; color: #718096; font-weight: 600; text-transform: uppercase;">本日推演劇本</div>
            <div class="scenario-title">{res['scenario_emoji']} 劇本：{res['scenario_name']}</div>
            <div style="font-size: 16px; font-weight: 700; color: #2b6cb0; margin-bottom: 10px;">
                開盤走向：{res['opening_direction']} ｜ 盤中趨勢：{res['intraday_trend']}
            </div>
            <div class="scenario-desc">{res['description']}</div>
        </div>

        <div style="padding: 0 20px;">
            <h3 style="font-size: 16px; color: #2d3748; margin-bottom: 10px;">🔍 3 大參考價值指標判定 (Threshold Filters)</h3>
            <table class="table">
                <tr>
                    <th>評估項目</th>
                    <th>實測數值</th>
                    <th>判定標準</th>
                    <th>狀態</th>
                </tr>
                <tr>
                    <td><b>夜盤成交量</b></td>
                    <td><b>{m.get('tx_near_night_volume', 0):,} 口</b></td>
                    <td>&gt; 300 口</td>
                    <td><span class="badge {'badge-success' if chk['night_volume']['pass'] else 'badge-warning'}">{vol_badge}</span></td>
                </tr>
                <tr>
                    <td><b>夜盤量佔比</b></td>
                    <td><b>{m.get('tx_near_night_ratio', 0.0)} %</b></td>
                    <td>&gt; 40 %</td>
                    <td><span class="badge {'badge-success' if chk['night_ratio']['pass'] else 'badge-warning'}">{ratio_badge}</span></td>
                </tr>
                <tr>
                    <td><b>外資多空淨額</b></td>
                    <td><b style="color:{foreign_color};">{foreign_sign}{foreign_val:,} 口</b></td>
                    <td>|淨額| &gt; 1000 口</td>
                    <td><span class="badge {'badge-success' if chk['foreign_net']['pass'] else 'badge-warning'}">{foreign_badge}</span></td>
                </tr>
            </table>
            <div style="margin-top: 8px; font-size: 13px; color: #4a5568; text-align: right;">
                <b>訊號信賴度評級：</b><span style="color: #2b6cb0; font-weight: 700;">{res['credibility_level']}</span>
            </div>
        </div>

        <div style="padding: 10px 20px 20px 20px;">
            <h3 style="font-size: 16px; color: #2d3748; margin-bottom: 10px;">📈 夜盤與日盤詳細數據行情</h3>
            <table class="table">
                <tr>
                    <th>指標名稱</th>
                    <th>夜盤 (盤後)</th>
                    <th>日盤 (一般)</th>
                </tr>
                <tr>
                    <td><b>台指期近月成交量</b></td>
                    <td><b>{m.get('tx_near_night_volume', 0):,}</b> 口</td>
                    <td>{m.get('tx_near_day_volume', 0):,} 口</td>
                </tr>
                <tr>
                    <td><b>夜盤量佔比 (近月)</b></td>
                    <td colspan="2"><b style="color: #2b6cb0;">{m.get('tx_near_night_ratio', 0.0)} %</b></td>
                </tr>
                <tr>
                    <td><b>夜盤收盤價 / 漲跌</b></td>
                    <td><b>{m.get('night_last_price', 0):,.0f}</b></td>
                    <td><b style="color: {chg_color};">{chg_sign}{chg:.0f} pts ({chg_sign}{m.get('night_change_pct', 0.0)}%)</b></td>
                </tr>
                <tr>
                    <td><b>外資未平倉淨部位</b></td>
                    <td colspan="2"><b style="color: {foreign_color};">{foreign_sign}{f.get('foreign_net_oi', 0):,} 口</b></td>
                </tr>
            </table>
        </div>

        <div class="footer">
            <p>本郵件由 GitHub Actions 自動排程系統發送。數據來源：台灣期貨交易所 (TAIFEX)。<br>警語：本報告僅供個人學習與盤前資訊整理參考，不構成任何投資建議與買賣決策。</p>
        </div>
    </div>
</body>
</html>
        """
        return html

    def send_email(self, html_content, subject=None):
        if not subject:
            subject = f"【夜盤觀測發報】{datetime.now().strftime('%Y/%m/%d')} 台指期夜盤與外資劇本分析"
            
        if not self.username or not self.password or not self.receiver:
            print("[Mailer] SMTP credentials missing. Skipping email sending.")
            return False
            
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = self.receiver
            
            part = MIMEText(html_content, "html", "utf-8")
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, [self.receiver], msg.as_string())
                
            print(f"[Mailer] Email successfully sent to {self.receiver}!")
            return True
        except Exception as e:
            print("[Mailer] Failed to send email:", e)
            return False
