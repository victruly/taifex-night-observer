import sys
import argparse
from fetcher import TAIFEXFetcher
from analyzer import MarketAnalyzer
from mailer import ReportMailer

def main():
    parser = argparse.ArgumentParser(description="台指期夜盤與外資劇本觀測系統")
    parser.add_argument("--dry-run", action="store_true", help="僅執行資料抓取與劇本判斷，輸出 HTML 檔案而不發送郵件")
    args = parser.parse_args()

    print("==================================================")
    print("🚀 啟動台指期夜盤指數觀測與外資劇本分析發報作業")
    print("==================================================")

    # 1. 抓取期交所數據
    fetcher = TAIFEXFetcher()
    print("\n[Step 1] 抓取期交所夜盤與日盤行情...")
    market_data = fetcher.fetch_night_and_day_market()
    print(f" -> 夜盤成交量: {market_data.get('tx_near_night_volume')} 口")
    print(f" -> 夜盤量佔比: {market_data.get('tx_near_night_ratio')} %")
    print(f" -> 夜盤漲跌: {market_data.get('night_change')} 點 ({market_data.get('night_change_pct')}%)")

    print("\n[Step 2] 抓取外資多空淨額 (盤後交易時段 futContractsDateAh)...")
    foreign_data = fetcher.fetch_foreign_net_position()
    print(f" -> 外資夜盤多空淨額: {foreign_data.get('night_foreign_net')} 口")
    print(f" -> 全日外資未平倉淨額: {foreign_data.get('foreign_net_oi')} 口")


    # 2. 進行劇本判斷與閥值檢查
    print("\n[Step 3] 執行 4 大劇本推演與門檻檢查...")
    analyzer = MarketAnalyzer(market_data, foreign_data)
    result = analyzer.analyze()

    print(f"\n🎯 判定劇本：{result['scenario_emoji']} {result['scenario_name']}")
    print(f"   開盤走向: {result['opening_direction']} ｜ 盤中趨勢: {result['intraday_trend']}")
    print(f"   信賴度評級: {result['credibility_level']}")
    print(f"   詳細推演: {result['description']}")

    # 3. 產出 HTML 郵件
    mailer = ReportMailer()
    html_content = mailer.generate_html_content(result)

    if args.dry_run:
        output_file = "sample_report.html"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n[Dry Run] 測試完成！HTML 報告已儲存至 '{output_file}'")
    else:
        print("\n[Step 4] 發送電子郵件...")
        success = mailer.send_email(html_content)
        if success:
            print("✅ 郵件發送成功！")
        else:
            print("⚠️ 郵件發送失敗或未設定 SMTP 憑證（請確認環境變數 / GitHub Secrets）。")

if __name__ == "__main__":
    main()
