def auto_translate_to_zh(text):
  """Dịch tiếng Việt sang Tiếng Trung (Không lấy Pinyin)"""
  if not text or not text.strip():
    return ""

  query_text = text.strip()

  try:
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=zh-CN&dt=t&q={urllib.parse.quote(query_text)}"
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
      result = json.loads(response.read().decode("utf-8"))

      zh_parts = []
      if result and len(result) > 0 and result[0]:
        for item in result[0]:
          if len(item) > 0 and item[0]:
            zh_parts.append(item[0])

      return "".join(zh_parts).strip()
  except Exception:
    pass

  return ""
