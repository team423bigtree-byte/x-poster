#!/usr/bin/env python3
"""
無料ソースからトレンド情報を収集するモジュール。

- Googleトレンド（日本）の急上昇ワード RSS
- 3本柱関連ニュースの見出し（Google News RSS）
外部ライブラリ不要（標準ライブラリのみ）。取得失敗時は空リストを返し、
本体の生成を止めない設計。
"""

import re
import urllib.request
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (compatible; XPosterBot/1.0)"
TIMEOUT = 20


def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", errors="ignore")


def _strip(text):
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def google_trends_jp(limit=10):
    """Googleトレンド 日本の急上昇ワード（世間一般トレンド）"""
    url = "https://trends.google.co.jp/trending/rss?geo=JP"
    out = []
    try:
        xml = _fetch(url)
        root = ET.fromstring(xml)
        for item in root.iter("item"):
            title = item.findtext("title")
            if title:
                out.append(_strip(title))
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out


def google_news_topic(query, limit=5):
    """特定トピックのニュース見出し（3本柱関連トレンド用）"""
    q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
    out = []
    try:
        xml = _fetch(url)
        root = ET.fromstring(xml)
        for item in root.iter("item"):
            title = item.findtext("title")
            if title:
                out.append(_strip(title))
            if len(out) >= limit:
                break
    except Exception:
        pass
    return out


import urllib.parse  # google_news_topic用（末尾importでも動作）


def collect_trends():
    """トレンド情報をまとめて取得し、テキストブロックで返す"""
    general = google_trends_jp(limit=10)
    invest = google_news_topic("投資 OR 株価 OR 新NISA", limit=4)
    mental = google_news_topic("メンタル OR ストレス OR 働き方", limit=4)
    work = google_news_topic("仕事 OR 職場 OR 会社", limit=4)

    blocks = []
    if general:
        blocks.append("【世間一般の急上昇ワード】\n- " + "\n- ".join(general))
    if invest:
        blocks.append("【投資関連ニュース】\n- " + "\n- ".join(invest))
    if mental:
        blocks.append("【メンタル・働き方関連ニュース】\n- " + "\n- ".join(mental))
    if work:
        blocks.append("【職場・仕事関連ニュース】\n- " + "\n- ".join(work))

    return "\n\n".join(blocks) if blocks else ""


if __name__ == "__main__":
    print(collect_trends())
