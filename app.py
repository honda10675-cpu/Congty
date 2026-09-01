from datetime import datetime, timedelta, timezone
import json
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client

SUPABASE_URL = "https://sndzaqqqrxoqlzemgboy.supabase.co"
SUPABASE_KEY = "DÁN_ANON_KEY_VÀO_ĐÂY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Báo Cáo Sự Cố",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def get_vn_now():
  vn_tz = timezone(timedelta(hours=7))
  return datetime.now(vn_tz)


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


def load_data():
  try:
    res = supabase.table("su_co").select("*").order("id", desc=False).execute()
    return pd.DataFrame(res.data)
  except Exception:
    return pd.DataFrame()


def insert_su_co_safe(data_dict):
  endpoint = f"{SUPABASE_URL}/rest/v1/su_co"
  headers = {
      "apikey": str(SUPABASE_KEY).strip(),
      "Authorization": f"Bearer {str(SUPABASE_KEY).strip()}",
      "Content-Type": "application/json; charset=utf-8",
      "Prefer": "return=minimal",
  }
  # Xử lý triệt để mã hóa Tiếng Việt UTF-8
  json_bytes = json.dumps(data_dict, ensure_ascii=False).encode("utf-8")
  res = requests.post(
      endpoint, headers=headers, data=json_bytes, timeout=10
  )
  res.raise_for_status()


