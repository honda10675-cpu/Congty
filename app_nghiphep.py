import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
from supabase import create_client

# --- CẤU HÌNH SUPABASE ---
SUPABASE_URL = "https://sndzaqqqrxoqlzemgboy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZHphcXFxcnhvcWx6ZW1nYm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMDM1MDMsImV4cCI6MjEwMzY3OTUwM30.N-7hXggITi6yM8VZPtDMWehb1_i1IsR6P5vDMQ6-hJg"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
ADMIN_PASSWORD = "023"  # Mật khẩu quản lý

# --- DANH SÁCH 33 NHÂN VIÊN ---
DANH_SACH_NHAN_VIEN = [
    "-- Chọn nhân viên / 选择员工 --",
    # --- THỢ ĐIỆN (16 Người) ---
    "Trương Văn Nhiển",
    "Điện 02", "Điện 03", "Điện 04", "Điện 05",
    "Điện 06", "Điện 07", "Điện 08", "Điện 09", "Điện 10",
    "Điện 11", "Điện 12", "Điện 13", "Điện 14", "Điện 15", "Điện 16",
    # --- THỢ CƠ KHÍ (17 Người) ---
    "Cơ Khí 01", "Cơ Khí 02", "Cơ Khí 03", "Cơ Khí 04", "Cơ Khí 05",
    "Cơ Khí 06", "Cơ Khí 07", "Cơ Khí 08", "Cơ Khí 09", "Cơ Khí 10",
    "Cơ Khí 11", "Cơ Khí 12", "Cơ Khí 13", "Cơ Khí 14", "Cơ Khí 15",
    "Cơ Khí 16", "Cơ Khí 17"
]

