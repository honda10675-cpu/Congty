import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Báo Cáo Sự Cố", page_icon="🛠️", layout="wide"
)

# Đổi sang DB mới để hoàn toàn sạch dữ liệu cũ
DB_NAME = "su_co_v3.db"


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
            nguoi_bao_cao TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

# Giao diện Xanh lá cây - Trắng
st.markdown(
    """
    <style>
    .stApp { background-color: #f4fbf7; color: #1b4332; }
    div[data-testid="stForm"] { background-color: #ffffff; border: 2px solid #52b788; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stTextInput input, div[data-baseweb="select"] { background-color: #f8fff9 !important; border: 1px solid #74c69d !important; border-radius: 8px !important; color: #1b4332 !important; }
    .stButton button, button[kind="FormSubmitButton"] { background: linear-gradient(90deg, #2d6a4f 0%, #40916c 100%) !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; width: 100%; font-size: 16px !important; }
    h1, h2, h3 { color: #1b4332 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# Tạo danh sách 48 khung giờ (mỗi nấc 30 phút)
time_slots = []
for hour in range(24):
  for minute in (0, 30):
    time_slots.append(f"{hour:02d}:{minute:02d}")

# Lấy thời gian thực tế hiện tại
now = datetime.now()
current_hour = now.hour
current_minute = 30 if now.minute >= 30 else 0
default_time_str = f"{current_hour:02d}:{current_minute:02d}"
default_index = (
    time_slots.index(default_time_str) if default_time_str in time_slots else 0
)

st.title("🛠️ BÁO CÁO & THEO DÕI SỰ CỐ")

tab1, tab2 = st.tabs(["📝 KHAI BÁO MỚI", "📊 DANH SÁCH QUẢN LÝ"])

with tab1:
  st.subheader("KHAI BÁO SỰ CỐ KỸ THUẬT")
  with st.form("form_su_co", clear_on_submit=True):

    # 1. MÁY / THIẾT BỊ
    thiet_bi = st.text_input("**MÁY / THIẾT BỊ ***")

    # 2. THỜI GIAN BÁO
    st.write("**THỜI GIAN BÁO ***")
    col1, col2 = st.columns(2)
    with col1:
      ngay_bao = st.date_input(
          "Ngày báo", value=now.date(), key="ngay_bao_input"
      )
    with col2:
      gio_bao = st.selectbox(
          "Giờ báo", time_slots, index=default_index, key="gio_bao_input"
      )

    # 3. TÊN SỰ CỐ / BỆNH CỦA MÁY
    ten_su_co = st.text_input("**TÊN SỰ CỐ / BỆNH CỦA MÁY ***")

    # 4. THỜI GIAN DỰ KIẾN HOÀN THÀNH
    st.write("**THỜI GIAN DỰ KIẾN HOÀN THÀNH**")
    col3, col4 = st.columns(2)
    with col3:
      ngay_dk = st.date_input(
          "Ngày dự kiến", value=now.date(), key="ngay_dk_input"
      )
    with col4:
      gio_dk = st.selectbox(
          "Giờ dự kiến", time_slots, index=default_index, key="gio_dk_input"
      )

    # 5. NGƯỜI BÁO CÁO
    nguoi_bao_cao = st.text_input("**NGƯỜI BÁO CÁO**")

    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ")

    if submit:
      if not thiet_bi.strip() or not ten_su_co.strip():
        st.error("⚠️ Vui lòng nhập đầy đủ thông tin MÁY và TÊN SỰ CỐ!")
      else:
        thoi_gian_bao_str = f"{ngay_bao.strftime('%d/%m/%Y')} {gio_bao}"
        du_kien_xong_str = f"{ngay_dk.strftime('%d/%m/%Y')} {gio_dk}"

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            """
                    INSERT INTO su_co (thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong, nguoi_bao_cao)
                    VALUES (?, ?, ?, ?, ?)
                """,
            (
                thiet_bi,
                thoi_gian_bao_str,
                ten_su_co,
                du_kien_xong_str,
                nguoi_bao_cao,
            ),
        )
        conn.commit()
        conn.close()
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("DANH SÁCH SỰ CỐ & SAO CHÉP")
  conn = sqlite3.connect(DB_NAME)
  df = pd.read_sql_query(
      "SELECT thiet_bi, thoi_gian_bao, ten_su_co, du_kien_xong, nguoi_bao_cao"
      " FROM su_co ORDER BY id DESC",
      conn,
  )
  conn.close()

  if not df.empty:
    # Đổi tên cột hiển thị
    df_display = df.rename(
        columns={
            "thiet_bi": "MÁY",
            "thoi_gian_bao": "THỜI GIAN BÁO",
            "ten_su_co": "TÊN SỰ CỐ",
            "du_kien_xong": "THỜI GIAN DỰ KIẾN HOÀN THÀNH",
            "nguoi_bao_cao": "NGƯỜI BÁO CÁO",
        }
    )
    st.dataframe(df_display, use_container_width=True)
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
      all_text += f"🔹 MÁY: {row['thiet_bi']}\n"
      all_text += f"   • Thời gian báo: {row['thoi_gian_bao']}\n"
      all_text += f"   • Sự cố: {row['ten_su_co']}\n"
      all_text += f"   • Dự kiến hoàn thành: {row['du_kien_xong']}\n"
      all_text += f"   • Người báo cáo: {nguoi_gui}\n\n"

    st.code(all_text, language="text")
    st.divider()

    # SAO CHÉP RIÊNG TỪNG SỰ CỐ
    st.subheader("🔍 SAO CHÉP RIÊNG TỪNG SỰ CỐ")
    su_co_list = [
        f"Máy: {row['thiet_bi']} - {row['ten_su_co']} ({row['thoi_gian_bao']})"
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
          f"🛠️ BÁO CÁO SỰ CỐ\n"
          f"• MÁY: {selected_row['thiet_bi']}\n"
          f"• THỜI GIAN BÁO: {selected_row['thoi_gian_bao']}\n"
          f"• TÊN SỰ CỐ: {selected_row['ten_su_co']}\n"
          f"• DỰ KIẾN HOÀN THÀNH: {selected_row['du_kien_xong']}\n"
          f"• NGƯỜI BÁO CÁO: {nguoi_gui}"
      )

      st.code(single_text, language="text")

  else:
    st.info("Chưa có báo cáo sự cố nào.")
