import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
from supabase import create_client

# --- CẤU HÌNH SUPABASE ---
SUPABASE_URL = "https://sndzaqqqrxoqlzemgboy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZHphcXFxcnhvcWx6ZW1nYm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDM2MDM1MDMsImV4cCI6MjAyOTE3OTUwM30.n-7hXggITi6yM8VZPtDMWehb1_i1IsR6P5vDMQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Đơn Xin Nghỉ Phép | 请假申请",
    page_icon="🏖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


def auto_translate_to_zh(text):
  if not text or not text.strip():
    return ""
  query_text = text.strip()
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }
  try:
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=zh-CN&dt=t&q={urllib.parse.quote(query_text)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=3) as response:
      result = json.loads(response.read().decode("utf-8"))
      if result and len(result) > 0 and result[0]:
        zh_parts = [
            item[0] for item in result[0] if len(item) > 0 and item[0]
        ]
        return "".join(zh_parts).strip()
  except Exception:
    pass
  return ""


st.markdown(
    """
    <style>
    :root { color-scheme: light !important; }
    header, footer, #MainMenu, [data-testid="stToolbar"], .stAppDeployButton, [data-testid="stHeader"] {
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #f4fbf7 !important; color: #1b4332 !important; }
    .block-container { padding: 0.2rem !important; }
    h1 { font-size: 1rem !important; margin: 0 !important; font-weight: 800 !important; text-align: center; color: #1b4332 !important; }
    .stTextInput label, .stSelectbox label, .stDateInput label { font-size: 11px !important; font-weight: bold !important; color: #1b4332 !important; }
    .stTextInput input, div[data-baseweb="select"], div[data-baseweb="input"] { background-color: #ffffff !important; color: #1b4332 !important; border: 1.5px solid #74c69d !important; border-radius: 5px !important; font-size: 12px !important; }
    div[data-testid="stForm"] { background-color: #ffffff !important; border: 1.5px solid #52b788 !important; border-radius: 8px !important; padding: 8px !important; }
    .stButton button { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: #ffffff !important; font-weight: bold !important; font-size: 12px !important; width: 100% !important; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1>🏖️ QUẢN LÝ XIN NGHỈ PHÉP / 请假管理</h1>", unsafe_allow_html=True
)

tab1, tab2 = st.tabs(
    ["📝 NGHỈ PHÉP MỚI / 申请请假", "📊 DANH SÁCH / 请假列表"]
)

with tab1:
  with st.form("form_nghi_phep", clear_on_submit=True):
    ho_ten = st.text_input("HỌ VÀ TÊN / 姓名 *")
    bo_phan = st.selectbox(
        "BỘ PHẬN / 部门 *",
        ["Thợ Điện / 电工", "Cơ Khí / 机械", "Khác / 其他"],
    )
    loai_nghi = st.selectbox(
        "LOẠI NGHỈ / 请假类型 *",
        [
            "Nghỉ phép năm / 年假",
            "Nghỉ việc riêng / 事假",
            "Nghỉ bệnh / 病假",
            "Khác / 其他",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
      tu_ngay = st.date_input("Từ ngày / 开始日期", value=get_vn_now().date())
    with col2:
      den_ngay = st.date_input("Đến ngày / 结束日期", value=get_vn_now().date())

    ly_do = st.text_input("LÝ DO NGHỈ / 请假原因")
    submit = st.form_submit_button("🚀 GỬI ĐƠN NGHỈ PHÉP / 提交申请")

    if submit:
      if not ho_ten.strip():
        st.error("⚠️ Vui lòng nhập họ và tên / 请填写姓名")
      else:
        ly_do_zh = auto_translate_to_zh(ly_do.strip()) if ly_do.strip() else ""
        full_ly_do = (
            f"{ly_do.strip()} ({ly_do_zh})" if ly_do_zh else ly_do.strip()
        )

        new_data = {
            "ho_ten": ho_ten.strip(),
            "bo_phan": bo_phan,
            "loai_nghi": loai_nghi,
            "tu_ngay": tu_ngay.strftime("%d/%m/%Y"),
            "den_ngay": den_ngay.strftime("%d/%m/%Y"),
            "ly_do": full_ly_do,
            "trang_thai": "Chờ duyệt",
        }
        try:
          supabase.table("nghiphep").insert(new_data).execute()
          st.success("🎉 Đã gửi đơn xin nghỉ phép thành công / 提交成功！")
        except Exception as e:
          st.error(f"❌ Lỗi gửi dữ liệu: {e}")

with tab2:
  try:
    res = (
        supabase.table("nghiphep").select("*").order("id", desc=True).execute()
    )
    df = pd.DataFrame(res.data)
    if not df.empty:
      st.dataframe(
          df[[
              "ho_ten",
              "bo_phan",
              "loai_nghi",
              "tu_ngay",
              "den_ngay",
              "ly_do",
              "trang_thai",
          ]],
          use_container_width=True,
      )
    else:
      st.info("Chưa có dữ liệu nghỉ phép / 暂无请假记录")
  except Exception as e:
    st.error(f"Lỗi tải danh sách: {e}")