st.set_page_config(
    page_title="Đăng Ký Nghỉ Phép | 请假",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


def get_week_range(ref_date):
  monday = ref_date - timedelta(days=ref_date.weekday())
  sunday = monday + timedelta(days=6)
  return monday, sunday


def get_existing_columns():
  try:
    res = supabase.table("nghiphep").select("*").limit(1).execute()
    if res.data and len(res.data) > 0:
      return list(res.data[0].keys())
  except Exception:
    pass
  return []


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
    .stSelectbox label, .stDateInput label { font-size: 11px !important; font-weight: bold !important; color: #1b4332 !important; }
    div[data-baseweb="select"], div[data-baseweb="input"] { background-color: #ffffff !important; color: #1b4332 !important; border: 1.5px solid #74c69d !important; border-radius: 5px !important; font-size: 12px !important; }
    div[data-testid="stForm"] { background-color: #ffffff !important; border: 1.5px solid #52b788 !important; border-radius: 8px !important; padding: 10px !important; }
    .stButton button { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: #ffffff !important; font-weight: bold !important; font-size: 12px !important; width: 100% !important; }
    .week-table { width: 100%; border-collapse: collapse; margin-top: 5px; background-color: #fff; border-radius: 8px; overflow: hidden; }
    .week-table th { background-color: #2d6a4f; color: white; padding: 6px; font-size: 11px; text-align: center; }
    .week-table td { border: 1px solid #d8f3dc; padding: 10px 6px; font-size: 12px; text-align: center; vertical-align: top; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1>🏖️ QUẢN LÝ XIN NGHỈ PHÉP / 请假管理</h1>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs([
    "📝 NGHỈ PHÉP / 申请",
    "📅 LỊCH THEO TUẦN / 周表",
    "⚙️ QUẢN LÝ / 设置",
])

# --- TAB 1: ĐĂNG KÝ TỐI GIẢN ---
with tab1:
  with st.form("form_nghi_phep", clear_on_submit=False):
    ho_ten = st.selectbox("HỌ VÀ TÊN / 姓名 *", DANH_SACH_NHAN_VIEN)
    loai_nghi = st.selectbox(
        "LOẠI NGHỈ / 类型 *",
        [
            "Nghỉ phép năm / 年假",
            "Nghỉ việc riêng / 事假",
            "Nghỉ bệnh / 病假",
            "Khác / 其他",
        ],
    )
    ngay_nghi = st.date_input("NGÀY NGHỈ / 日期 *", value=get_vn_now().date())

    checking_date_str = ngay_nghi.strftime("%Y-%m-%d")

    # Kiểm tra trùng lịch
    is_conflict = False
    try:
      res_all = supabase.table("nghiphep").select("*").execute()
      if res_all.data:
        df_chk = pd.DataFrame(res_all.data)
        col_dt = (
            "tu_ngay"
            if "tu_ngay" in df_chk.columns
            else "ngay_nghi"
            if "ngay_nghi" in df_chk.columns
            else None
        )
        if col_dt:
          df_chk["clean_dt"] = df_chk[col_dt].astype(str).str.strip().str[:10]
          matched = df_chk[df_chk["clean_dt"] == checking_date_str]
          if len(matched) >= 1:
            is_conflict = True
    except Exception:
      pass

    admin_pass = ""
    if is_conflict:
      st.warning(
          f"⚠️ Ngày {ngay_nghi.strftime('%d/%m/%Y')} đã có người đăng ký"
          " nghỉ!"
      )
      st.info("👉 Nhập mật khẩu 023 nếu muốn đăng ký thêm người tiếp theo:")
      admin_pass = st.text_input("Mật khẩu / 密码", type="password")

    submit = st.form_submit_button("🚀 GỬI ĐƠN / 提交")

    if submit:
      if ho_ten == "-- Chọn nhân viên / 选择员工 --":
        st.error("⚠️ Vui lòng chọn Họ và tên! / 请选择姓名！")
      elif is_conflict and admin_pass != ADMIN_PASSWORD:
        st.error("❌ Mật khẩu không đúng! Không thể đăng ký thêm.")
      else:
        existing_cols = get_existing_columns()
        new_data = {}

        clean_name = ho_ten.strip()
        if "ho_ten" in existing_cols:
          new_data["ho_ten"] = clean_name
        if "ten_nhanvien" in existing_cols:
          new_data["ten_nhanvien"] = clean_name
        if "hoten" in existing_cols:
          new_data["hoten"] = clean_name

        if "loai_nghi" in existing_cols:
          new_data["loai_nghi"] = loai_nghi
        if "tu_ngay" in existing_cols:
          new_data["tu_ngay"] = checking_date_str
        if "den_ngay" in existing_cols:
          new_data["den_ngay"] = checking_date_str
        if "ngay_nghi" in existing_cols:
          new_data["ngay_nghi"] = checking_date_str
        if "ly_do" in existing_cols:
          new_data["ly_do"] = loai_nghi

        try:
          supabase.table("nghiphep").insert(new_data).execute()
          st.success("🎉 Đăng ký thành công / 提交成功！")
          st.rerun()
        except Exception as e:
          st.error(f"❌ Lỗi gửi dữ liệu: {e}")

# --- TAB 2: LỊCH NGHỈ THEO TUẦN (1 BẢNG DUY NHẤT) ---
with tab2:
  now_vn = get_vn_now().date()
  week_choice = st.radio(
      "Chọn tuần / 选择周:",
      ["Tuần này / 本周", "Tuần sau / 下周"],
      horizontal=True,
  )

  target_date = (
      now_vn + timedelta(days=7) if "Tuần sau" in week_choice else now_vn
  )
  mon, sun = get_week_range(target_date)

  st.write(
      f"📅 **Lịch từ Thứ 2 ({mon.strftime('%d/%m/%Y')}) đến Chủ Nhật ({sun.strftime('%d/%m/%Y')})**"
  )

  days_in_week = [mon + timedelta(days=i) for i in range(7)]
  days_headers = [
      f"T{i+2}<br>({d.strftime('%d/%m')})"
      if i < 6
      else f"CN<br>({d.strftime('%d/%m')})"
      for i, d in enumerate(days_in_week)
  ]

  try:
    res = supabase.table("nghiphep").select("*").execute()
    df_all = pd.DataFrame(res.data)

    col_dt = (
        "tu_ngay"
        if "tu_ngay" in df_all.columns
        else "ngay_nghi"
        if "ngay_nghi" in df_all.columns
        else None
    )
    col_name = (
        "ho_ten"
        if "ho_ten" in df_all.columns
        else "ten_nhanvien"
        if "ten_nhanvien" in df_all.columns
        else "hoten"
        if "hoten" in df_all.columns
        else None
    )

    row_data = []

    if not df_all.empty and col_dt:
      df_all["clean_date"] = df_all[col_dt].astype(str).str.strip().str[:10]

    for d in days_in_week:
      d_str = d.strftime("%Y-%m-%d")
      entries = []

      if not df_all.empty and col_dt and col_name:
        matched = df_all[df_all["clean_date"] == d_str]
        for _, r in matched.iterrows():
          name_str = str(r.get(col_name, ""))
          entries.append(
              f"<span style='color:#d90429;'>👤 {name_str}</span>"
          )

      row_data.append("<br><br>".join(entries) if entries else "-")

    html_table = f"""
        <table class="week-table">
            <tr>{"".join([f"<th>{h}</th>" for h in days_headers])}</tr>
            <tr>{"".join([f"<td>{cell}</td>" for cell in row_data])}</tr>
        </table>
        """
    st.markdown(html_table, unsafe_allow_html=True)

  except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")

# --- TAB 3: SỬA / XÓA ĐƠN ---
with tab3:
  pass_input = st.text_input(
      "🔑 Nhập mật khẩu 023 để quản lý:", type="password"
  )
  if pass_input == ADMIN_PASSWORD:
    st.success("🔓 Quyền ADMIN!")
    try:
      res_edit = (
          supabase.table("nghiphep")
          .select("*")
          .order("id", desc=True)
          .execute()
      )
      df_edit = pd.DataFrame(res_edit.data)

      if not df_edit.empty:
        col_dt = (
            "tu_ngay"
            if "tu_ngay" in df_edit.columns
            else "ngay_nghi"
            if "ngay_nghi" in df_edit.columns
            else None
        )
        col_name = (
            "ho_ten"
            if "ho_ten" in df_edit.columns
            else "ten_nhanvien"
            if "ten_nhanvien" in df_edit.columns
            else "hoten"
            if "hoten" in df_edit.columns
            else None
        )

        for _, row in df_edit.iterrows():
          dt_val = row.get(col_dt, "") if col_dt else ""
          nm_val = row.get(col_name, "") if col_name else ""
          with st.expander(f"📌 ID {row['id']}: {nm_val} - Ngày: {dt_val}"):
            if st.button("🗑️ Xóa đơn này", key=f"btn_del_{row['id']}"):
              supabase.table("nghiphep").delete().eq(
                  "id", row["id"]
              ).execute()
              st.warning("Đã xóa!")
              st.rerun()
      else:
        st.info("Chưa có dữ liệu.")
    except Exception as e:
      st.error(f"Lỗi: {e}")
  elif pass_input:
    st.error("Mật khẩu không đúng!")
