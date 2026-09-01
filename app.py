import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client

# --- CẤU HÌNH SUPABASE ---
SUPABASE_URL = "https://sndzaqqqrxoqlzemgboy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNuZHphcXFxcnhvcWx6ZW1nYm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMDM1MDMsImV4cCI6MjEwMzY3OTUwM30.N-7hXggITi6yM8VZPtDMWehb1_i1IsR6P5vDMQ6-hJg"  # Thay bằng Anon Key chuẩn của anh

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Báo Cáo & Theo Dõi Sự Cố | 故障报告与跟踪",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --- HÀM DỊCH ĐA TẦNG (ĐẢM BẢO LUÔN DỊCH ĐƯỢC TIẾNG TRUNG) ---
def auto_translate_to_zh(text):
  if not text or not text.strip():
    return ""

  query_text = text.strip()
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
      )
  }

  # Cách 1: Google Translate API (v1)
  try:
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=vi&tl=zh-CN&dt=t&q={urllib.parse.quote(query_text)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=4) as response:
      result = json.loads(response.read().decode("utf-8"))
      if result and len(result) > 0 and result[0]:
        zh_parts = [
            item[0] for item in result[0] if len(item) > 0 and item[0]
        ]
        res = "".join(zh_parts).strip()
        if res:
          return res
  except Exception:
    pass

  # Cách 2: MyMemory Translation API (Dự phòng 1)
  try:
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(query_text)}&langpair=vi|zh-CN"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=4) as response:
      data = json.loads(response.read().decode("utf-8"))
      if data and "responseData" in data and "translatedText" in data["responseData"]:
        res = data["responseData"]["translatedText"].strip()
        if res and res.lower() != query_text.lower():
          return res
  except Exception:
    pass

  # Cách 3: Lingva Translate API (Dự phòng 2)
  try:
    url = f"https://lingva.ml/api/v1/vi/zh/{urllib.parse.quote(query_text)}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=4) as response:
      data = json.loads(response.read().decode("utf-8"))
      if data and "translation" in data:
        res = data["translation"].strip()
        if res:
          return res
  except Exception:
    pass

  return ""


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
  except Exception as e:
    st.error(f"❌ Lỗi tải dữ liệu từ Supabase: {e}")
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

    h1 { font-size: 0.9rem !important; margin: 0 !important; font-weight: 800 !important; text-align: center; color: #1b4332; }

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
        font-size: 10px;
        font-weight: bold;
    }
    .mobile-table td {
        padding: 5px 3px;
        border: 1px solid #b7e4c7;
        text-align: center;
        word-wrap: break-word;
        font-size: 11px;
        vertical-align: middle;
        line-height: 1.25;
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
        font-size: 11px !important; 
        height: 34px !important; 
        min-height: 34px !important;
        margin-top: 2px !important; 
    }

    button[data-baseweb="tab"] { 
        font-size: 10px !important; 
        font-weight: bold !important; 
        padding: 2px 4px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

UNKNOWN_TIME_OPTION = "Chưa xác định thời gian / 未确定时间"
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

st.markdown(
    "<h1>🛠️ BÁO CÁO & THEO DÕI SỰ CỐ / 故障报告与跟踪</h1>",
    unsafe_allow_html=True,
)
tab1, tab2 = st.tabs(
    ["📝 KHAI BÁO MỚI / 新建申报", "📊 QUẢN LÝ SỰ CỐ / 故障管理"]
)

with tab1:
  if st.session_state.show_success_msg:
    st.success("🎉 GỬI BÁO CÁO THÀNH CÔNG / 提交成功！")
    st.balloons()
    st.session_state.show_success_msg = False

  with st.form("form_su_co", clear_on_submit=False):
    thiet_bi = st.text_input("MÁY / THIẾT BỊ / 设备 *", key="input_thiet_bi")
    ten_su_co = st.text_input(
        "TÊN SỰ CỐ / BỆNH CỦA MÁY / 故障名称 *", key="input_ten_su_co"
    )

    col3, col4 = st.columns(2)
    with col3:
      ngay_dk = st.date_input(
          "Ngày dự kiến hoàn thành / 预计完成日期 *",
          value=now_vn.date(),
          key="ngay_dk_input",
      )
    with col4:
      gio_dk = st.selectbox(
          "Giờ dự kiến hoàn thành / 预计完成时间 *",
          time_slots,
          index=default_index,
          key="gio_dk_input",
      )

    nguoi_bao_cao = st.text_input(
        "NGƯỜI BÁO CÁO / 报告人 *", key="input_nguoi_bao_cao"
    )
    submit = st.form_submit_button("🚀 GỬI BÁO CÁO SỰ CỐ / 提交故障报告")

    if submit:
      missing_fields = []
      if not thiet_bi.strip():
        missing_fields.append("MÁY/设备")
      if not ten_su_co.strip():
        missing_fields.append("SỰ CỐ/故障")
      if not nguoi_bao_cao.strip():
        missing_fields.append("NGƯỜI BÁO CÁO/报告人")

      if missing_fields:
        st.error(f"⚠️ Chưa nhập / 未填写: {', '.join(missing_fields)}")
      else:
        with st.spinner("Đang tự động dịch sang tiếng Trung..."):
          ten_su_co_vi = ten_su_co.strip()
          ten_su_co_zh = auto_translate_to_zh(ten_su_co_vi)

          if ten_su_co_zh and ten_su_co_zh.lower() != ten_su_co_vi.lower():
            full_su_co_bilingual = (
                f"{ten_su_co_vi}<br><span"
                f" style='color:#2d6a4f;font-weight:bold;'>{ten_su_co_zh}</span>"
            )
          else:
            full_su_co_bilingual = ten_su_co_vi

        if str(gio_dk) == UNKNOWN_TIME_OPTION:
          du_kien_str = "Chưa xác định / 未确定"
        else:
          du_kien_str = f"{ngay_dk.strftime('%d/%m/%Y')} {gio_dk}"

        new_row = {
            "thiet_bi": str(thiet_bi).strip(),
            "thoi_gian_bao": get_rounded_time(get_vn_now()),
            "ten_su_co": full_su_co_bilingual,
            "du_kien_xong": du_kien_str,
            "nguoi_bao_cao": str(nguoi_bao_cao).strip(),
            "trang_thai": "Đang xử lý",
            "thoi_gian_xong": "",
        }

        try:
          supabase.table("su_co").insert(new_row).execute()
          st.session_state.reset_form = True
          st.session_state.show_success_msg = True
          st.rerun()
        except Exception as e:
          st.error(f"Lỗi gửi dữ liệu / 提交错误: {e}")

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
        ">📸 TẢI ẢNH BẢNG SỰ CỐ / 下载故障表格图片</button>

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

      if "Chưa xác định" in du_kien_val:
        du_kien_display = (
            "<span style='color:#d90429; font-weight:bold;'>Chưa xác định /"
            " 未确定</span>"
        )
      elif " " in du_kien_val:
        parts = du_kien_val.split(" ")
        du_kien_display = (
            f"{parts[0]}<div style='margin-top: 6px; color:#2d6a4f;"
            f" font-weight:bold;'>{parts[1]}</div>"
        )
      else:
        du_kien_display = du_kien_val

      if row["trang_thai"] == "✅ Đã xong":
        thiet_bi_display = (
            f"<span style='color:#2d6a4f;'>{row['thiet_bi']}</span> (Đã xong /"
            " 已完成)"
        )
      else:
        thiet_bi_display = f"<b>{row['thiet_bi']}</b>"

      ten_su_co_display = str(row["ten_su_co"])

      row_html = (
          f"<tr><td style='width: 8%; font-weight: bold;"
          f" color: #2d6a4f;'>{stt}</td><td style='width:"
          f" 22%;'>{thiet_bi_display}</td><td style='width: 42%; text-align:"
          f" left;'>{ten_su_co_display} <span style='color:#666;"
          f" font-size:10px;'>({row['thoi_gian_bao']})</span></td><td"
          f" style='width: 28%;'>{du_kien_display}</td></tr>"
      )
      rows_list.append(row_html)

    all_rows = "".join(rows_list)
    table_html = (
        f'<div class="mobile-table-container"><table'
        ' class="mobile-table"><thead><tr><th style="width: 8%;">STT</th><th'
        ' style="width: 22%;">MÁY<br>设备</th><th style="width: 42%;">SỰ CỐ'
        ' (TG BÁO)<br>故障 (时间)</th><th style="width: 28%;">DỰ KIẾN HOÀN'
        f' THÀNH<br>预计完成</th></tr></thead><tbody>{all_rows}</tbody></table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)

    pending_df = df_sorted[df_sorted["trang_thai"] != "✅ Đã xong"]

    st.markdown("---")
    st.markdown("### 🔧 XÁC NHẬN SỬA XONG MÁY / 确认维修完成")

    if not pending_df.empty:
      pending_options = {}
      for _, r in pending_df.iterrows():
        clean_name = (
            str(r["ten_su_co"])
            .replace("<br>", " ")
            .replace("<span style='color:#2d6a4f;font-weight:bold;'>", "")
            .replace("<span style='color:#555;'>", "")
            .replace("</span>", "")
        )
        pending_options[f"{r['thiet_bi']} - {clean_name}"] = r["id"]

      selected_machine = st.selectbox(
          "Chọn máy đã sửa xong / 选择已修好的设备:",
          list(pending_options.keys()),
      )

      col_pass, col_btn = st.columns([2, 1])
      with col_pass:
        pwd_done = st.text_input(
            "Mật khẩu / 密码 (230):", type="password", key="pwd_done"
        )
      with col_btn:
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        if st.button("✅ SỬA XONG / 完成"):
          if pwd_done == "230":
            target_id = int(pending_options[selected_machine])
            actual_done_time = get_rounded_time(get_vn_now())
            supabase.table("su_co").update({
                "trang_thai": "✅ Đã xong",
                "thoi_gian_xong": actual_done_time,
            }).eq("id", target_id).execute()
            st.success(
                f"🎉 Đã cập nhật xong lúc: {actual_done_time} / 已更新完成"
            )
            st.rerun()
          else:
            st.error("🔑 Sai mật khẩu / 密码错误!")
    else:
      st.info("Hiện không có sự cố nào đang chờ xử lý / 暂无待处理故障。")

    with st.expander("✏️ Sửa nội dung báo cáo sai / 修改错误申报"):
      edit_options = {}
      for _, row in df_sorted.iterrows():
        clean_name = (
            str(row["ten_su_co"])
            .replace("<br>", " ")
            .replace("<span style='color:#2d6a4f;font-weight:bold;'>", "")
            .replace("<span style='color:#555;'>", "")
            .replace("</span>", "")
        )
        edit_options[f"{row['thiet_bi']} - {clean_name}"] = row["id"]

      selected_edit = st.selectbox(
          "Chọn sự cố cần sửa / 选择要修改的故障:", list(edit_options.keys())
      )
      target_edit_id = int(edit_options[selected_edit])
      edit_row = df_sorted[df_sorted["id"] == target_edit_id].iloc[0]

      raw_su_co = str(edit_row["ten_su_co"]).split("<br>")[0]

      new_tb = st.text_input("Tên máy mới / 新设备名:", value=edit_row["thiet_bi"])
      new_sc_vi = st.text_input(
          "Tên sự cố tiếng Việt mới / 新故障名称:", value=raw_su_co
      )
      edit_pass = st.text_input(
          "Mật khẩu xác nhận / 密码 (230):", type="password", key="edit_pwd"
      )

      if st.button("💾 CẬP NHẬT LẠI / 更新"):
        if edit_pass == "230":
          with st.spinner("Đang dịch và cập nhật lại..."):
            zh_trans = auto_translate_to_zh(new_sc_vi.strip())
            if zh_trans and zh_trans.lower() != new_sc_vi.strip().lower():
              new_full_sc = (
                  f"{new_sc_vi.strip()}<br><span"
                  f" style='color:#2d6a4f;font-weight:bold;'>{zh_trans}</span>"
              )
            else:
              new_full_sc = new_sc_vi.strip()

            supabase.table("su_co").update({
                "thiet_bi": new_tb.strip(),
                "ten_su_co": new_full_sc,
            }).eq("id", target_edit_id).execute()

            st.success("✅ Đã sửa thành công / 修改成功！")
            st.rerun()
        else:
          st.error("🔑 Sai mật khẩu / 密码错误!")

    with st.expander("🔑 Admin xóa sự cố / 管理员删除"):
      admin_pass = st.text_input("Mật khẩu Admin / 管理员密码:", type="password")
      del_options = {}
      for _, row in df_sorted.iterrows():
        clean_name = (
            str(row["ten_su_co"])
            .replace("<br>", " ")
            .replace("<span style='color:#2d6a4f;font-weight:bold;'>", "")
            .replace("<span style='color:#555;'>", "")
            .replace("</span>", "")
        )
        del_options[f"{row['thiet_bi']} - {clean_name}"] = row["id"]

      selected_del = st.selectbox(
          "Chọn sự cố cần xóa / 选择要删除的故障:", list(del_options.keys())
      )

      if st.button("❌ XÓA SỰ CỐ / 删除"):
        if admin_pass == "230":
          target_id = int(del_options[selected_del])
          supabase.table("su_co").delete().eq("id", target_id).execute()
          st.success("🗑️ Đã xóa sự cố thành công / 删除成功！")
          st.rerun()
        else:
          st.error("🔑 Sai mật khẩu Admin / 密码错误!")
  else:
    st.info("Chưa có báo cáo sự cố nào / 暂无故障报告。")
