import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ Thống Báo Cáo Sự Cố", page_icon="🛠️", layout="wide"
)

# CSS giao diện xanh công nghiệp (đã rút gọn tránh lỗi dán)
st.markdown(
    "<style>.stApp{background:linear-gradient(135deg,#0f172a 0%,#1e293b"
    " 100%);color:#f8fafc;}div[data-testid='stForm']{background-color:#1e293b;border:1px"
    " solid #334155;border-radius:12px;padding:20px;}.stTextInput"
    " input,.stTextArea textarea,div[data-baseweb='select']{background-color:#0f172a"
    " !important;color:#f8fafc !important;border:1px solid #475569"
    " !important;border-radius:8px !important;}.stButton"
    " button,button[kind='FormSubmitButton']{background:linear-gradient(90deg,#2563eb"
    " 0%,#1d4ed8 100%) !important;color:white !important;font-weight:bold"
    " !important;border-radius:8px !important;width:100%;}</style>",
    unsafe_allow_html=True,
)


def init_db():
  conn = sqlite3.connect("su_co_web.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS su_co (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_su_co TEXT NOT NULL,
            thiet_bi TEXT NOT NULL,
            muc_do TEXT NOT NULL,
            trang_thai TEXT NOT NULL,
            nguoi_bao_cao TEXT,
            ngay_tao TEXT,
            mo_ta TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

st.title("🛠️ Báo Cáo & Theo Dõi Sự Cố")

tab1, tab2 = st.tabs(["📝 Khai Báo Mới", "📊 Danh Sách Quản Lý"])

with tab1:
  st.subheader("Khai báo sự cố kỹ thuật")
  with st.form("form_su_co", clear_on_submit=True):
    ten_su_co = st.text_input("Tên sự cố / Bệnh của máy *")
    thiet_bi = st.text_input("Tên thiết bị / Máy móc *")
    nguoi_bao_cao = st.text_input("Người báo cáo")
    muc_do = st.selectbox(
        "Mức độ ưu tiên", ["Thấp", "Trung bình", "Cao", "Khẩn cấp"], index=1
    )
    trang_thai = st.selectbox(
        "Trạng thái ban đầu",
        ["Mới ghi nhận", "Đang xử lý", "Đã hoàn thành"],
        index=0,
    )
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
                    INSERT INTO su_co (ten_su_co, thiet_bi, muc_do, trang_thai, nguoi_bao_cao, ngay_tao, mo_ta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                ten_su_co,
                thiet_bi,
                muc_do,
                trang_thai,
                nguoi_bao_cao,
                ngay_tao,
                mo_ta,
            ),
        )
        conn.commit()
        conn.close()
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("Danh sách quản lý sự cố")
  conn = sqlite3.connect("su_co_web.db")
  df = pd.read_sql_query("SELECT * FROM su_co ORDER BY id DESC", conn)
  conn.close()

  if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("Cập nhật trạng thái xử lý")
    col_a, col_b = st.columns(2)
    with col_a:
      selected_id = st.number_input("Nhập ID sự cố:", min_value=1, step=1)
    with col_b:
      new_status = st.selectbox(
          "Trạng thái mới:", ["Mới ghi nhận", "Đang xử lý", "Đã hoàn thành"]
      )

    if st.button("Cập nhật trạng thái"):
      conn = sqlite3.connect("su_co_web.db")
      c = conn.cursor()
      c.execute(
          "UPDATE su_co SET trang_thai=? WHERE id=?", (new_status, selected_id)
      )
      conn.commit()
      conn.close()
      st.success(f"Đã cập nhật trạng thái cho ID {selected_id}!")
      st.rerun()
  else:
    st.info("Chưa có báo cáo sự cố nào.")    mo_ta = st.text_area("Mô tả chi tiết sự cố")

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
                    INSERT INTO su_co (ten_su_co, thiet_bi, muc_do, trang_thai, nguoi_bao_cao, ngay_tao, mo_ta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                ten_su_co,
                thiet_bi,
                muc_do,
                trang_thai,
                nguoi_bao_cao,
                ngay_tao,
                mo_ta,
            ),
        )
        conn.commit()
        conn.close()
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("Danh sách quản lý sự cố")
  conn = sqlite3.connect("su_co_web.db")
  df = pd.read_sql_query("SELECT * FROM su_co ORDER BY id DESC", conn)
  conn.close()

  if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("Cập nhật trạng thái xử lý")
    col_a, col_b = st.columns(2)
    with col_a:
      selected_id = st.number_input("Nhập ID sự cố:", min_value=1, step=1)
    with col_b:
      new_status = st.selectbox(
          "Trạng thái mới:", ["Mới ghi nhận", "Đang xử lý", "Đã hoàn thành"]
      )

    if st.button("Cập nhật trạng thái"):
      conn = sqlite3.connect("su_co_web.db")
      c = conn.cursor()
      c.execute(
          "UPDATE su_co SET trang_thai=? WHERE id=?", (new_status, selected_id)
      )
      conn.commit()
      conn.close()
      st.success(f"Đã cập nhật trạng thái cho ID {selected_id}!")
      st.rerun()
  else:
    st.info("Chưa có báo cáo sự cố nào.")        padding: 10px 24px !important;
        width: 100%;
    }
    </style>
