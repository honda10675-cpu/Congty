import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Báo Cáo Sự Cố", page_icon="🛠️", layout="wide"
)


def init_db():
  conn = sqlite3.connect("su_co_web.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS su_co (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_su_co TEXT,
            thiet_bi TEXT,
            nguoi_bao_cao TEXT,
            khung_gio TEXT,
            ngay_tao TEXT
        )
    """)
  # Tự động cập nhật cột nếu cơ sở dữ liệu cũ chưa có
  c.execute("PRAGMA table_info(su_co)")
  columns = [col[1] for col in c.fetchall()]
  if "khung_gio" not in columns:
    c.execute("ALTER TABLE su_co ADD COLUMN khung_gio TEXT")
  conn.commit()
  conn.close()


init_db()

# Danh sách 48 khung giờ (mỗi nấc 30 phút)
time_slots = []
for hour in range(24):
  for minute in (0, 30):
    time_slots.append(f"{hour:02d}:{minute:02d}")

# Tính toán khung giờ hiện tại làm mặc định
now = datetime.now()
current_hour = now.hour
current_minute = 30 if now.minute >= 30 else 0
default_time_str = f"{current_hour:02d}:{current_minute:02d}"
default_index = (
    time_slots.index(default_time_str) if default_time_str in time_slots else 0
)

st.title("🛠️ Báo Cáo & Theo Dõi Sự Cố")

tab1, tab2 = st.tabs(["📝 Khai Báo Mới", "📊 Danh Sách Quản Lý"])

with tab1:
  st.subheader("Khai báo sự cố kỹ thuật")
  with st.form("form_su_co", clear_on_submit=True):
    ten_su_co = st.text_input("Tên sự cố / Bệnh của máy *")
    thiet_bi = st.text_input("Tên thiết bị / Máy móc *")
    nguoi_bao_cao = st.text_input("Người báo cáo")

    col1, col2 = st.columns(2)
    with col1:
      # Tự động hiển thị ngày thực tế hiện tại
      ngay_phat_sinh = st.date_input("Ngày phát sinh", value=now.date())
    with col2:
      # Tự động chọn khung giờ gần nhất
      khung_gio_selected = st.selectbox(
          "Khung giờ phát sinh (30 phút)",
          time_slots,
          index=default_index,
      )

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      if not ten_su_co or not thiet_bi:
        st.error("⚠️ Vui lòng điền Tên sự cố và Thiết bị!")
      else:
        ngay_tao_str = now.strftime("%Y-%m-%d %H:%M")
        khung_gio_full = (
            f"{ngay_phat_sinh.strftime('%d/%m/%Y')} {khung_gio_selected}"
        )

        conn = sqlite3.connect("su_co_web.db")
        c = conn.cursor()
        c.execute(
            """
                    INSERT INTO su_co (ten_su_co, thiet_bi, nguoi_bao_cao, khung_gio, ngay_tao)
                    VALUES (?, ?, ?, ?, ?)
                """,
            (
                ten_su_co,
                thiet_bi,
                nguoi_bao_cao,
                khung_gio_full,
                ngay_tao_str,
            ),
        )
        conn.commit()
        conn.close()
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("Danh sách quản lý & Sao chép sự cố")
  conn = sqlite3.connect("su_co_web.db")
  df = pd.read_sql_query("SELECT * FROM su_co ORDER BY id DESC", conn)
  conn.close()

  if not df.empty:
    st.dataframe(df, use_container_width=True)
    st.divider()

    # Sao chép TOÀN BỘ
    st.subheader("📋 Sao chép toàn bộ sự cố")
    all_text = "📋 DANH SÁCH BÁO CÁO SỰ CỐ:\n-----------------------------------\n"
    for _, row in df.iterrows():
      nguoi_gui = (
          row["nguoi_bao_cao"]
          if ("nguoi_bao_cao" in row and pd.notna(row["nguoi_bao_cao"]))
          else "N/A"
      )
      gio_lay = (
          row["khung_gio"]
          if ("khung_gio" in row and pd.notna(row["khung_gio"]))
          else row.get("ngay_tao", "")
      )
      all_text += (
          f"🔹 [ID {row['id']}] {row['ten_su_co']} - Máy: {row['thiet_bi']}\n"
      )
      all_text += f"   • Thời gian: {gio_lay} | Người báo: {nguoi_gui}\n\n"

    st.code(all_text, language="text")
    st.divider()

    # Sao chép RIÊNG
    st.subheader("🔍 Sao chép riêng từng sự cố")
    su_co_list = [
        f"ID {row['id']} - {row['ten_su_co']} ({row['thiet_bi']})"
        for _, row in df.iterrows()
    ]
    selected_option = st.selectbox("Chọn sự cố cần lấy thông tin:", su_co_list)

    if selected_option:
      selected_id = int(selected_option.split(" - ")[0].replace("ID ", ""))
      selected_row = df[df["id"] == selected_id].iloc[0]

      nguoi_gui = (
          selected_row["nguoi_bao_cao"]
          if (
              "nguoi_bao_cao" in selected_row
              and pd.notna(selected_row["nguoi_bao_cao"])
          )
          else "N/A"
      )
      gio_lay = (
          selected_row["khung_gio"]
          if (
              "khung_gio" in selected_row
              and pd.notna(selected_row["khung_gio"])
          )
          else selected_row.get("ngay_tao", "")
      )

      single_text = (
          f"🛠️ BÁO CÁO SỰ CỐ [ID {selected_row['id']}]\n"
          f"• Tên sự cố: {selected_row['ten_su_co']}\n"
          f"• Thiết bị: {selected_row['thiet_bi']}\n"
          f"• Thời gian phát sinh: {gio_lay}\n"
          f"• Người báo cáo: {nguoi_gui}"
      )

      st.code(single_text, language="text")

  else:
    st.info("Chưa có báo cáo sự cố nào.")
