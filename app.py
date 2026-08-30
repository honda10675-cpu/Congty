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

# Giao diện Xanh lá cây - Trắng tối ưu cho Mobile
st.markdown(
    """
    <style>
    .stApp { background-color: #f4fbf7; color: #1b4332; }
    div[data-testid="stForm"] { background-color: #ffffff; border: 2px solid #52b788; border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stTextInput input, div[data-baseweb="select"] { background-color: #f8fff9 !important; border: 1px solid #74c69d !important; border-radius: 8px !important; color: #1b4332 !important; font-size: 16px !important; }
    .stButton button, button[kind="FormSubmitButton"] { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; width: 100%; font-size: 16px !important; min-height: 48px !important; }
    h1, h2, h3 { color: #1b4332 !important; }
    
    /* Responsive cho điện thoại */
    @media (max-width: 640px) {
        div[data-testid="stForm"] { padding: 10px; }
        .stButton button { font-size: 15px !important; }
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


# Tạo danh sách 48 khung giờ (mỗi nấc 30 phút)
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

st.title("🛠️ BÁO CÁO & THEO DÕI SỰ CỐ")

tab1, tab2 = st.tabs(["📝 KHAI BÁO MỚI", "📊 DANH SÁCH QUẢN LÝ"])

with tab1:
  st.subheader("KHAI BÁO SỰ CỐ KỸ THUẬT")
  with st.form("form_su_co", clear_on_submit=True):
    thiet_bi = st.text_input("**MÁY / THIẾT BỊ ***")

    st.write("**THỜI GIAN BÁO ***")
    col1, col2 = st.columns(2)
    with col1:
      ngay_bao = st.date_input(
          "Ngày báo *", value=now_vn.date(), key="ngay_bao_input"
      )
    with col2:
      gio_bao = st.selectbox(
          "Giờ báo *", time_slots, index=default_index, key="gio_bao_input"
      )

    ten_su_co = st.text_input("**TÊN SỰ CỐ / BỆNH CỦA MÁY ***")

    st.write("**THỜI GIAN DỰ KIẾN HOÀN THÀNH ***")
    col3, col4 = st.columns(2)
    with col3:
      ngay_dk = st.date_input(
          "Ngày dự kiến *", value=now_vn.date(), key="ngay_dk_input"
      )
    with col4:
      gio_dk = st.selectbox(
          "Giờ dự kiến *", time_slots, index=default_index, key="gio_dk_input"
      )

    nguoi_bao_cao = st.text_input("**NGƯỜI BÁO CÁO ***")

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      # Kiểm tra ràng buộc bắt buộc nhập tất cả các ô
      if (
          not thiet_bi.strip()
          or not ten_su_co.strip()
          or not nguoi_bao_cao.strip()
      ):
        st.error(
            "⚠️ Vui lòng nhập ĐẦY ĐỦ TẤT CẢ CÁC MỤC (Máy, Sự cố, Người báo"
            " cáo)!"
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
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("DANH SÁCH SỰ CỐ & SAO CHÉP")
  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query(
      "SELECT id, thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong,"
      " nguoi_bao_cao, trang_thai, thoi_gian_xong FROM su_co ORDER BY id DESC",
      conn,
  )
  conn.close()

  if not df.empty:
    df_display = df.drop(columns=["id"]).rename(
        columns={
            "thiet_bi": "MÁY",
            "thoi_gian_bao": "THỜI GIAN BÁO",
            "ten_su_co": "TÊN SỰ CỐ",
            "du_kien_xong": "THỜI GIAN DỰ KIẾN",
            "nguoi_bao_cao": "NGƯỜI BÁO CÁO",
            "trang_thai": "TRẠNG THÁI",
            "thoi_gian_xong": "THỜI GIAN HOÀN THÀNH THỰC TẾ",
        }
    )
    st.dataframe(df_display, use_container_width=True)

    st.divider()

    # CẬP NHẬT HOÀN THÀNH SỬA CHỮA
    st.subheader("✅ CẬP NHẬT HOÀN THÀNH SỬA CHỮA")
    pending_df = df[df["trang_thai"] != "✅ Đã xong"]

    if not pending_df.empty:
      col_done1, col_done2 = st.columns([3, 1])
      with col_done1:
        done_list = [
            f"Máy: {row['thiet_bi']} - {row['ten_su_co']} (Báo lúc:"
            f" {row['thoi_gian_bao']})"
            for _, row in pending_df.iterrows()
        ]
        selected_done = st.selectbox(
            "Chọn sự cố đã sửa xong:", done_list, key="done_select"
        )
      with col_done2:
        st.write(" ")
        st.write(" ")
        if st.button("✅ HOÀN THÀNH SỬA CHỮA"):
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
          st.success(
              f"🎉 Đã xác nhận hoàn thành! Thời gian ghi nhận:"
              f" {actual_done_time}"
          )
          st.rerun()
    else:
      st.info("Tất cả sự cố hiện tại đã được hoàn thành!")

    st.divider()

    # SAO CHÉP TOÀN BỘ
    st.subheader("📋 SAO CHÉP TOÀN BỘ SỰ CỐ")
    all_text = "📋 DANH SÁCH BÁO CÁO SỰ CỐ:\n-----------------------------------\n"
    for _, row in df.iterrows():
      nguoi_gui = (
          row["nguoi_bao_cao"]
          if (pd.notna(row["nguoi_bao_cao"]) and str(row["nguoi_bao_cao"]).strip())
          else "N/A"
      )
      status_str = row["trang_thai"]
      all_text += (
          f"🔹 MÁY: {row['thiet_bi']} [{status_str}]\n"
          f"   • Thời gian báo: {row['thoi_gian_bao']}\n"
          f"   • Sự cố: {row['ten_su_co']}\n"
          f"   • Dự kiến hoàn thành: {row['du_kien_xong']}\n"
      )
      if row["trang_thai"] == "✅ Đã xong":
        all_text += (
            f"   • Thời gian hoàn thành thực tế: {row['thoi_gian_xong']}\n"
        )
      all_text += f"   • Người báo cáo: {nguoi_gui}\n\n"

    st.code(all_text, language="text")
    st.divider()

    # SAO CHÉP RIÊNG TỪNG SỰ CỐ
    st.subheader("🔍 SAO CHÉP RIÊNG TỪNG SỰ CỐ")
    su_co_list = [
        f"Máy: {row['thiet_bi']} - {row['ten_su_co']} [{row['trang_thai']}]"
        for _, row in df.iterrows()
    ]
    selected_option = st.selectbox(
        "Chọn sự cố cần sao chép:", su_co_list, index=0
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

      single_text = (
          f"🛠️ BÁO CÁO SỰ CỐ [{selected_row['trang_thai']}]\n"
          f"• MÁY: {selected_row['thiet_bi']}\n"
          f"• THỜI GIAN BÁO: {selected_row['thoi_gian_bao']}\n"
          f"• TÊN SỰ CỐ: {selected_row['ten_su_co']}\n"
          f"• DỰ KIẾN HOÀN THÀNH: {selected_row['du_kien_xong']}\n"
      )
      if selected_row["trang_thai"] == "✅ Đã xong":
        single_text += f"• HOÀN THÀNH THỰC TẾ: {selected_row['thoi_gian_xong']}\n"
      single_text += f"• NGƯỜI BÁO CÁO: {nguoi_gui}"

      st.code(single_text, language="text")

    st.divider()

    # QUẢN LÝ XÓA SỰ CỐ (DÀNH CHO ADMIN)
    st.subheader("🔒 XÓA SỰ CỐ (DÀNH CHO ADMIN)")
    with st.expander("Mở vùng quản trị Admin để xóa sự cố"):
      admin_pass = st.text_input("Mật khẩu Admin:", type="password")
      del_list = [
          f"Máy: {row['thiet_bi']} - {row['ten_su_co']} ({row['thoi_gian_bao']})"
          for _, row in df.iterrows()
      ]
      selected_del = st.selectbox("Chọn sự cố cần xóa:", del_list)

      if st.button("❌ XÓA SỰ CỐ NÀY"):
        if admin_pass == "230":
          del_idx = del_list.index(selected_del)
          del_id = int(df.iloc[del_idx]["id"])

          conn = sqlite3.connect(DB_NAME)
          c = conn.cursor()
          c.execute("DELETE FROM su_co WHERE id=?", (del_id,))
          conn.commit()
          conn.close()

          st.success("🗑️ Đã xóa thành công sự cố khỏi hệ thống!")
          st.rerun()
        else:
          st.error("🔑 Sai mật khẩu Admin! Vui lòng thử lại.")

  else:
    st.info("Chưa có báo cáo sự cố nào.")
