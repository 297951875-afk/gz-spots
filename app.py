import os
import re
import pandas as pd
import streamlit as st

# 1. 页面基本配置
st.set_page_config(
    page_title="广州出片机位情报局",
    page_icon="📸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 注入轻量 CSS
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .badge-district {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .source-title {
        font-size: 14px;
        color: #666;
        margin-top: 4px;
        margin-bottom: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. 读取并缓存数据
DATA_FILE = "Guangzhou_Premium_Spots_Cleaned.xlsx"


@st.cache_data
def load_data():
  if os.path.exists(DATA_FILE):
    return pd.read_excel(DATA_FILE)

  fallback = "Guangzhou_Premium_Spots_V5_AI_Fixed.xlsx"
  if os.path.exists(fallback):
    return pd.read_excel(fallback)

  return pd.DataFrame()


df = load_data()

st.title("📍 广州出片机位情报局")
st.caption("基于全网高互动数据自动清洗 · 内部公测版")

if df.empty:
  st.warning("⚠️ 暂未检测到机位数据文件，请先确认 Excel 文件已上传。")
  st.stop()


# 地址标签清理函数（去除方括号等杂质）
def clean_display_address(addr):
  if not isinstance(addr, str):
    return "广州市 待定"
  return re.sub(r"[【】\[\]]", "", addr).strip()


# 3. 筛选栏
districts = ["全部区域"]
extracted = (
    df["提取地址"].astype(str).str.extract(r"广州市\s*([^\s]+区)")[0].dropna().unique()
)
districts.extend(list(extracted))

selected_district = st.selectbox("🔍 筛选区域", districts)

if selected_district != "全部区域":
  display_df = df[df["提取地址"].astype(str).str.contains(selected_district, na=False)]
else:
  display_df = df

st.write(f"共找到 **{len(display_df)}** 个优质出片机位")
st.divider()

# 4. 卡片式内容渲染
for idx, row in display_df.iterrows():
  with st.container():
    title = str(row.get("帖子标题", "未命名机位"))
    raw_address = str(row.get("提取地址", "广州市 待定"))
    address = clean_display_address(raw_address)
    collects = row.get("收藏量", 0)
    raw_images = str(row.get("全量本地照片", ""))

    # 路径标准化（跨平台转换，兼容 Linux 云端）
    raw_imgs = [
        p.strip().replace("\\", "/")
        for p in raw_images.split(" | ")
        if p.strip() and p.strip() != "nan"
    ]

    # 过滤出当前物理路径真实存在的图片
    valid_imgs = [p for p in raw_imgs if os.path.exists(p)]

    # 卡片信息
    st.markdown(
        f"""
        <div class="badge-district">🗺️ {address}</div>
        <h3 style="margin:0; font-size:18px;">{title}</h3>
        <p class="source-title">🔥 收藏量: {collects}</p>
        """,
        unsafe_allow_html=True,
    )

    # 图片展示
    if valid_imgs:
      st.image(valid_imgs[0], width="stretch")

      if len(valid_imgs) > 1:
        with st.expander(f"查看更多实拍图 ({len(valid_imgs)} 张)"):
          for extra_img in valid_imgs[1:]:
            st.image(extra_img, width="stretch")
    else:
      st.info("📷 暂无本地图片预览")

    st.write("---")
