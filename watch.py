# -*- coding: utf-8 -*-
"""只读看护：云端定时检查 Cookie 认证状态（不做签到）。

背景（2026-11）：GLaDOS 签到接口要求 Cloudflare Turnstile 令牌，纯 HTTP
签到已不可行，真实签到由本机浏览器计划任务完成（见 README）。本脚本只
做只读检查：Cookie 认证有效则退出码 0，失效则退出码 1 让 Actions 显红，
提醒同步最新 Cookie 到 GLADOS_COOKIES secret。
"""

import json
import os
import sys

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36")


def main():
    raw = os.environ.get("GLADOS_COOKIES", "").strip()
    if not raw:
        print("ERROR 未配置 GLADOS_COOKIES secret")
        return 1
    # 旧 & 分隔多账号格式取第一段；JSON 数组格式提取 cookie 字段
    if raw.startswith("["):
        try:
            raw = json.loads(raw)[0].get("cookie", "")
        except (ValueError, IndexError, KeyError, TypeError):
            print("ERROR GLADOS_COOKIES JSON 解析失败")
            return 1
    cookie = raw.split("&")[0].strip()
    if "gld:sess=" not in cookie:
        print("ERROR Cookie 缺少 gld:sess 字段")
        return 1

    try:
        resp = requests.get(
            "https://glados.cloud/api/user/status",
            headers={"cookie": cookie, "user-agent": UA},
            timeout=(10, 30),
            allow_redirects=False,
        )
    except requests.RequestException as e:
        print(f"ERROR 请求异常：{type(e).__name__}: {e}")
        return 1
    try:
        data = resp.json()
    except ValueError:
        print(f"ERROR 返回非 JSON（状态码 {resp.status_code}），Cookie 可能已失效")
        return 1

    code = data.get("code")
    print(f"status -> code={code} message={data.get('message', '')} "
          f"leftDays={data.get('leftDays')}")
    if code == 0:
        print("OK Cookie 认证有效（真实签到由本机浏览器计划任务完成）")
        return 0
    print("ERROR Cookie 认证失效或接口异常。处理指引：")
    print("  - 若本机浏览器签到仍正常，只需把最新 Cookie 同步到 GLADOS_COOKIES secret")
    print("  - 若本机也失败，请重新登录 glados.cloud 更新 cookie.txt 与 secret")
    _push("GLaDOS Cookie 失效", "云端看护检测到 GLADOS_COOKIES 认证失效，"
          "需要把最新 Cookie 同步到 secret（若本机签到正常，从 cookie.txt 复制即可）。")
    return 1


def _push(title, body):
    """Server酱 微信推送（配置 SERVERCHAN_SENDKEY secret 后生效）。"""
    key = os.environ.get("SERVERCHAN_SENDKEY", "").strip()
    if not key:
        print("（未配置 SERVERCHAN_SENDKEY，跳过微信推送）")
        return
    if key.upper().startswith("SCTP"):
        uid = key[4:].split("t")[0]
        url = f"https://{uid}.push.ft07.com/send/{key}.send"
    else:
        url = f"https://sctapi.ftqq.com/{key}.send"
    try:
        resp = requests.post(url, data={"title": title, "desp": body}, timeout=(10, 30))
        print(f"方糖推送 -> {resp.status_code} {resp.text[:100]}")
    except requests.RequestException as e:
        print(f"WARN 方糖推送失败：{type(e).__name__}: {e}")


if __name__ == "__main__":
    sys.exit(main())