""",
    unsafe_allow_javascript=True,
)


def init_db():
  conn = sqlite3.connect("su_co_web.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS su_co (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_su_co TEXT NOT NULL,
            thiet_bi TEXT NOT NULL,
            muc_do TEXT NOT NULL,
            trang_thai TEXT NOT NULL,
            nguoi_bao_cao TEXT,
            ngay_tao TEXT,
            mo_ta TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

st.title("🛠️ Báo Cáo & Theo Dõi Sự Cố")

tab1, tab2 = st.tabs(["📝 Khai Báo Mới", "📊 Danh Sách Quản Lý"])

with tab1:
  st.subheader("Khai báo sự cố kỹ thuật")
  with st.form("form_su_co", clear_on_submit=True):
    ten_su_co = st.text_input("Tên sự cố / Bệnh của máy *")
    thiet_bi = st.text_input("Tên thiết bị / Máy móc / Dây chuyền *")
    nguoi_bao_cao = st.text_input("Người báo cáo")
    muc_do = st.selectbox(
        "Mức độ ưu tiên", ["Thấp", "Trung bình", "Cao", "Khẩn cấp"], index=1
    )
    trang_thai = st.selectbox(
        "Trạng thái ban đầu",
        ["Mới ghi nhận", "Đang xử lý", "Đã hoàn thành"],
        index=0,
    )
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
                    INSERT INTO su_co (ten_su_co, thiet_bi, muc_do, trang_thai, nguoi_bao_cao, ngay_tao, mo_ta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                ten_su_co,
                thiet_bi,
                muc_do,
                trang_thai,
                nguoi_bao_cao,
                ngay_tao,
                mo_ta,
            ),
        )
        conn.commit()
        conn.close()
        st.success("✅ Đã ghi nhận báo cáo sự cố thành công!")

with tab2:
  st.subheader("Danh sách quản lý sự cố")
  conn = sqlite3.connect("su_co_web.db")
  df = pd.read_sql_query("SELECT * FROM su_co ORDER BY id DESC", conn)
  conn.close()

  if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("Cập nhật trạng thái xử lý")
    col_a, col_b = st.columns(2)
    with col_a:
      selected_id = st.number_input("Nhập ID sự cố:", min_value=1, step=1)
    with col_b:
      new_status = st.selectbox(
          "Trạng thái mới:", ["Mới ghi nhận", "Đang xử lý", "Đã hoàn thành"]
      )

    if st.button("Cập nhật trạng thái"):
      conn = sqlite3.connect("su_co_web.db")
      c = conn.cursor()
      c.execute(
          "UPDATE su_co SET trang_thai=? WHERE id=?", (new_status, selected_id)
      )
      conn.commit()
      conn.close()
      st.success(f"Đã cập nhật trạng thái cho ID {selected_id}!")
      st.rerun()
  else:
    st.info("Chưa có báo cáo sự cố nào.")      st.rerun()
  else:
    st.info("Chưa có báo cáo nào.")
