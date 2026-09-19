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
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .badge-district {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    .source-title {
        font-size: 14px;
        color: #666;
        margin-top: 4px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. 读取并缓存数据
DATA_FILE = "Guangzhou_Premium_Spots_Cleaned.xlsx"


@st.cache_data
def load_data():
  if not os.path.exists(DATA_FILE):
    fallback = "Guangzhou_Premium_Spots_V5_AI_Fixed.xlsx"
    if os.path.exists(fallback):
      return pd.read_excel(fallback)
    return pd.DataFrame()
  return pd.read_excel(DATA_FILE)


df = load_data()

st.title("📍 广州出片机位情报局")
st.caption("基于全网高互动数据自动清洗 · 内部公测版")

if df.empty:
  st.warning("⚠️ 暂未检测到机位数据文件，请先确认 Excel 文件路径。")
  st.stop()

# 3. 筛选栏
districts = ["全部区域"]
extracted_districts = (
    df["提取地址"].str.extract(r"广州市\s*([^\s]+区)")[0].dropna().unique()
)
districts.extend(list(extracted_districts))

selected_district = st.selectbox("🔍 筛选区域", districts)

if selected_district != "全部区域":
  display_df = df[df["提取地址"].str.contains(selected_district, na=False)]
else:
  display_df = df

st.write(f"共找到 **{len(display_df)}** 个优质出片机位")
st.divider()

# 4. 卡片式内容渲染
for idx, row in display_df.iterrows():
  with st.container():
    title = str(row.get("帖子标题", "未命名机位"))
    address = str(row.get("提取地址", "广州市 待定"))
    collects = row.get("收藏量", 0)
    raw_images = str(row.get("全量本地照片", ""))

    img_list = [p.strip() for p in raw_images.split(" | ") if p.strip()]

    st.markdown(
        f"""
        <div class="badge-district">🗺️ {address}</div>
        <h3 style="margin:0; font-size:18px;">{title}</h3>
        <p class="source-title">🔥 收藏量: {collects}</p>
        """,
        unsafe_allow_html=True,
    )

    # 渲染首图或多图（已适配新参数 width='stretch'）
    if img_list and os.path.exists(img_list[0]):
      st.image(img_list[0], width="stretch")

      if len(img_list) > 1:
        with st.expander(f"查看更多实拍图 ({len(img_list)} 张)"):
          for extra_img in img_list[1:]:
            if os.path.exists(extra_img):
              st.image(extra_img, width="stretch")
    else:
      st.info("📷 暂无本地图片预览")

    st.write("---")