import json, os, urllib.request, urllib.parse

KEY = os.environ["BARK_KEY"]
PARTS = {"MK2D4X/A": "256GB Star White", "MK2E4X/A": "256GB Night Sky"}
BUY = "https://www.apple.com/au/shop/buy-iphone/iphone-duo"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def bark(title, body, critical):
    q = {"group": "duo", "url": BUY}
    if critical:
        q.update(level="critical", volume="8")
    url = (f"https://api.day.app/{KEY}/{urllib.parse.quote(title)}/{urllib.parse.quote(body)}?"
           + urllib.parse.urlencode(q))
    urllib.request.urlopen(url, timeout=15).read()


qs = "&".join(f"parts.{i}={urllib.parse.quote(p, safe='')}" for i, p in enumerate(PARTS))
url = f"https://www.apple.com/au/shop/fulfillment-messages?pl=true&mts.0=regular&{qs}&location=3000"
req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", "Referer": BUY})
try:
    data = json.load(urllib.request.urlopen(req, timeout=20))
except Exception as e:
    print("Apple 查询失败:", e)
    if os.environ.get("FIRST_RUN") == "1":
        bark("Duo 云端监控失败", f"GitHub 访问 Apple 被拦：{e}", False)
    raise SystemExit(1)

found = []
for s in data["body"]["content"]["pickupMessage"]["stores"]:
    for p, v in s.get("partsAvailability", {}).items():
        if p in PARTS and v.get("pickupDisplay") == "available":
            found.append((s["storeName"], PARTS[p], v.get("pickupSearchQuote", "")))
print("结果:", found or "无货")
for store, model, q in found:
    bark(f"Duo 有货 | {store}", f"{model}\n{q}\n点开去官网下单", True)
if os.environ.get("FIRST_RUN") == "1":
    bark("Duo 云端监控测试成功", "GitHub 能查到 Apple 库存：" + ("有货" if found else "当前无货"), False)
