#!/usr/bin/env python3
"""
@Yuki_mental_log 向け Xポスト自動生成スクリプト（トレンド対応版）

- 20個生成：10個はトレンド絡み、10個は定番ミックス
- トレンドは無料ソース（Googleトレンド/News RSS）で収集
- 3本柱（投資／メンタル／職場あるある）＋世間一般トレンド両方を対象
- 型はミックスして多様に。投資系ポストには免責を必ず付与
- キーワード指定時は、そのキーワードと3本柱を絡めて生成
- 結果を docs/posts/YYYY-MM-DD.json に保存し、index.json を更新
"""

import os
import re
import json
import datetime
import urllib.request

from trends import collect_trends

# ---- 設定 ---------------------------------------------------------------

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-opus-4-8"       # コスト優先なら claude-sonnet-5 に変更可
POST_COUNT = 20
TREND_COUNT = 10                # うちトレンド絡みの本数
KEYWORD = os.environ.get("KEYWORD", "").strip()   # 手動実行時に入る

JST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(JST).strftime("%Y-%m-%d")

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
POSTS_DIR = os.path.join(DOCS_DIR, "posts")

# ---- プロンプト ---------------------------------------------------------

SYSTEM_PROMPT = """あなたは日本語Xアカウント「@Yuki_mental_log」の運用担当ライターです。
このアカウントの3本柱は「投資」「メンタルウェルネス」「職場あるある」です。

# アカウントの勝ちパターン・トーン
- 代表的な型:「〇〇するまでが一番長い + あるある5個リスト + 完璧主義の否定 + ハードルを下げる結論」
- 会話形式（3者の会話 + 最後にオチ）もよく使う
- 押しつけがましくなく、読者の肩の力を抜くトーン
- 共感先行、説教しない

# 厳守ルール
- 投資に関する内容を含むポストには、末尾に必ず免責を付ける:
  「※投資は自己責任で。内容は情報提供であり投資助言ではありません。」
- 1ポストは140字前後（日本語）。長すぎない。
- 誹謗中傷・特定の個人攻撃・過度に断定的な投資勧誘は書かない。
- トレンドに触れる場合も、政治的・センシティブな話題への断定や煽りは避ける。
- 各ポストは独立して単体で成立させる。
"""


def build_user_prompt(trend_text):
    type_note = (
        "型は「あるある5個リスト型」「会話形式（3者+オチ）」「短い問いかけ型」"
        "「共感一言型」などをミックスし、同じ型が連続しないよう多様にすること。"
    )

    trend_block = ""
    trend_instruction = ""
    if trend_text:
        trend_block = f"\n\n# 参考トレンド情報（本日収集）\n{trend_text}\n"
        trend_instruction = (
            f"このうち{TREND_COUNT}個は、上記トレンド情報を自然に絡めたポストにすること"
            f"（無理に固有名詞を入れず、話題の空気感を活かす）。"
            f"残り{POST_COUNT - TREND_COUNT}個は3本柱の定番ネタでミックスすること。"
        )
    else:
        trend_instruction = (
            f"投資／メンタル／職場あるあるの3本柱をバランスよくミックスして"
            f"{POST_COUNT}個作ること。"
        )

    if KEYWORD:
        theme = (
            f"今回のテーマキーワードは「{KEYWORD}」です。"
            f"このキーワードを軸にしつつ、3本柱と自然に絡めてください。"
            f"さらに{TREND_COUNT}個は上記トレンドも絡めること。"
        )
    else:
        theme = trend_instruction

    return f"""{theme}
{type_note}
{trend_block}
# 出力形式（厳守）
以下のJSON配列のみを出力してください。前置き・説明・コードフェンスは一切不要です。
各要素は次のキーを持つオブジェクト:
- "pillar": "投資" | "メンタル" | "職場あるある" のいずれか
- "type": ポストの型（例:「あるある5個リスト」「会話形式」など）
- "trend": true（トレンド絡み）または false（定番）
- "text": ポスト本文（改行を含んでよい。投資系は免責込み）

必ず{POST_COUNT}個。JSON配列だけを返すこと。"""


def call_claude(trend_text):
    payload = {
        "model": MODEL,
        "max_tokens": 8000,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": build_user_prompt(trend_text)}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    return "".join(parts)


def parse_posts(raw):
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)


def main():
    if not API_KEY:
        raise SystemExit("ANTHROPIC_API_KEY が設定されていません。")

    print("トレンド情報を収集中...")
    trend_text = collect_trends()
    print(f"トレンド収集: {'成功' if trend_text else '取得できず（定番のみで生成）'}")

    raw = call_claude(trend_text)
    posts = parse_posts(raw)

    record = {
        "date": TODAY,
        "mode": "manual" if KEYWORD else "scheduled",
        "keyword": KEYWORD,
        "used_trends": bool(trend_text),
        "generated_at": datetime.datetime.now(JST).isoformat(),
        "posts": posts,
    }

    os.makedirs(POSTS_DIR, exist_ok=True)
    out_path = os.path.join(POSTS_DIR, f"{TODAY}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    dates = sorted(
        [f[:-5] for f in os.listdir(POSTS_DIR) if f.endswith(".json") and f != "index.json"],
        reverse=True,
    )
    with open(os.path.join(POSTS_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f, ensure_ascii=False, indent=2)

    print(f"生成完了: {out_path} ({len(posts)}件, mode={record['mode']}, "
          f"trend={record['used_trends']}, keyword='{KEYWORD}')")


if __name__ == "__main__":
    main()
