from datetime import datetime, timedelta, timezone
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Báo Cáo Sự Cố",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_NAME = "su_co_v5.db"


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


def init_db():
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS su_co (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thiet_bi TEXT,
            thoi_gian_bao TEXT,
            ten_su_co TEXT,
            du_kien_xong TEXT,
            nguoi_bao_cao TEXT,
            trang_thai TEXT DEFAULT 'Đang xử lý',
            thoi_gian_xong TEXT DEFAULT ''
        )
    """)
  conn.commit()
  conn.close()


init_db()

# CSS CAN THIỆP SÂU - ÉP 1 HÀNG DỌC DI ĐỘNG & ẨN LOGO
st.markdown(
    """
    <style>
    /* 1. ẨN TRIỆT ĐỂ LOGO STREAMLIT & HOSTING BADGE */
    header, footer, #MainMenu, [data-testid="stToolbar"], 
    .stAppDeployButton, [data-testid="stStatusWidget"],
    div[class*="viewerBadge"], div[class*="styles_viewerBadge"],
    a[href*="streamlit.io"], iframe[title*="Streamlit"],
    .stApp > footer, [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    .stApp { background-color: #f4fbf7; color: #1b4332; }

    /* 2. KHU VỰC LỀ SIÊU GỌN VỪA KHÍT MÀN HÌNH */
    .block-container { 
        padding-top: 0.1rem !important; 
        padding-bottom: 0.1rem !important; 
        padding-left: 0.2rem !important; 
        padding-right: 0.2rem !important; 
    }

    h1 { font-size: 0.95rem !important; margin: 0 !important; font-weight: 800 !important; text-align: center; }

    /* 3. ĐỊNH DẠNG BẢNG HTML VỪA VẶN 1 HÀNG NGANG MÀN HÌNH DI ĐỘNG */
    .custom-table-container {
        width: 100%;
        overflow-x: hidden;
        margin-bottom: 5px;
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 10px !important;
        background-color: #ffffff;
    }
    .custom-table th {
        background-color: #2d6a4f;
        color: #ffffff;
        padding: 4px 2px;
        text-align: center;
        border: 1px solid #52b788;
        font-size: 10px;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 4px 2px;
        border: 1px solid #b7e4c7;
        text-align: center;
        word-wrap: break-word;
        font-size: 10px;
    }

    /* 4. TỐI ƯU FORM NHẬP */
    div[data-testid="stForm"] { 
        background-color: #ffffff; 
        border: 1.5px solid #52b788; 
        border-radius: 6px; 
        padding: 4px 6px !important; 
    }

    .stTextInput label, .stSelectbox label, .stDateInput label { 
        font-size: 10px !important; 
        margin-bottom: 0px !important; 
        font-weight: bold;
    }

    div[data-testid="stVerticalBlock"] > div { gap: 0.1rem !important; }

    .stTextInput input, div[data-baseweb="select"], div[data-baseweb="input"] { 
        background-color: #f8fff9 !important; 
        border: 1px solid #74c69d !important; 
        border-radius: 4px !important; 
        font-size: 11px !important; 
        height: 30px !important; 
        min-height: 30px !important;
    }

    .stButton button, button[kind="FormSubmitButton"] { 
        background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 5px !important; 
        font-size: 12px !important; 
        height: 34px !important; 
        min-height: 34px !important;
        margin-top: 2px !important; 
    }

    button[data-baseweb="tab"] { 
        font-size: 11px !important; 
        font-weight: bold !important; 
        padding: 2px 4px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def get_rounded_time(dt):
  minute = dt.minute
  if minute < 15:
    rounded_dt = dt.replace(minute=0, second=0, microsecond=0)
  elif minute < 45:
    rounded_dt = dt.replace(minute=30, second=0, microsecond=0)
  else:
    rounded_dt = (dt + timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
  return rounded_dt.strftime("%d/%m/%Y %H:%M")


time_slots = []
for hour in range(24):
  for minute in (0, 30):
    time_slots.append(f"{hour:02d}:{minute:02d}")

now_vn = get_vn_now()
current_hour = now_vn.hour
current_minute = 30 if now_vn.minute >= 30 else 0
default_time_str = f"{current_hour:02d}:{current_minute:02d}"
default_index = (
    time_slots.index(default_time_str) if default_time_str in time_slots else 0
)

if "reset_form" not in st.session_state:
  st.session_state.reset_form = False

if "show_success_msg" not in st.session_state:
  st.session_state.show_success_msg = False

if st.session_state.reset_form:
  st.session_state["input_thiet_bi"] = ""
  st.session_state["input_ten_su_co"] = ""
  st.session_state["input_nguoi_bao_cao"] = ""
  st.session_state.reset_form = False

st.markdown("<h1>🛠️ BÁO CÁO & THEO DÕI SỰ CỐ</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 KHAI BÁO MỚI", "📊 QUẢN LÝ SỰ CỐ"])

with tab1:
  if st.session_state.show_success_msg:
    st.success("🎉 GỬI BÁO CÁO THÀNH CÔNG!")
    st.balloons()
    st.session_state.show_success_msg = False

  with st.form("form_su_co", clear_on_submit=False):
    thiet_bi = st.text_input("MÁY / THIẾT BỊ *", key="input_thiet_bi")

    col1, col2 = st.columns(2)
    with col1:
      ngay_bao = st.date_input(
          "Ngày báo *", value=now_vn.date(), key="ngay_bao_input"
      )
    with col2:
      gio_bao = st.selectbox(
          "Giờ báo *", time_slots, index=default_index, key="gio_bao_input"
      )

    ten_su_co = st.text_input(
        "TÊN SỰ CỐ / BỆNH CỦA MÁY *", key="input_ten_su_co"
    )

    col3, col4 = st.columns(2)
    with col3:
      ngay_dk = st.date_input(
          "Ngày dự kiến *", value=now_vn.date(), key="ngay_dk_input"
      )
    with col4:
      gio_dk = st.selectbox(
          "Giờ dự kiến *", time_slots, index=default_index, key="gio_dk_input"
      )

    nguoi_bao_cao = st.text_input("NGƯỜI BÁO CÁO *", key="input_nguoi_bao_cao")

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      missing_fields = []
      if not thiet_bi.strip():
        missing_fields.append("MÁY")
      if not ten_su_co.strip():
        missing_fields.append("SỰ CỐ")
      if not nguoi_bao_cao.strip():
        missing_fields.append("NGƯỜI BÁO CÁO")

      if missing_fields:
        st.error(f"⚠️ Chưa nhập: {', '.join(missing_fields)}")
      else:
        thoi_gian_bao_str = f"{ngay_bao.strftime('%d/%m/%Y')} {gio_bao}"
        du_kien_xong_str = f"{ngay_dk.strftime('%d/%m/%Y')} {gio_dk}"

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            """
                    INSERT INTO su_co (thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong, nguoi_bao_cao, trang_thai, thoi_gian_xong)
                    VALUES (?, ?, ?, ?, ?, 'Đang xử lý', '')
                """,
            (
                thiet_bi.strip(),
                thoi_gian_bao_str,
                ten_su_co.strip(),
                du_kien_xong_str,
                nguoi_bao_cao.strip(),
            ),
        )
        conn.commit()
        conn.close()

        st.session_state.reset_form = True
        st.session_state.show_success_msg = True
        st.rerun()

with tab2:
  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query(
      "SELECT id, thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong,"
      " nguoi_bao_cao, trang_thai, thoi_gian_xong FROM su_co ORDER BY id DESC",
      conn,
  )
  conn.close()

  if not df.empty:
    # TỰ TẠO BẢNG HTML CHUẨN XÓA LỖI INDENT KHÔNG BỊ TRỢT CODE
    rows_html = ""
    for _, row in df.iterrows():
      rows_html += (
          f"<tr><td><b>{row['thiet_bi']}</b></td><td>{row['thoi_gian_bao']}</td><td"
          f" style='text-align:"
          f" left;'>{row['ten_su_co']}</td><td>{row['du_kien_xong']}</td></tr>"
      )

    table_html = (
        f'<div class="custom-table-container"><table'
        " class="custom-table"><thead><tr><th style="width: 15%;">MÁY</th><th"
        ' style="width: 25%;">TG BÁO</th><th style="width: 35%;">SỰ CỐ</th><th'
        ' style="width: 25%;">DỰ'
        f" KIẾN</th></tr></thead><tbody>{rows_html}</tbody></table></div>"
    )

    st.markdown(table_html, unsafe_allow_html=True)

    # SAO CHÉP SỰ CỐ
    su_co_list = [
        f"{row['thiet_bi']} - {row['ten_su_co']} [{row['trang_thai']}]"
        for _, row in df.iterrows()
    ]
    selected_option = st.selectbox("Chọn sự cố copy:", su_co_list, index=0)

    if selected_option:
      selected_idx = su_co_list.index(selected_option)
      selected_row = df.iloc[selected_idx]

      nguoi_gui = (
          selected_row["nguoi_bao_cao"]
          if (
              pd.notna(selected_row["nguoi_bao_cao"])
              and str(selected_row["nguoi_bao_cao"]).strip()
          )
          else "N/A"
      )

      single_text = (
          f"🛠️ BÁO CÁO SỰ CỐ [{selected_row['trang_thai']}]\n"
          f"MÁY: {selected_row['thiet_bi']}\n"
          f"THỜI GIAN BÁO: {selected_row['thoi_gian_bao']}\n"
          f"TÊN SỰ CỐ: {selected_row['ten_su_co']}\n"
          f"THỜI GIAN DỰ KIẾN: {selected_row['du_kien_xong']}\n"
      )
      if selected_row["trang_thai"] == "✅ Đã xong":
        single_text += f"THỜI GIAN HOÀN THÀNH THỰC TẾ: {selected_row['thoi_gian_xong']}\n"
      single_text += f"NGƯỜI BÁO CÁO: {nguoi_gui}"

      st.code(single_text, language="text")

    # XÁC NHẬN HOÀN THÀNH
    pending_df = df[df["trang_thai"] != "✅ Đã xong"]
    if not pending_df.empty:
      done_list = [
          f"{row['thiet_bi']} - {row['ten_su_co']}"
          for _, row in pending_df.iterrows()
      ]
      selected_done = st.selectbox(
          "Xác nhận xong:", done_list, key="done_select"
      )

      if st.button("✅ XÁC NHẬN HOÀN THÀNH"):
        selected_idx = done_list.index(selected_done)
        target_id = int(pending_df.iloc[selected_idx]["id"])

        actual_click_time = get_vn_now()
        actual_done_time = get_rounded_time(actual_click_time)

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "UPDATE su_co SET trang_thai='✅ Đã xong', thoi_gian_xong=? WHERE"
            " id=?",
            (actual_done_time, target_id),
        )
        conn.commit()
        conn.close()
        st.success(f"🎉 Đã xong lúc: {actual_done_time}")
        st.rerun()

    # ADMIN XÓA
    with st.expander("🔑 Admin xóa"):
      admin_pass = st.text_input("Mật khẩu Admin:", type="password")
      del_list = [
          f"{row['thiet_bi']} - {row['ten_su_co']}" for _, row in df.iterrows()
      ]
      selected_del = st.selectbox("Sự cố xóa:", del_list)

      if st.button("❌ XÓA"):
        if admin_pass == "230":
          del_idx = del_list.index(selected_del)
          del_id = int(df.iloc[del_idx]["id"])

          conn = sqlite3.connect(DB_NAME)
          c = conn.cursor()
          c.execute("DELETE FROM su_co WHERE id=?", (del_id,))
          conn.commit()
          conn.close()

          st.success("🗑️ Đã xóa!")
          st.rerun()
        else:
          st.error("🔑 Sai mật khẩu!")
  else:
    st.info("Chưa có báo cáo sự cố nào.")
