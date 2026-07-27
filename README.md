# Xポスト自動生成システム（@Yuki_mental_log）

毎朝20ポストを自動生成し、日毎ファイルに保存。パスワード付きダッシュボードで
1ポストずつコピーできます。外出先ではiPhoneからURLを開くだけ。

## 仕組み
- 定時（毎朝7:00 JST）：20個生成（うち10個はトレンド絡み、10個は3本柱の定番ミックス）
- トレンド収集：Googleトレンド／ニュースRSS（無料）で世間一般＋3本柱関連の話題を取得
- 手動：GitHubから「Run workflow」→キーワードを入れて生成
- ローカル：Windows PCで run_local.bat から直接生成も可能
- 生成物は docs/posts/YYYY-MM-DD.json に日毎保存
- docs/index.html がGitHub Pagesで公開されるダッシュボード（合言葉ロック付き）
  → トレンド絡みのポストには「トレンド」バッジが付きます

## ファイル構成
```
.github/workflows/generate.yml  … 定時＋手動実行のワークフロー
scripts/generate.py             … 生成本体
scripts/trends.py               … トレンド収集モジュール
docs/index.html                 … パスワード付きダッシュボード
docs/posts/                     … 生成結果（自動生成）
windows/setup.bat               … Windows初期セットアップ
windows/run_local.bat           … Windowsローカル生成
```

---

## A. クラウド自動運用のセットアップ（PCで一度だけ）

### 1. リポジトリを作る
GitHubで新規リポジトリを作成（**Private推奨**）。このフォルダ一式をアップロード。

### 2. APIキーを登録
Settings → Secrets and variables → Actions → New repository secret
- Name: `ANTHROPIC_API_KEY`
- Secret: あなたのAnthropic APIキー

### 3. 合言葉を設定
docs/index.html の `const PASSWORD = "CHANGE_ME";` を好きな合言葉に書き換えてコミット。

### 4. GitHub Pagesを有効化
Settings → Pages → Source「Deploy from a branch」、Branch `main` / フォルダ `/docs`。
数分後に `https://（ID）.github.io/（リポジトリ名）/` で開けます。

### 5. Actionsの書き込み権限
Settings → Actions → General → Workflow permissions を
「Read and write permissions」に設定。

---

## B. Windowsローカル生成のセットアップ

### 1. Pythonを入れる
Microsoft Store か https://www.python.org/ からPython 3.10以上をインストール。
インストール時「Add Python to PATH」にチェック。

### 2. setup.bat を実行
windows\setup.bat をダブルクリック → APIキーを入力。
（ユーザー環境変数に保存されます。実行後はコマンド窓を開き直してください）

### 3. run_local.bat で生成
windows\run_local.bat をダブルクリック → キーワードを入れる（空でもOK）。
docs\posts に結果が保存されます。GitHubへ反映したい場合はコミット＆プッシュ。

※ローカル生成は追加パッケージ不要（標準ライブラリのみで動作）。

---

## 使い方（iPhoneでOK）

**閲覧・コピー**：公開URLをブックマーク → 合言葉入力 → 日付選択 → 各ポストの「コピー」。
**手動生成**：GitHubアプリ → Actions → Generate X Posts → Run workflow → キーワード入力。

---

## カスタマイズ
- トレンド比率：generate.py の `TREND_COUNT`（初期10）
- 生成時刻：generate.yml の cron（`0 22 * * *` = 7:00 JST）
- 生成数：generate.py の `POST_COUNT`
- モデル：generate.py の `MODEL`（コスト優先は `claude-sonnet-5`）
- トレンド収集ソース：trends.py（Google News の検索キーワード等を調整可）

## セキュリティ注意
- 合言葉はJavaScript内の簡易ロックです。URL＋合言葉を知られると閲覧されます。
- 厳密な非公開はPrivateリポジトリ＋GitHubアプリでJSON直接閲覧に切り替えてください。
