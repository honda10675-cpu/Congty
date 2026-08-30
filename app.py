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

# Giao diện Xanh lá cây - Trắng tối ưu không gian gọn gàng
st.markdown(
    """
    <style>
    .stApp { background-color: #f4fbf7; color: #1b4332; }
    div[data-testid="stForm"] { background-color: #ffffff; border: 2px solid #52b788; border-radius: 12px; padding: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stTextInput input, div[data-baseweb="select"] { background-color: #f8fff9 !important; border: 1px solid #74c69d !important; border-radius: 8px !important; color: #1b4332 !important; font-size: 15px !important; }
    .stButton button, button[kind="FormSubmitButton"] { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; width: 100%; font-size: 15px !important; min-height: 42px !important; }
    h1, h2, h3, h4 { color: #1b4332 !important; margin-bottom: 0.5rem !important; }
    
    /* Thu gọn khoảng cách padding trên màn hình */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
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

# Quản lý Session State
if "reset_form" not in st.session_state:
  st.session_state.reset_form = False

if "show_success_msg" not in st.session_state:
  st.session_state.show_success_msg = False

if st.session_state.reset_form:
  st.session_state["input_thiet_bi"] = ""
  st.session_state["input_ten_su_co"] = ""
  st.session_state["input_nguoi_bao_cao"] = ""
  st.session_state.reset_form = False

st.title("🛠️ HỆ THỐNG BÁO CÁO & THEO DÕI SỰ CỐ")

# CHIA MÀN HÌNH THÀNH 2 CỘT TỶ LỆ SONG SONG (5:7)
col_left, col_right = st.columns([5, 7])

# --- CỘT TRÁI: NHẬP KHAI BÁO SỰ CỐ ---
with col_left:
  st.subheader("📝 KHAI BÁO SỰ CỐ MỚI")

  if st.session_state.show_success_msg:
    st.success("🎉 GỬI BÁO CÁO THÀNH CÔNG!")
    st.balloons()
    st.session_state.show_success_msg = False

  with st.form("form_su_co", clear_on_submit=False):
    thiet_bi = st.text_input("**MÁY / THIẾT BỊ ***", key="input_thiet_bi")

    st.write("**THỜI GIAN BÁO ***")
    c1, c2 = st.columns(2)
    with c1:
      ngay_bao = st.date_input(
          "Ngày báo", value=now_vn.date(), key="ngay_bao_input"
      )
    with c2:
      gio_bao = st.selectbox(
          "Giờ báo", time_slots, index=default_index, key="gio_bao_input"
      )

    ten_su_co = st.text_input(
        "**TÊN SỰ CỐ / BỆNH MÁY ***", key="input_ten_su_co"
    )

    st.write("**THỜI GIAN DỰ KIẾN HOÀN THÀNH ***")
    c3, c4 = st.columns(2)
    with c3:
      ngay_dk = st.date_input(
          "Ngày dự kiến", value=now_vn.date(), key="ngay_dk_input"
      )
    with c4:
      gio_dk = st.selectbox(
          "Giờ dự kiến", time_slots, index=default_index, key="gio_dk_input"
      )

    nguoi_bao_cao = st.text_input(
        "**NGƯỜI BÁO CÁO ***", key="input_nguoi_bao_cao"
    )

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
        st.error(
            f"⚠️ Vui lòng nhập đầy đủ: **{', '.join(missing_fields)}**"
        )
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

# --- CỘT PHẢI: QUẢN LÝ, CẬP NHẬT VÀ SAO CHÉP ---
with col_right:
  st.subheader("📊 DANH SÁCH & SAO CHÉP BÁO CÁO")

  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query(
      "SELECT id, thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong,"
      " nguoi_bao_cao, trang_thai, thoi_gian_xong FROM su_co ORDER BY id DESC",
      conn,
  )
  conn.close()

  if not df.empty:
    # Hiển thị bảng thu nhỏ vừa khung hình
    df_display = df.drop(columns=["id"]).rename(
        columns={
            "thiet_bi": "MÁY",
            "thoi_gian_bao": "THỜI GIAN BÁO",
            "ten_su_co": "TÊN SỰ CỐ",
            "du_kien_xong": "THỜI GIAN DỰ KIẾN",
            "nguoi_bao_cao": "NGƯỜI BÁO CÁO",
            "trang_thai": "TRẠNG THÁI",
            "thoi_gian_xong": "THỜI GIAN THỰC TẾ",
        }
    )
    st.dataframe(df_display, use_container_width=True, height=220)

    # NÚT XÁC NHẬN HOÀN THÀNH
    pending_df = df[df["trang_thai"] != "✅ Đã xong"]
    if not pending_df.empty:
      col_d1, col_d2 = st.columns([2, 1])
      with col_d1:
        done_list = [
            f"Máy: {row['thiet_bi']} - {row['ten_su_co']}"
            for _, row in pending_df.iterrows()
        ]
        selected_done = st.selectbox(
            "Chọn sự cố đã sửa xong:",
            done_list,
            key="done_select",
            label_visibility="collapsed",
        )
      with col_d2:
        if st.button("✅ BẤM HOÀN THÀNH"):
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
          st.success(f"🎉 Đã xong lúc {actual_done_time}")
          st.rerun()

    # VÙNG SAO CHÉP ĐỊNH DẠNG XUỐNG DÒNG MỖI TIÊU ĐỀ
    tab_copy1, tab_copy2, tab_admin = st.tabs(
        ["📋 Copy Riêng Từng Sự Cố", "📑 Copy Tất Cả", "🔒 Quyền Admin"]
    )

    with tab_copy1:
      su_co_list = [
          f"Máy: {row['thiet_bi']} - {row['ten_su_co']} [{row['trang_thai']}]"
          for _, row in df.iterrows()
      ]
      selected_option = st.selectbox(
          "Chọn sự cố cần copy:",
          su_co_list,
          index=0,
          label_visibility="collapsed",
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

        # ĐỊNH DẠNG XUỐNG DÒNG RÕ RÀNG MỖI TIÊU ĐỀ
        single_text = (
            f"🛠️ BÁO CÁO SỰ CỐ [{selected_row['trang_thai']}]\n"
            f"MÁY: {selected_row['thiet_bi']}\n"
            f"THỜI GIAN BÁO: {selected_row['thoi_gian_bao']}\n"
            f"TÊN SỰ CỐ: {selected_row['ten_su_co']}\n"
            f"THỜI GIAN DỰ KIẾN: {selected_row['du_kien_xong']}\n"
        )
        if selected_row["trang_thai"] == "✅ Đã xong":
          single_text += (
              f"THỜI GIAN HOÀN THÀNH THỰC TẾ: {selected_row['thoi_gian_xong']}\n"
          )
        single_text += f"NGƯỜI BÁO CÁO: {nguoi_gui}"

        st.code(single_text, language="text")

    with tab_copy2:
      all_text = (
          "📋 DANH SÁCH BÁO CÁO SỰ CỐ:\n-----------------------------------\n"
      )
      for _, row in df.iterrows():
        nguoi_gui = (
            row["nguoi_bao_cao"]
            if (
                pd.notna(row["nguoi_bao_cao"])
                and str(row["nguoi_bao_cao"]).strip()
            )
            else "N/A"
        )
        all_text += (
            f"🔹 MÁY: {row['thiet_bi']} [{row['trang_thai']}]\n"
            f"THỜI GIAN BÁO: {row['thoi_gian_bao']}\n"
            f"TÊN SỰ CỐ: {row['ten_su_co']}\n"
            f"THỜI GIAN DỰ KIẾN: {row['du_kien_xong']}\n"
        )
        if row["trang_thai"] == "✅ Đã xong":
          all_text += (
              f"THỜI GIAN HOÀN THÀNH THỰC TẾ: {row['thoi_gian_xong']}\n"
          )
        all_text += f"NGƯỜI BÁO CÁO: {nguoi_gui}\n\n"

      st.code(all_text, language="text")

    with tab_admin:
      col_a1, col_a2 = st.columns([2, 1])
      with col_a1:
        admin_pass = st.text_input(
            "Mật khẩu Admin:", type="password", placeholder="Nhập mật khẩu..."
        )
        del_list = [
            f"Máy: {row['thiet_bi']} - {row['ten_su_co']}"
            for _, row in df.iterrows()
        ]
        selected_del = st.selectbox("Chọn sự cố xóa:", del_list)
      with col_a2:
        st.write(" ")
        st.write(" ")
        if st.button("❌ XÓA SỰ CỐ"):
          if admin_pass == "230":
            del_idx = del_list.index(selected_del)
            del_id = int(df.iloc[del_idx]["id"])

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM su_co WHERE id=?", (del_id,))
            conn.commit()
            conn.close()

            st.success("🗑️ Đã xóa thành công!")
            st.rerun()
          else:
            st.error("🔑 Sai mật khẩu!")

  else:
    st.info("Chưa có báo cáo sự cố nào trong hệ thống.")
