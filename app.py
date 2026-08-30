from datetime import datetime, timedelta, timezone
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Báo Cáo Sự Cố", page_icon="🛠️", layout="wide"
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

# CSS Tối ưu hiển thị vừa khít 1 màn hình (No Scroll)
st.markdown(
    """
    <style>
    /* Tổng thể ứng dụng */
    .stApp { 
        background-color: #f4fbf7; 
        color: #1b4332; 
    }
    
    /* Thu gọn khoảng cách container chính */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Thu gọn tiêu đề */
    h1 {
        font-size: 1.4rem !important;
        margin-bottom: 0.2rem !important;
        padding-bottom: 0rem !important;
    }
    h2, h3, h4 {
        font-size: 1.05rem !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Form gọn gàng */
    div[data-testid="stForm"] { 
        background-color: #ffffff; 
        border: 2px solid #52b788; 
        border-radius: 10px; 
        padding: 8px 12px !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    
    /* Input & Select thu nhỏ chiều cao */
    .stTextInput input, div[data-baseweb="select"] { 
        background-color: #f8fff9 !important; 
        border: 1px solid #74c69d !important; 
        border-radius: 6px !important; 
        color: #1b4332 !important; 
        font-size: 14px !important; 
        min-height: 36px !important;
        height: 36px !important;
    }
    
    .stDateInput input {
        height: 36px !important;
        font-size: 14px !important;
    }

    /* Thu nhỏ nhãn field */
    label {
        font-size: 13px !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }

    /* Button tối ưu gọn */
    .stButton button, button[kind="FormSubmitButton"] { 
        background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 6px !important; 
        width: 100%; 
        font-size: 14px !important; 
        height: 40px !important;
        min-height: 40px !important;
        margin-top: 4px !important;
    }

    /* Giảm lề giữa các phần tử */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.3rem !important;
    }
    
    hr {
        margin: 0.4rem 0 !important;
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

# Quản lý trạng thái reset và thông báo gửi thành công
if "reset_form" not in st.session_state:
  st.session_state.reset_form = False

if "show_success_msg" not in st.session_state:
  st.session_state.show_success_msg = False

if st.session_state.reset_form:
  st.session_state["input_thiet_bi"] = ""
  st.session_state["input_ten_su_co"] = ""
  st.session_state["input_nguoi_bao_cao"] = ""
  st.session_state.reset_form = False

st.markdown("### 🛠️ KHAI BÁO & THEO DÕI SỰ CỐ KỸ THUẬT")

# Chia 2 cột màn hình chính: Bên trái Khai Báo (40%), Bên phải Quản Lý & Copy (60%)
col_left, col_right = st.columns([4, 6], gap="small")

with col_left:
  st.markdown("##### 📝 KHAI BÁO MỚI")

  if st.session_state.show_success_msg:
    st.success("🎉 ĐÃ GỬI BÁO CÁO THÀNH CÔNG!")
    st.balloons()
    st.session_state.show_success_msg = False

  with st.form("form_su_co", clear_on_submit=False):
    thiet_bi = st.text_input("MÁY / THIẾT BỊ *", key="input_thiet_bi")

    c1, c2 = st.columns(2)
    with c1:
      ngay_bao = st.date_input(
          "Ngày báo *", value=now_vn.date(), key="ngay_bao_input"
      )
    with c2:
      gio_bao = st.selectbox(
          "Giờ báo *", time_slots, index=default_index, key="gio_bao_input"
      )

    ten_su_co = st.text_input(
        "TÊN SỰ CỐ / BỆNH CỦA MÁY *", key="input_ten_su_co"
    )

    c3, c4 = st.columns(2)
    with c3:
      ngay_dk = st.date_input(
          "Ngày dự kiến *", value=now_vn.date(), key="ngay_dk_input"
      )
    with c4:
      gio_dk = st.selectbox(
          "Giờ dự kiến *", time_slots, index=default_index, key="gio_dk_input"
      )

    nguoi_bao_cao = st.text_input("NGƯỜI BÁO CÁO *", key="input_nguoi_bao_cao")

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      missing_fields = []
      if not thiet_bi.strip():
        missing_fields.append("MÁY / THIẾT BỊ")
      if not ten_su_co.strip():
        missing_fields.append("TÊN SỰ CỐ")
      if not nguoi_bao_cao.strip():
        missing_fields.append("NGƯỜI BÁO CÁO")

      if missing_fields:
        st.error(f"⚠️ Thiếu: **{', '.join(missing_fields)}**")
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

with col_right:
  st.markdown("##### 📊 DANH SÁCH & SAO CHÉP BÁO CÁO")

  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query(
      "SELECT id, thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong,"
      " nguoi_bao_cao, trang_thai, thoi_gian_xong FROM su_co ORDER BY id DESC",
      conn,
  )
  conn.close()

  if not df.empty:
    tab_list, tab_done, tab_copy = st.tabs(
        ["📋 Danh Sách", "✅ Cập Nhật Xong", "📋 Copy Báo Cáo"]
    )

    with tab_list:
      df_display = df.drop(columns=["id"]).rename(
          columns={
              "thiet_bi": "MÁY",
              "thoi_gian_bao": "THỜI GIAN BÁO",
              "ten_su_co": "TÊN SỰ CỐ",
              "du_kien_xong": "DỰ KIẾN",
              "nguoi_bao_cao": "NGƯỜI BÁO",
              "trang_thai": "TRẠNG THÁI",
              "thoi_gian_xong": "HOÀN THÀNH",
          }
      )
      st.dataframe(df_display, height=260, use_container_width=True)

    with tab_done:
      pending_df = df[df["trang_thai"] != "✅ Đã xong"]
      if not pending_df.empty:
        done_list = [
            f"Máy: {row['thiet_bi']} - {row['ten_su_co']} ({row['thoi_gian_bao']})"
            for _, row in pending_df.iterrows()
        ]
        selected_done = st.selectbox(
            "Chọn sự cố đã sửa xong:", done_list, key="done_select"
        )
        if st.button("✅ XÁC NHẬN HOÀN THÀNH SỬA CHỮA"):
          selected_idx = done_list.index(selected_done)
          target_id = int(pending_df.iloc[selected_idx]["id"])
          actual_done_time = get_rounded_time(get_vn_now())

          conn = sqlite3.connect(DB_NAME)
          c = conn.cursor()
          c.execute(
              "UPDATE su_co SET trang_thai='✅ Đã xong', thoi_gian_xong=? WHERE"
              " id=?",
              (actual_done_time, target_id),
          )
          conn.commit()
          conn.close()
          st.success(f"🎉 Đã xong! Thời gian: {actual_done_time}")
          st.rerun()
      else:
        st.info("Tất cả sự cố đã được hoàn thành!")

    with tab_copy:
      copy_mode = st.radio(
          "Chọn kiểu copy:",
          ["Copy 1 Sự Cố", "Copy Tất Cả Sự Cố"],
          horizontal=True,
      )

      if copy_mode == "Copy 1 Sự Cố":
        su_co_list = [
            f"Máy: {row['thiet_bi']} - {row['ten_su_co']} [{row['trang_thai']}]"
            for _, row in df.iterrows()
        ]
        selected_option = st.selectbox(
            "Chọn sự cố:", su_co_list, index=0, label_visibility="collapsed"
        )
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

          # ĐỊNH DẠNG XUỐNG DÒNG RÕ RÀNG CHO TỪNG TIÊU ĐỀ
          single_text = (
              f"🛠️ BÁO CÁO SỰ CỐ [{selected_row['trang_thai']}]\n"
              f"• MÁY / THIẾT BỊ:\n"
              f"  {selected_row['thiet_bi']}\n"
              f"• THỜI GIAN BÁO:\n"
              f"  {selected_row['thoi_gian_bao']}\n"
              f"• TÊN SỰ CỐ / BỆNH MÁY:\n"
              f"  {selected_row['ten_su_co']}\n"
              f"• DỰ KIẾN HOÀN THÀNH:\n"
              f"  {selected_row['du_kien_xong']}\n"
          )
          if selected_row["trang_thai"] == "✅ Đã xong":
            single_text += (
                f"• HOÀN THÀNH THỰC TẾ:\n  {selected_row['thoi_gian_xong']}\n"
            )
          single_text += f"• NGƯỜI BÁO CÁO:\n  {nguoi_gui}"

          st.code(single_text, language="text")

      else:
        # ĐỊNH DẠNG XUỐNG DÒNG DÀNH CHO TẤT CẢ SỰ CỐ
        all_text = (
            "📋 DANH SÁCH BÁO CÁO SỰ CỐ\n===================================\n\n"
        )
        for idx, row in df.iterrows():
          nguoi_gui = (
              row["nguoi_bao_cao"]
              if (
                  pd.notna(row["nguoi_bao_cao"])
                  and str(row["nguoi_bao_cao"]).strip()
              )
              else "N/A"
          )
          all_text += (
              f"🔹 MÁY / THIẾT BỊ:\n"
              f"  {row['thiet_bi']} [{row['trang_thai']}]\n"
              f"• THỜI GIAN BÁO:\n"
              f"  {row['thoi_gian_bao']}\n"
              f"• TÊN SỰ CỐ:\n"
              f"  {row['ten_su_co']}\n"
              f"• DỰ KIẾN HOÀN THÀNH:\n"
              f"  {row['du_kien_xong']}\n"
          )
          if row["trang_thai"] == "✅ Đã xong":
            all_text += (
                f"• HOÀN THÀNH THỰC TẾ:\n  {row['thoi_gian_xong']}\n"
            )
          all_text += f"• NGƯỜI BÁO CÁO:\n  {nguoi_gui}\n\n-----------------------------------\n\n"

        st.code(all_text, language="text")

  else:
    st.info("Chưa có báo cáo sự cố nào.")
