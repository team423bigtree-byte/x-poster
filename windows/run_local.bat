@echo off
chcp 65001 > nul
setlocal
title X-Poster ローカル生成

echo ============================================
echo  Xポスト ローカル生成
echo ============================================
echo.

REM --- APIキー確認 ---
if "%ANTHROPIC_API_KEY%"=="" (
  echo [エラー] 環境変数 ANTHROPIC_API_KEY が設定されていません。
  echo setup.bat を実行してから、コマンド窓を開き直してください。
  echo.
  pause
  exit /b 1
)

REM --- キーワード入力（空でもOK） ---
echo テーマキーワードを入れると、それを絡めて生成します。
echo 何も入れずにEnterを押すと、通常のトレンド＋定番ミックスで生成します。
echo.
set /p KW="キーワード（省略可）: "
set "KEYWORD=%KW%"

echo.
echo 生成を開始します...
echo.

REM --- スクリプトのある場所へ移動して実行 ---
cd /d "%~dp0..\scripts"
python generate.py

echo.
if errorlevel 1 (
  echo [エラー] 生成に失敗しました。上のメッセージを確認してください。
) else (
  echo 完了しました。docs\posts フォルダに保存されています。
  echo GitHubへ反映する場合は、変更をコミット＆プッシュしてください。
)
echo.
pause
