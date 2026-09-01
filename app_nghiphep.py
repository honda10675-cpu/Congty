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
    # --- BỘ PHẬN THỢ ĐIỆN (16 Người) ---
    "Trương Văn Nhiển (Thợ Điện)",
    "Điện 02", "Điện 03", "Điện 04", "Điện 05",
    "Điện 06", "Điện 07", "Điện 08", "Điện 09", "Điện 10",
    "Điện 11", "Điện 12", "Điện 13", "Điện 14", "Điện 15", "Điện 16",
    # --- BỘ PHẬN THỢ CƠ KHÍ (17 Người) ---
    "Cơ Khí 01", "Cơ Khí 02", "Cơ Khí 03", "Cơ Khí 04", "Cơ Khí 05",
    "Cơ Khí 06", "Cơ Khí 07", "Cơ Khí 08", "Cơ Khí 09", "Cơ Khí 10",
    "Cơ Khí 11", "Cơ Khí 12", "Cơ Khí 13", "Cơ Khí 14", "Cơ Khí 15",
    "Cơ Khí 16", "Cơ Khí 17"
]

st.set_page_config(
    page_title="Quản Lý Nghỉ Phép & Tăng Ca | 请假与加班管理",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "tong_dien" not in st.session_state:
  st.session_state.tong_dien = 16
if "tong_cokhi" not in st.session_state:
  st.session_state.tong_cokhi = 17


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


def get_week_range(ref_date):
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
    .stTextInput label, .stSelectbox label, .stDateInput label, .stNumberInput label { font-size: 11px !important; font-weight: bold !important; color: #1b4332 !important; }
    .stTextInput input, div[data-baseweb="select"], div[data-baseweb="input"] { background-color: #ffffff !important; color: #1b4332 !important; border: 1.5px solid #74c69d !important; border-radius: 5px !important; font-size: 12px !important; }
    div[data-testid="stForm"] { background-color: #ffffff !important; border: 1.5px solid #52b788 !important; border-radius: 8px !important; padding: 10px !important; }
    .stButton button { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: #ffffff !important; font-weight: bold !important; font-size: 12px !important; width: 100% !important; }
    .week-table { width: 100%; border-collapse: collapse; margin-top: 5px; background-color: #fff; border-radius: 8px; overflow: hidden; }
    .week-table th { background-color: #2d6a4f; color: white; padding: 6px; font-size: 11px; text-align: center; }
    .week-table td { border: 1px solid #d8f3dc; padding: 6px; font-size: 11px; text-align: center; vertical-align: top; }
    .summary-table { width: 100%; border-collapse: collapse; margin-top: 5px; background-color: #fff; border-radius: 8px; overflow: hidden; }
    .summary-table th { background-color: #1b4332; color: white; padding: 6px; font-size: 11px; text-align: center; }
    .summary-table td { border: 1px solid #b7e4c7; padding: 6px; font-size: 11px; text-align: center; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1>🏖️ QUẢN LÝ XIN NGHỈ PHÉP & TĂNG CA / 请假与加班管理</h1>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs([
    "📝 NGHỈ PHÉP & TĂNG CA / 申请",
    "📅 LỊCH THEO TUẦN / 周表",
    "⚙️ CÀI ĐẶT & SỬA ĐƠN / 设置",
])

# --- TAB 1: ĐĂNG KÝ NGHỈ PHÉP / TĂNG CA ---
with tab1:
  with st.form("form_nghi_phep", clear_on_submit=False):
    ho_ten = st.selectbox("HỌ VÀ TÊN / 姓名 *", DANH_SACH_NHAN_VIEN)
    bo_phan = st.selectbox(
        "BỘ PHẬN / 部门 *", ["Thợ Điện / 电工", "Thợ Cơ Khí / 机械"]
    )
    loai_don = st.selectbox(
        "LOẠI ĐƠN / 申请类型 *",
        ["Xin nghỉ phép / 请假", "Đăng ký tăng ca / 加班"],
    )
    ca_lam_nghi = st.selectbox(
        "CA NGHỈ / CA TĂNG CA (班次) *", ["Ca ngày / 白班", "Ca đêm / 夜班"]
    )
    loai_nghi = st.selectbox(
        "LÝ DO CỤ THỂ / 类型 *",
        [
            "Nghỉ phép năm / 年假",
            "Nghỉ việc riêng / 事假",
            "Nghỉ bệnh / 病假",
            "Tăng ca sản xuất / 加班",
            "Khác / 其他",
        ],
    )
    ngay_nghi = st.date_input("NGÀY / 日期 *", value=get_vn_now().date())
    ly_do = st.text_input("GHI CHÚ / CHI TIẾT (原因/备注) *")

    checking_date_str = ngay_nghi.strftime("%Y-%m-%d")

    is_conflict = False
    try:
      res_all = supabase.table("nghiphep").select("*").execute()
      if res_all.data:
        df_chk = pd.DataFrame(res_all.data)
        col_bp = (
            "bophan_thotien"
            if "bophan_thotien" in df_chk.columns
            else "bo_phan"
            if "bo_phan" in df_chk.columns
            else None
        )
        col_dt = (
            "tu_ngay"
            if "tu_ngay" in df_chk.columns
            else "ngay_nghi"
            if "ngay_nghi" in df_chk.columns
            else None
        )

        if col_bp and col_dt and "Xin nghỉ" in loai_don:
          df_chk["clean_dt"] = df_chk[col_dt].astype(str).str.strip().str[:10]
          matched = df_chk[
              (df_chk[col_bp] == bo_phan)
              & (df_chk["clean_dt"] == checking_date_str)
              & (~df_chk["ly_do"].astype(str).str.contains("Tăng ca", na=False))
          ]
          if len(matched) >= 1:
            is_conflict = True
    except Exception:
      pass

    admin_pass = ""
    if is_conflict:
      st.warning(
          f"⚠️ Ngày {ngay_nghi.strftime('%d/%m/%Y')} đã có 1 {bo_phan} xin"
          " nghỉ!"
      )
      st.info("👉 Nhập mật khẩu 023 để duyệt thêm người thứ 2:")
      admin_pass = st.text_input("Mật khẩu / 密码", type="password")

    submit = st.form_submit_button("🚀 GỬI ĐƠN / 提交申请")

    if submit:
      if ho_ten == "-- Chọn nhân viên / 选择员工 --":
        st.error("⚠️ Vui lòng chọn Họ và tên! / 请选择姓名！")
      elif not ly_do.strip():
        st.error("⚠️ Vui lòng nhập ghi chú / lý do! / 请填写原因/备注！")
      elif is_conflict and admin_pass != ADMIN_PASSWORD:
        st.error("❌ Mật khẩu không đúng! Không thể đăng ký trùng ngày.")
      else:
        ly_do_zh = auto_translate_to_zh(ly_do.strip()) if ly_do.strip() else ""
        full_ly_do = f"[{loai_don}] [{ca_lam_nghi}] {ly_do.strip()} ({ly_do_zh})"

        existing_cols = get_existing_columns()
        new_data = {}

        clean_name = ho_ten.split(" (")[0].strip()
        if "ho_ten" in existing_cols:
          new_data["ho_ten"] = clean_name
        if "ten_nhanvien" in existing_cols:
          new_data["ten_nhanvien"] = clean_name
        if "hoten" in existing_cols:
          new_data["hoten"] = clean_name

        if "bo_phan" in existing_cols:
          new_data["bo_phan"] = bo_phan
        if "bophan_thotien" in existing_cols:
          new_data["bophan_thotien"] = bo_phan
        if "loai_nghi" in existing_cols:
          new_data["loai_nghi"] = loai_nghi
        if "tu_ngay" in existing_cols:
          new_data["tu_ngay"] = checking_date_str
        if "den_ngay" in existing_cols:
          new_data["den_ngay"] = checking_date_str
        if "ngay_nghi" in existing_cols:
          new_data["ngay_nghi"] = checking_date_str
        if "ly_do" in existing_cols:
          new_data["ly_do"] = full_ly_do
        if "trang_thai" in existing_cols:
          new_data["trang_thai"] = "Đã duyệt"

        try:
          supabase.table("nghiphep").insert(new_data).execute()
          st.success("🎉 Gửi đơn thành công / 提交成功！")
          st.rerun()
        except Exception as e:
          st.error(f"❌ Lỗi gửi dữ liệu: {e}")

# --- TAB 2: LỊCH THEO TUẦN ---
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
      f"📅 **Từ Thứ 2 ({mon.strftime('%d/%m/%Y')}) đến Chủ Nhật ({sun.strftime('%d/%m/%Y')})**"
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

    col_bp = (
        "bophan_thotien"
        if "bophan_thotien" in df_all.columns
        else "bo_phan"
        if "bo_phan" in df_all.columns
        else None
    )
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

    st.subheader("📋 1. LỊCH ĐĂNG KÝ NGHỈ PHÉP & TĂNG CA")

    row_data = []
    count_dien_nghi = [0] * 7
    count_cokhi_nghi = [0] * 7

    if not df_all.empty and col_dt:
      df_all["clean_date"] = df_all[col_dt].astype(str).str.strip().str[:10]

    for idx, d in enumerate(days_in_week):
      d_str = d.strftime("%Y-%m-%d")
      entries = []

      if not df_all.empty and col_dt and col_name:
        matched = df_all[df_all["clean_date"] == d_str]
        for _, r in matched.iterrows():
          reason_str = str(r.get("ly_do", ""))
          dept_str = str(r.get(col_bp, ""))
          name_str = str(r.get(col_name, ""))

          is_tangca = "Tăng ca" in reason_str
          ca_tag = "Đêm" if "Ca đêm" in reason_str else "Ngày"
          dept_tag = "Điện" if "Điện" in dept_str else "Cơ khí"

          if not is_tangca:
            if "Điện" in dept_str:
              count_dien_nghi[idx] += 1
            else:
              count_cokhi_nghi[idx] += 1

            color = "#d90429"  # Đỏ cho nghỉ
            tag_label = f"Nghỉ-{ca_tag}"
          else:
            color = "#2a9d8f"  # Xanh cho tăng ca
            tag_label = f"TăngCa-{ca_tag}"

          entries.append(
              f"<b>{name_str}</b> ({dept_tag})<br><span style='color:{color};"
              f" font-size:10px;'>[{tag_label}]</span>"
          )

      row_data.append("<br><br>".join(entries) if entries else "-")

    html_table = f"""
        <table class="week-table">
            <tr>{"".join([f"<th>{h}</th>" for h in days_headers])}</tr>
            <tr>{"".join([f"<td>{cell}</td>" for cell in row_data])}</tr>
        </table>
        """
    st.markdown(html_table, unsafe_allow_html=True)

    # --- BẢNG THỐNG KÊ SỐ LƯỢNG NGHỈ ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 2. THỐNG KÊ SỐ NGƯỜI NGHỈ TRONG NGÀY")

    row_dien_html = [f"<span style='color:#d90429;'>{c} người</span>" for c in count_dien_nghi]
    row_cokhi_html = [f"<span style='color:#d90429;'>{c} người</span>" for c in count_cokhi_nghi]

    summary_table_html = f"""
        <table class="summary-table">
            <tr>
                <th>Bộ phận</th>
                {"".join([f"<th>{h}</th>" for h in days_headers])}
            </tr>
            <tr>
                <td><b>⚡ Thợ Điện nghỉ</b></td>
                {"".join([f"<td>{cell}</td>" for cell in row_dien_html])}
            </tr>
            <tr>
                <td><b>🔧 Thợ Cơ Khí nghỉ</b></td>
                {"".join([f"<td>{cell}</td>" for cell in row_cokhi_html])}
            </tr>
        </table>
        """
    st.markdown(summary_table_html, unsafe_allow_html=True)

  except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")

# --- TAB 3: CÀI ĐẶT & SỬA ĐƠN ---
with tab3:
  pass_input = st.text_input(
      "🔑 Nhập mật khẩu 023 để quản lý:", type="password"
  )
  if pass_input == ADMIN_PASSWORD:
    st.success("🔓 Đã xác thực quyền ADMIN!")

    st.write("👥 **Cấu hình tổng nhân sự mặc định:**")
    col_d, col_ck = st.columns(2)
    with col_d:
      st.session_state.tong_dien = st.number_input(
          "Tổng Thợ Điện", value=st.session_state.tong_dien, step=1
      )
    with col_ck:
      st.session_state.tong_cokhi = st.number_input(
          "Tổng Thợ Cơ Khí", value=st.session_state.tong_cokhi, step=1
      )

    st.markdown("---")

    try:
      res_edit = (
          supabase.table("nghiphep")
          .select("*")
          .order("id", desc=True)
          .execute()
      )
      df_edit = pd.DataFrame(res_edit.data)

      if not df_edit.empty:
        st.write("📋 **Danh sách đơn đã đăng ký:**")
        col_bp = (
            "bophan_thotien"
            if "bophan_thotien" in df_edit.columns
            else "bo_phan"
            if "bo_phan" in df_edit.columns
            else None
        )
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
          bp_val = row.get(col_bp, "") if col_bp else ""
          dt_val = row.get(col_dt, "") if col_dt else ""
          nm_val = row.get(col_name, "") if col_name else ""
          with st.expander(
              f"📌 ID {row['id']}: {nm_val} - {bp_val} - Ngày: {dt_val}"
          ):
            c1, c2 = st.columns(2)
            with c1:
              new_name = st.text_input(
                  "Họ tên", value=str(nm_val), key=f"name_{row['id']}"
              )
              new_dept = st.selectbox(
                  "Bộ phận",
                  ["Thợ Điện / 电工", "Thợ Cơ Khí / 机械"],
                  index=0 if "Điện" in str(bp_val) else 1,
                  key=f"dept_{row['id']}",
              )
            with c2:
              new_date = st.text_input(
                  "Ngày (YYYY-MM-DD)",
                  value=str(dt_val),
                  key=f"date_{row['id']}",
              )
              new_reason = st.text_input(
                  "Ghi chú / Lý do",
                  value=str(row.get("ly_do", "")),
                  key=f"reason_{row['id']}",
              )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
              if st.button("💾 Cập nhật", key=f"btn_up_{row['id']}"):
                up_dict = {}
                if col_name:
                  up_dict[col_name] = new_name
                if col_bp:
                  up_dict[col_bp] = new_dept
                if col_dt:
                  up_dict[col_dt] = new_date
                if "ly_do" in df_edit.columns:
                  up_dict["ly_do"] = new_reason

                supabase.table("nghiphep").update(up_dict).eq(
                    "id", row["id"]
                ).execute()
                st.success("Đã cập nhật!")
                st.rerun()
            with col_btn2:
              if st.button("🗑️ Xóa đơn", key=f"btn_del_{row['id']}"):
                supabase.table("nghiphep").delete().eq(
                    "id", row["id"]
                ).execute()
                st.warning("Đã xóa đơn!")
                st.rerun()
      else:
        st.info("Chưa có dữ liệu.")
    except Exception as e:
      st.error(f"Lỗi: {e}")
  elif pass_input:
    st.error("Mật khẩu không đúng!")