st.markdown(
    """
    <style>
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

    .block-container { 
        padding-top: 0.1rem !important; 
        padding-bottom: 0.1rem !important; 
        padding-left: 0.2rem !important; 
        padding-right: 0.2rem !important; 
    }

    h1 { font-size: 0.95rem !important; margin: 0 !important; font-weight: 800 !important; text-align: center; color: #1b4332; }

    .mobile-table-container { width: 100%; margin-bottom: 8px; background: white; padding: 4px; border-radius: 4px;}
    .mobile-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px !important;
        background-color: #ffffff;
        table-layout: fixed;
    }
    .mobile-table th {
        background-color: #2d6a4f;
        color: #ffffff;
        padding: 5px 2px;
        text-align: center;
        border: 1px solid #52b788;
        font-size: 11px;
        font-weight: bold;
    }
    .mobile-table td {
        padding: 5px 3px;
        border: 1px solid #b7e4c7;
        text-align: center;
        word-wrap: break-word;
        font-size: 11px;
        vertical-align: middle;
        line-height: 1.2;
    }

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

    div[data-testid="stVerticalBlock"] > div { gap: 0.15rem !important; }

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

UNKNOWN_TIME_OPTION = "Chưa xác định thời gian"
time_slots = [UNKNOWN_TIME_OPTION] + [
    f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)
]

now_vn = get_vn_now()
default_time_str = f"{now_vn.hour:02d}:{'30' if now_vn.minute >= 30 else '00'}"
default_index = (
    time_slots.index(default_time_str) if default_time_str in time_slots else 1
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
    ten_su_co = st.text_input(
        "TÊN SỰ CỐ / BỆNH CỦA MÁY *", key="input_ten_su_co"
    )

    col3, col4 = st.columns(2)
    with col3:
      ngay_dk = st.date_input(
          "Ngày dự kiến hoàn thành *", value=now_vn.date(), key="ngay_dk_input"
      )
    with col4:
      gio_dk = st.selectbox(
          "Giờ dự kiến hoàn thành *",
          time_slots,
          index=default_index,
          key="gio_dk_input",
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
        if str(gio_dk) == UNKNOWN_TIME_OPTION:
          du_kien_str = "Chưa xác định"
        else:
          du_kien_str = f"{ngay_dk.strftime('%d/%m/%Y')} {gio_dk}"

        new_row = {
            "thiet_bi": str(thiet_bi).strip(),
            "thoi_gian_bao": get_rounded_time(get_vn_now()),
            "ten_su_co": str(ten_su_co).strip(),
            "du_kien_xong": du_kien_str,
            "nguoi_bao_cao": str(nguoi_bao_cao).strip(),
            "trang_thai": "Đang xử lý",
            "thoi_gian_xong": "",
        }

        try:
          insert_su_co_safe(new_row)
          st.session_state.reset_form = True
          st.session_state.show_success_msg = True
          st.rerun()
        except Exception as e:
          st.error(f"Lỗi gửi dữ liệu: {e}")

with tab2:
  df = load_data()

  if not df.empty and "id" in df:
    df_sorted = df.sort_values(by="id", ascending=False).reset_index(drop=True)

    components.html(
        """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <button onclick="captureTable()" style="
            background: #2d6a4f; color: white; border: none; padding: 6px 12px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 11px; width: 100%;
        ">📸 TẢI ẢNH BẢNG SỰ CỐ</button>

        <script>
        function captureTable() {
            var table = window.parent.document.querySelector(".mobile-table-container");
            if (table) {
                html2canvas(table).then(canvas => {
                    var link = document.createElement('a');
                    link.download = 'bang_su_co.png';
                    link.href = canvas.toDataURL();
                    link.click();
                });
            } else {
                alert("Không tìm thấy bảng dữ liệu!");
            }
        }
        </script>
        """,
        height=40,
    )

    rows_list = []
    for idx, row in df_sorted.iterrows():
      stt = f"{idx + 1}/"
      du_kien_val = str(row["du_kien_xong"])

      if du_kien_val == "Chưa xác định":
        du_kien_display = (
            "<span style='color:#d90429; font-weight:bold;'>Chưa xác"
            " định</span>"
        )
      elif " " in du_kien_val:
        parts = du_kien_val.split(" ")
        du_kien_display = (
            f"{parts[0]}<br><span style='color:#2d6a4f;"
            f" font-weight:bold;'>{parts[1]}</span>"
        )
      else:
        du_kien_display = du_kien_val

      if row["trang_thai"] == "✅ Đã xong":
        thiet_bi_display = (
            f"<span style='color:#2d6a4f;'>{row['thiet_bi']}</span> (Đã xong)"
        )
      else:
        thiet_bi_display = f"<b>{row['thiet_bi']}</b>"

      row_html = (
          f"<tr><td style='width: 8%; font-weight: bold;"
          f" color: #2d6a4f;'>{stt}</td><td style='width:"
          f" 22%;'>{thiet_bi_display}</td><td style='width: 42%; text-align:"
          f" left;'>{row['ten_su_co']} <span style='color:#666;"
          f" font-size:10px;'>({row['thoi_gian_bao']})</span></td><td"
          f" style='width: 28%;'>{du_kien_display}</td></tr>"
      )
      rows_list.append(row_html)

    all_rows = "".join(rows_list)
    table_html = (
        f'<div class="mobile-table-container"><table'
        ' class="mobile-table"><thead><tr><th style="width: 8%;">STT</th><th'
        ' style="width: 22%;">MÁY</th><th style="width: 42%;">SỰ CỐ (TG'
        ' BÁO)</th><th style="width:'
        f' 28%;">DỰ KIẾN HOÀN THÀNH</th></tr></thead><tbody>{all_rows}</tbody></table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    pending_df = df_sorted[df_sorted["trang_thai"] != "✅ Đã xong"]

    st.markdown("---")
    st.markdown("### 🔧 XÁC NHẬN SỬA XONG MÁY")

    if not pending_df.empty:
      pending_options = {
          f"{r['thiet_bi']} - {r['ten_su_co']}": r["id"]
          for _, r in pending_df.iterrows()
      }
      selected_machine = st.selectbox(
          "Chọn máy đã sửa xong:", list(pending_options.keys())
      )

      col_pass, col_btn = st.columns([2, 1])
      with col_pass:
        pwd_done = st.text_input(
            "Mật khẩu (230):", type="password", key="pwd_done"
        )
      with col_btn:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("✅ SỬA XONG"):
          if pwd_done == "230":
            target_id = int(pending_options[selected_machine])
            actual_done_time = get_rounded_time(get_vn_now())
            supabase.table("su_co").update({
                "trang_thai": "✅ Đã xong",
                "thoi_gian_xong": actual_done_time,
            }).eq("id", target_id).execute()
            st.success(f"🎉 Đã cập nhật xong lúc: {actual_done_time}")
            st.rerun()
          else:
            st.error("🔑 Sai mật khẩu!")
    else:
      st.info("Hiện không có sự cố nào đang chờ xử lý.")

    with st.expander("🔑 Admin xóa sự cố"):
      admin_pass = st.text_input("Mật khẩu Admin:", type="password")
      del_list = [
          f"{row['thiet_bi']} - {row['ten_su_co']}"
          for _, row in df_sorted.iterrows()
      ]
      selected_del = st.selectbox("Chọn sự cố cần xóa:", del_list)

      if st.button("❌ XÓA SỰ CỐ"):
        if admin_pass == "230":
          del_idx = del_list.index(selected_del)
          target_id = int(df_sorted.iloc[del_idx]["id"])
          supabase.table("su_co").delete().eq("id", target_id).execute()
          st.success("🗑️ Đã xóa sự cố thành công!")
          st.rerun()
        else:
          st.error("🔑 Sai mật khẩu Admin!")
  else:
    st.info("Chưa có báo cáo sự cố nào.")
