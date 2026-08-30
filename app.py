from datetime import datetime, time
import sqlite3
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
            ten_su_co TEXT NOT NULL,
            thiet_bi TEXT NOT NULL,
            nguoi_bao_cao TEXT,
            khung_gio TEXT,
            ngay_tao TEXT,
            mo_ta TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

# Danh sách khung giờ từ 00:00 đến 23:30 (mỗi nấc 30 phút)
time_slots = []
for hour in range(24):
  for minute in (0, 30):
    time_slots.append(f"{hour:02d}:{minute:02d}")

st.title("🛠️ Báo Cáo & Theo Dõi Sự Cố")

tab1, tab2 = st.tabs(["📝 Khai Báo Mới", "📊 Danh Sách Quản Lý"])

with tab1:
  st.subheader("Khai báo sự cố kỹ thuật")
  with st.form("form_su_co", clear_on_submit=True):
    ten_su_co = st.text_input("Tên sự cố / Bệnh của máy *")
    thiet_bi = st.text_input("Tên thiết bị / Máy móc *")
    nguoi_bao_cao = st.text_input("Người báo cáo")

    khung_gio = st.selectbox("Chọn khung giờ phát sinh (30 phút)", time_slots)
    mo_ta = st.text_area("Mô tả chi tiết sự cố")

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      if not ten_su_co or not thiet_bi:
        st.error("⚠️ Vui lòng điền Tên sự cố và Thiết bị!")
      else:
        ngay_tao = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("su_co_web.db")
        c = conn.cursor()
        c.execute(
            """
                    INSERT INTO su_co (ten_su_co, thiet_bi, nguoi_bao_cao, khung_gio, ngay_tao, mo_ta)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
            (ten_su_co, thiet_bi, nguoi_bao_cao, khung_gio, ngay_tao, mo_ta),
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
    # 1. Bảng dữ liệu tổng quan
    st.dataframe(df, use_container_width=True)

    st.divider()

    # 2. Tạo đoạn văn bản Copy TOÀN BỘ sự cố
    st.subheader("📋 Sao chép toàn bộ sự cố")
    all_text = "📋 DẠNH SÁCH BÁO CÁO SỰ CỐ:\n"
    all_text += "-----------------------------------\n"
    for idx, row in df.iterrows():
      all_text += (
          f"🔹 [ID {row['id']}] {row['ten_su_co']} - Máy: {row['thiet_bi']}\n"
      )
      all_text += f"   • Khung giờ: {row['khung_gio']} | Người báo:"
      f" {row['nguoi_bao_cao'] if row['nguoi_bao_cao'] else 'N/A'}\n"
      if row["mo_ta"]:
        all_text += f"   • Chi tiết: {row['mo_ta']}\n"
      all_text += "\n"

    st.code(all_text, language="text")

    st.divider()

    # 3. Copy TỪNG sự cố riêng
    st.subheader("🔍 Sao chép riêng từng sự cố")
    su_co_list = [
        f"ID {row['id']} - {row['ten_su_co']} ({row['thiet_bi']})"
        for _, row in df.iterrows()
    ]
    selected_option = st.selectbox("Chọn sự cố cần lấy thông tin:", su_co_list)

    if selected_option:
      selected_id = int(selected_option.split(" - ")[0].replace("ID ", ""))
      selected_row = df[df["id"] == selected_id].iloc[0]

      single_text = (
          f"🛠️ BÁO CÁO SỰ CỐ [ID {selected_row['id']}]\n"
          f"• Tên sự cố: {selected_row['ten_su_co']}\n"
          f"• Thiết bị: {selected_row['thiet_bi']}\n"
          f"• Khung giờ: {selected_row['khung_gio']}\n"
          f"• Người báo cáo: {selected_row['nguoi_bao_cao'] if selected_row['nguoi_bao_cao'] else 'N/A'}\n"
          f"• Ngày tạo: {selected_row['ngay_tao']}\n"
          f"• Mô tả: {selected_row['mo_ta'] if selected_row['mo_ta'] else 'Không có'}"
      )

      st.code(single_text, language="text")

  else:
    st.info("Chưa có báo cáo sự cố nào.")
