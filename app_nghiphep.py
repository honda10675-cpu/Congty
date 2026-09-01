import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
from supabase import create_client

# --- CẤU HÌNH SUPABASE ---
SUPABASE_URL = "https://sndzaqqqrxoqlzemgboy.supabase.co"
# Dùng chung SUPABASE_KEY với app.py của anh
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZHphcXFxcnhvcWx6ZW1nYm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMDM1MDMsImV4cCI6MjEwMzY3OTUwM30.N-7hXggITi6yM8VZPtDMWehb1_i1IsR6P5vDMQ6-hJg"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = "123456"  # Mật khẩu duyệt Admin (Anh có thể đổi thành mật khẩu tùy chọn)

st.set_page_config(
    page_title="Đơn Xin Nghỉ Phép | 请假申请",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


def get_week_range(ref_date):
  # Tìm Thứ 2 của tuần chứa ref_date
  monday = ref_date - timedelta(days=ref_date.weekday())
  sunday = monday + timedelta(days=6)
  return monday, sunday


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


# CSS Tùy chỉnh giao diện gọn đẹp
st.markdown(
    """
    <style>
    :root { color-scheme: light !important; }
    header, footer, #MainMenu, [data-testid="stToolbar"], .stAppDeployButton, [data-testid="stHeader"] {
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #f4fbf7 !important; color: #1b4332 !important; }
    .block-container { padding: 0.5rem 1rem !important; }
    h1 { font-size: 1.2rem !important; font-weight: 800 !important; text-align: center; color: #1b4332 !important; margin-bottom: 10px; }
    .stTextInput label, .stSelectbox label, .stDateInput label { font-size: 11px !important; font-weight: bold !important; color: #1b4332 !important; }
    .stTextInput input, div[data-baseweb="select"], div[data-baseweb="input"] { background-color: #ffffff !important; color: #1b4332 !important; border: 1.5px solid #74c69d !important; border-radius: 5px !important; font-size: 12px !important; }
    div[data-testid="stForm"] { background-color: #ffffff !important; border: 1.5px solid #52b788 !important; border-radius: 8px !important; padding: 10px !important; }
    .stButton button { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: #ffffff !important; font-weight: bold !important; font-size: 12px !important; width: 100% !important; }
    .week-table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: #fff; border-radius: 8px; overflow: hidden; }
    .week-table th { background-color: #2d6a4f; color: white; padding: 8px; font-size: 12px; text-align: center; }
    .week-table td { border: 1px solid #d8f3dc; padding: 8px; font-size: 11px; text-align: center; vertical-align: top; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1>🏖️ QUẢN LÝ XIN NGHỈ PHÉP / 请假管理</h1>", unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "📝 NGHỈ PHÉP MỚI / 申请请假",
    "📅 LỊCH NGHỈ THEO TUẦN / 周请假表",
    "⚙️ QUẢN LÝ AD / 管理员",
])

# --- TAB 1: NGHỈ PHÉP MỚI ---
with tab1:
  hours_options = [f"{h:02d}:00" for h in range(24)]

  with st.form("form_nghi_phep", clear_on_submit=False):
    ho_ten = st.text_input("HỌ VÀ TÊN / 姓名 *")
    bo_phan = st.selectbox(
        "BỘ PHẬN / 部门 *", ["Thợ Điện / 电工", "Thợ Cơ Khí / 机械"]
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
      tu_gio = st.selectbox("Từ giờ / 开始时间", hours_options, index=7)  # 07:00
    with col2:
      den_ngay = st.date_input("Đến ngày / 结束日期", value=get_vn_now().date())
      den_gio = st.selectbox(
          "Đến giờ / 结束时间", hours_options, index=17
      )  # 17:00

    ly_do = st.text_input("LÝ DO NGHỈ / 请假原因")

    # Kiểm tra trùng lịch trước khi gửi
    checking_date_str = tu_ngay.strftime("%d/%m/%Y")

    # Đếm số người cùng bộ phận đã đăng ký trùng ngày
    is_conflict = False
    try:
      res_check = (
          supabase.table("nghiphep")
          .select("*")
          .eq("bo_phan", bo_phan)
          .eq("tu_ngay", checking_date_str)
          .neq("trang_thai", "Từ chối")
          .execute()
      )
      if len(res_check.data) >= 1:
        is_conflict = True
    except Exception:
      pass

    admin_pass = ""
    if is_conflict:
      st.warning(
          f"⚠️ Ngày {checking_date_str} đã có 1 {bo_phan} đăng ký nghỉ!"
      )
      st.info(
          "👉 Cần nhập Mật khẩu Admin để phê duyệt đăng ký thêm người thứ 2:"
      )
      admin_pass = st.text_input(
          "Mật khẩu Admin / 管理员密码", type="password"
      )

    submit = st.form_submit_button("🚀 GỬI ĐƠN NGHỈ PHÉP / 提交申请")

    if submit:
      if not ho_ten.strip():
        st.error("⚠️ Vui lòng nhập họ và tên / 请填写姓名")
      elif is_conflict and admin_pass != ADMIN_PASSWORD:
        st.error(
            "❌ Trùng lịch nghỉ! Mật khẩu Admin không đúng, không thể gửi đơn."
        )
      else:
        ly_do_zh = auto_translate_to_zh(ly_do.strip()) if ly_do.strip() else ""
        full_ly_do = (
            f"{ly_do.strip()} ({ly_do_zh})" if ly_do_zh else ly_do.strip()
        )

        status = "Đã duyệt" if is_conflict else "Đã duyệt"

        new_data = {
            "ho_ten": ho_ten.strip(),
            "bo_phan": bo_phan,
            "loai_nghi": loai_nghi,
            "tu_ngay": tu_ngay.strftime("%d/%m/%Y"),
            "tu_gio": tu_gio,
            "den_ngay": den_ngay.strftime("%d/%m/%Y"),
            "den_gio": den_gio,
            "ly_do": full_ly_do,
            "trang_thai": status,
        }
        try:
          supabase.table("nghiphep").insert(new_data).execute()
          st.success("🎉 Đã gửi đơn xin nghỉ phép thành công / 提交成功！")
        except Exception as e:
          st.error(f"❌ Lỗi gửi dữ liệu: {e}")

# --- TAB 2: LỊCH NGHỈ THEO TUẦN ---
with tab2:
  now_vn = get_vn_now().date()

  week_choice = st.radio(
      "Chọn tuần xem lịch / 选择周:",
      ["Tuần này / 本周", "Tuần sau / 下周"],
      horizontal=True,
  )

  if "Tuần sau" in week_choice:
    target_date = now_vn + timedelta(days=7)
  else:
    target_date = now_vn

  mon, sun = get_week_range(target_date)
  st.write(
      f"📅 **Lịch từ Thứ 2 ({mon.strftime('%d/%m/%Y')}) đến Chủ Nhật ({sun.strftime('%d/%m/%Y')})**"
  )

  # Tạo danh sách các ngày trong tuần
  days_in_week = [mon + timedelta(days=i) for i in range(7)]
  days_headers = [
      f"T{i+2}\n({d.strftime('%d/%m')})" if i < 6 else f"CN\n({d.strftime('%d/%m')})"
      for i, d in enumerate(days_in_week)
  ]

  try:
    res = (
        supabase.table("nghiphep")
        .select("*")
        .neq("trang_thai", "Từ chối")
        .execute()
    )
    df_all = pd.DataFrame(res.data)

    for dept in ["Thợ Điện / 电工", "Thợ Cơ Khí / 机械"]:
      st.subheader(f"🔹 {dept}")
      row_data = []

      for d in days_in_week:
        d_str = d.strftime("%d/%m/%Y")
        names = []
        if not df_all.empty and "tu_ngay" in df_all.columns:
          matched = df_all[
              (df_all["bo_phan"] == dept) & (df_all["tu_ngay"] == d_str)
          ]
          for _, r in matched.iterrows():
            time_str = f"({r.get('tu_gio','')} - {r.get('den_gio','')})"
            names.append(f"<b>{r['ho_ten']}</b><br><small>{time_str}</small>")

        row_data.append("<br><br>".join(names) if names else "-")

      # Tạo bảng HTML hiển thị gọn đẹp
      html_table = f"""
            <table class="week-table">
                <tr>{"".join([f"<th>{h}</th>" for h in days_headers])}</tr>
                <tr>{"".join([f"<td>{cell}</td>" for cell in row_data])}</tr>
            </table>
            """
      st.markdown(html_table, unsafe_allow_html=True)
      st.write("")

  except Exception as e:
    st.error(f"Lỗi tải dữ liệu lịch tuần: {e}")

# --- TAB 3: QUẢN LÝ AD ---
with tab3:
  ad_pass = st.text_input(
      "Nhập mật khẩu Admin để quản lý:", type="password", key="ad_tab_pass"
  )
  if ad_pass == ADMIN_PASSWORD:
    st.success("Đã xác thực quyền Admin")
    try:
      res_admin = (
          supabase.table("nghiphep")
          .select("*")
          .order("id", desc=True)
          .execute()
      )
      df_ad = pd.DataFrame(res_admin.data)
      if not df_ad.empty:
        st.dataframe(df_ad, use_container_width=True)
      else:
        st.info("Chưa có danh sách nghỉ phép.")
    except Exception as e:
      st.error(f"Lỗi: {e}")
  elif ad_pass:
    st.error("Mật khẩu Admin không đúng!")
