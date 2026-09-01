from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
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

    .mobile-table-container { width: 100%; margin-bottom: 8px; }
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
            "thiet_bi": str(thiet_bi.strip()),
            "thoi_gian_bao": str(get_rounded_time(get_vn_now())),
            "ten_su_co": str(ten_su_co.strip()),
            "du_kien_xong": str(du_kien_str),
            "nguoi_bao_cao": str(nguoi_bao_cao.strip()),
            "trang_thai": "Đang xử lý",
            "thoi_gian_xong": "",
        }

        try:
          supabase.table("su_co").insert(new_row).execute()
          st.session_state.reset_form = True
          st.session_state.show_success_msg = True
          st.rerun()
        except Exception as e:
          st.error(f"Lỗi gửi dữ liệu: {e}")

with tab2:
  df = load_data()

  if not df.empty and "id" in df:
    df_sorted = df.sort_values(by="id", ascending=False).reset_index(drop=True)

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

      row_html = (
          f"<tr><td style='width: 8%; font-weight: bold;"
          f" color: #2d6a4f;'>{stt}</td><td style='width: 18%; font-weight:"
          f" bold;'>{row['thiet_bi']}</td><td style='width: 46%; text-align:"
          f" left;'>{row['ten_su_co']} <span style='color:#666;"
          f" font-size:10px;'>({row['thoi_gian_bao']})</span></td><td"
          f" style='width: 28%;'>{du_kien_display}</td></tr>"
      )
      rows_list.append(row_html)

    all_rows = "".join(rows_list)
    table_html = (
        f'<div class="mobile-table-container"><table'
        ' class="mobile-table"><thead><tr><th style="width: 8%;">STT</th><th'
        ' style="width: 18%;">MÁY</th><th style="width: 46%;">SỰ CỐ (TG'
        ' BÁO)</th><th style="width:'
        f' 28%;">DỰ KIẾN HOÀN THÀNH</th></tr></thead><tbody>{all_rows}</tbody></table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # SAO CHÉP SỰ CỐ
    su_co_list = [
        f"{idx + 1}/ {row['thiet_bi']} - {row['ten_su_co']} [{row['trang_thai']}]"
        for idx, row in df_sorted.iterrows()
    ]
    selected_option = st.selectbox("Chọn sự cố copy:", su_co_list, index=0)

    if selected_option:
      selected_idx = su_co_list.index(selected_option)
      selected_row = df_sorted.iloc[selected_idx]

      nguoi_gui = (
          selected_row["nguoi_bao_cao"]
          if (
              pd.notna(selected_row["nguoi_bao_cao"])
              and str(selected_row["nguoi_bao_cao"]).strip()
          )
          else "N/A"
      )

      single_text = (
          f"MÁY: {selected_row['thiet_bi']}\n"
          f"THỜI GIAN BÁO: {selected_row['thoi_gian_bao']}\n"
          f"TÊN SỰ CỐ: {selected_row['ten_su_co']}\n"
          f"THỜI GIAN DỰ KIẾN HOÀN THÀNH: {selected_row['du_kien_xong']}\n"
      )
      if selected_row["trang_thai"] == "✅ Đã xong":
        single_text += f"THỜI GIAN HOÀN THÀNH THỰC TẾ: {selected_row['thoi_gian_xong']}\n"
      single_text += f"NGƯỜI BÁO CÁO: {nguoi_gui}"

      st.code(single_text, language="text")

    # XÁC NHẬN HOÀN THÀNH
    pending_df = df_sorted[df_sorted["trang_thai"] != "✅ Đã xong"]
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
        actual_done_time = get_rounded_time(get_vn_now())

        supabase.table("su_co").update({
            "trang_thai": "✅ Đã xong",
            "thoi_gian_xong": actual_done_time,
        }).eq("id", target_id).execute()

        st.success(f"🎉 Đã xong lúc: {actual_done_time}")
        st.rerun()

    # ADMIN XÓA
    with st.expander("🔑 Admin xóa"):
      admin_pass = st.text_input("Mật khẩu Admin:", type="password")
      del_list = [
          f"{row['thiet_bi']} - {row['ten_su_co']}"
          for _, row in df_sorted.iterrows()
      ]
      selected_del = st.selectbox("Sự cố xóa:", del_list)

      if st.button("❌ XÓA"):
        if admin_pass == "230":
          del_idx = del_list.index(selected_del)
          target_id = int(df_sorted.iloc[del_idx]["id"])

          supabase.table("su_co").delete().eq("id", target_id).execute()

          st.success("🗑️ Đã xóa!")
          st.rerun()
        else:
          st.error("🔑 Sai mật khẩu!")
  else:
    st.info("Chưa có báo cáo sự cố nào.")
