@echo off
chcp 65001 > nul
setlocal
title X-Poster セットアップ

echo ============================================
echo  Xポスト自動生成システム セットアップ
echo ============================================
echo.

REM --- Python の確認 ---
where python >nul 2>nul
if errorlevel 1 (
  echo [エラー] Python が見つかりません。
  echo.
  echo Microsoft Store または https://www.python.org/ から
  echo Python 3.10 以上をインストールしてください。
  echo インストール時「Add Python to PATH」に必ずチェックを入れてください。
  echo.
  pause
  exit /b 1
)

echo [OK] Python が見つかりました:
python --version
echo.

REM --- APIキーの登録（ユーザー環境変数として保存） ---
echo Anthropic の APIキーを入力してください。
echo （画面には表示されますが、この端末のユーザー環境変数に保存されます）
echo.
set /p APIKEY="APIキー: "

if "%APIKEY%"=="" (
  echo [スキップ] APIキーが未入力のため保存しませんでした。
) else (
  setx ANTHROPIC_API_KEY "%APIKEY%" >nul
  echo [OK] APIキーを環境変数 ANTHROPIC_API_KEY に保存しました。
  echo     ※ 反映のため、この後コマンド窓を開き直してください。
)
echo.

echo このシステムは標準ライブラリのみで動作するため、
echo 追加パッケージのインストールは不要です。
echo.
echo セットアップ完了です。
echo ローカル生成は run_local.bat を実行してください。
echo.
pause
