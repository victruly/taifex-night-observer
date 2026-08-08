# 台指期夜盤指數觀測與外資多空劇本自動發報系統

本專案是一個基於 Python 與 GitHub Actions 的自動化台指期夜盤觀測發報工具。系統會在**每日夜盤結束後的早上 06:20（台灣時間）** 自動擷取台灣期貨交易所（TAIFEX）最新夜盤成交量、日盤成交量、夜盤漲跌點數與外資多空未沖銷淨額，自動進行 4 大行情劇本推演與參考價值檢測，並將精美的 HTML 分析報告寄送至您的 Email。

---

## 📌 核心功能與判斷邏輯

### 1. 三大參考價值指標檢測 (Threshold Filters)
系統在進行劇本推演前，會自動檢查當日數據是否具備高參考價值：
- 🔹 **條件一（夜盤成交量）**：`夜盤成交量 > 300 口`（確保具備基本成交流動性）
- 🔹 **條件二（夜盤量佔比）**：`夜盤量佔比 > 40%`（夜盤走勢具強烈參考價值）
- 🔹 **條件三（外資多空淨額）**：`|外資多空淨額| > 1000 口`（外資籌碼方向明確）

---

### 2. 四大行情劇本推演矩陣 (Scenario Matrix)

| 劇本圖示與名稱 | 夜盤漲跌 | 外資多空淨額 | 預測隔天開盤與盤中走勢 | 說明 |
| :--- | :---: | :---: | :--- | :--- |
| 🟢 **開高走高** | 漲 (`+`) | 正 (多頭 `>0`) | **開盤上漲，後續持續上漲** | 夜盤順勢，外資籌碼偏多，多頭強勢突破攻堅 |
| 🟡 **開高走低** | 漲 (`+`) | 負 (空頭 `<0`) | **開盤上漲，後續拉回下跌** | 夜盤受國際帶動，但外資空單壓頂，易開高誘多洗盤 |
| 🔴 **開低走低** | 跌 (`-`) | 負 (空頭 `<0`) | **開盤下跌，後續持續下跌** | 夜盤偏空，外資籌碼站在空方，空頭主導向下探底 |
| 🔵 **開低走走高** | 跌 (`-`) | 正 (多頭 `>0`) | **開盤下跌，後續拉回上漲** | 夜盤拉回，但外資多單護盤，易開低誘空反彈向上 |

---

## 🛠️ GitHub 專案部署與自動寄信設定教學

如同「月領現金5000流」專案，您可以將此專案推送到您的 GitHub Repository，並透過 **GitHub Secrets** 安全設定 Email 寄信憑證：

### 步驟 1：推動程式碼至 GitHub
在本地終端機執行：
```bash
git init
git add .
git commit -m "Feat: Add 台指期夜盤指數觀測與外資劇本發報系統"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 步驟 2：設定 GitHub Actions Secrets
1. 進入您的 GitHub Repository 頁面。
2. 點擊頂部的 **Settings** ➔ 點擊左側選單 **Secrets and variables** ➔ **Actions**。
3. 點擊 **New repository secret**，依次建立以下三個環境變數：

| Secret 名稱 | 設定值說明 | 範例 |
| :--- | :--- | :--- |
| `MAIL_USERNAME` | 您的發信 Gmail 帳號 | `your_email@gmail.com` |
| `MAIL_PASSWORD` | 您的 Gmail **應用程式密碼** (App Password) | `abcd efgh ijkl mnop` |
| `RECEIVER_EMAIL` | 接收每日報告的 Email | `your_email@gmail.com` |

> 🔑 **如何取得 Gmail 應用程式密碼？**
> 1. 前往 Google 帳戶管理 ➔ 點擊「安全性」。
> 2. 確認已開啟「兩步驟驗證」。
> 3. 在搜尋列搜尋「應用程式密碼 (App Passwords)」，建立一個名稱為 `GitHub-Observer` 的密碼並複製 16 位密碼填入 `MAIL_PASSWORD` 中。

---

## 💻 本地端測試說明 (Local Execution & Dry-Run)

### 1. 安裝套件
```bash
pip install -r requirements.txt
```

### 2. 測試模式 (Dry-Run 不寄信，產出 HTML 預覽)
```bash
python main.py --dry-run
```
執行後會在目錄下產生 `sample_report.html`，您可以用瀏覽器雙擊打開預覽發報郵件樣式。

### 3. 本地端真實寄信測試
複製 `.env.example` 為 `.env` 並填入憑證後執行：
```bash
cp .env.example .env
# 編輯 .env 填入密碼
python main.py
```

---

## ⏰ 自動化排程時間 (GitHub Actions Schedule)

.github/workflows/daily_night_observer.yml 設定每日在 **22:20 UTC** 自動觸發（對應**台灣時間每日 06:20 AM**），夜盤收盤後第一時間發送報告！

---

## ⚠️ 免責聲明 (Disclaimer)
本專案所提供之數據分析與劇本推演僅供學術研究與個人盤前資料整理參考，不構成任何投資建議或買賣邀約。投資交易具有高槓桿風險，請獨立評估並自負投資盈虧。
