import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import random
import time

# ================= 页面配置与基础设置 =================
st.set_page_config(page_title="动物百科监控大屏", layout="wide", initial_sidebar_state="expanded")

# ================= 基础科普绿模式 CSS =================
st.markdown("""
    <style>
    /* 1. 渐入动画 */
    @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeIn 0.8s ease-in-out; }
    
    /* 2. 预警闪烁 */
    @keyframes blink { 0% { color: #D32F2F; } 50% { color: #FF8A80; } 100% { color: #D32F2F; } }
    .alert-text { animation: blink 1s infinite; font-weight: bold; font-size: 20px; }

    /* 3. 基础科普绿模式 */
    .stApp { background-color: #F4F8F4; transition: background-color 0.5s; }
    h1, h2, h3 { color: #1B5E20; font-weight: 600; }
    
    /* 4. 卡片化 */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04); border-top: 4px solid #2E8B57; margin-bottom: 10px;
    }
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF; border-radius: 12px; padding: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .modebar { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ================= 侧边栏控制 =================
st.sidebar.header("⚙️ 监控与显示设置")
realtime_mode = st.sidebar.checkbox("📡 开启实时数据监控", value=False)
if realtime_mode:
    st_autorefresh(interval=2000, key="realtime_refresh")
    st.sidebar.success("实时监控中...")

dark_mode = st.sidebar.checkbox("🌌 科技风动态大屏", value=False)

# ================= 科技风动态暗黑主题 CSS =================
if dark_mode:
    st.markdown("""
        <style>
        /* 1. 动态星空网格背景动画 */
        @keyframes moveBackground {
            from { background-position: 0 0, 0 0, 0 0; }
            to { background-position: 20px 20px, 40px 40px, 40px 40px; }
        }
        
        .stApp { 
            background-color: #0E1117 !important; 
            /* 由点、横向线、纵向线构成的科技网格 */
            background-image: 
                radial-gradient(#00FF7F 1px, transparent 1px),
                linear-gradient(rgba(46, 139, 87, 0.2) 1px, transparent 1px),
                linear-gradient(90deg, rgba(46, 139, 87, 0.2) 1px, transparent 1px) !important;
            background-size: 20px 20px, 40px 40px, 40px 40px !important;
            animation: moveBackground 3s linear infinite !important;
        }
        
        /* 2. 强制全局文字颜色 */
        h1, h2, h3, p, span, div, label { color: #E0E0E0 !important; }
        
        /* 3. 卡片与侧边栏 */
        div[data-testid="stMetric"] { background-color: #1E1E1E !important; border-top: 4px solid #00FF7F; box-shadow: 0 0 15px rgba(0, 255, 127, 0.2); }
        div[data-testid="stPlotlyChart"] { background-color: rgba(30, 30, 30, 0.8) !important; border: 1px solid rgba(0, 255, 127, 0.3); }
        [data-testid="stSidebar"] { background-color: #161B22 !important; }
        
        /* 4. 修复下拉框 */
        div[data-baseweb="select"] > div { background-color: #2B313E !important; border-color: #444 !important; color: #E0E0E0 !important; }
        ul[data-testid="stSelectboxVirtualDropdown"] { background-color: #1E1E1E !important; }
        ul[data-testid="stSelectboxVirtualDropdown"] li { color: #E0E0E0 !important; }
        input { background-color: #2B313E !important; color: #E0E0E0 !important; }
        
        /* 5. 修复数据表格 */
        div[data-testid="stDataFrame"] { background-color: rgba(30, 30, 30, 0.8) !important; border-radius: 8px; border: 1px solid #333; }
        div[data-testid="stDataFrame"] * { color: #E0E0E0 !important; }
        
        /* 6. 修复底部数据导出按钮 */
        div[data-testid="stDownloadButton"] button {
            background-color: #2B313E !important; border: 1px solid #00FF7F !important; 
            box-shadow: 0 0 10px rgba(0, 255, 127, 0.3);
        }
        div[data-testid="stDownloadButton"] button p {
            color: #00FF7F !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

auto_carousel = st.sidebar.checkbox("🎞️ 开启详情自动轮播", value=False)

st.sidebar.markdown("---")
st.sidebar.header("数据筛选")

@st.cache_data
def load_data():
    return pd.read_csv("data/animals.csv")

if realtime_mode:
    df = load_data()
    df.loc[df["iucn_level"].isin(["极危", "濒危", "易危"]), "iucn_level"] = df[df["iucn_level"].isin(["极危", "濒危", "易危"])]["iucn_level"].apply(
        lambda x: x if random.random() > 0.1 else random.choice(["极危", "濒危", "易危", "近危"])
    )
else:
    df = load_data()

search_query = st.sidebar.text_input("🔍 搜索动物名称/学名", "")
class_list = ["全部"] + list(df["class_name"].unique())
selected_class = st.sidebar.selectbox("选择纲目", class_list)
iucn_list = ["全部"] + list(df["iucn_level"].unique())
selected_iucn = st.sidebar.selectbox("选择IUCN等级", iucn_list)

filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["chinese_name"].str.contains(search_query) | filtered_df["scientific_name"].str.contains(search_query, case=False)]
if selected_class != "全部":
    filtered_df = filtered_df[filtered_df["class_name"] == selected_class]
if selected_iucn != "全部":
    filtered_df = filtered_df[filtered_df["iucn_level"] == selected_iucn]

if filtered_df.empty:
    st.warning("没有找到符合条件的动物数据，请调整筛选条件。")
    st.stop()

# ================= 页面主内容 =================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.title("🐾 动物百科实时监控看板")
st.markdown("探索动物分类、濒危等级与栖息地分布")

threatened_species = len(filtered_df[filtered_df["iucn_level"].isin(["极危", "濒危", "易危"])])
if threatened_species > 50:
    st.error("🚨 **实时预警**：受威胁物种数已超过 50 种，请立即关注！")

st.markdown("### 📊 核心数据概览")
col1, col2, col3, col4 = st.columns(4)

total_species = len(filtered_df)
families = filtered_df["family_name"].nunique()
avg_lifespan = round(filtered_df["lifespan_years"].mean(), 1)

col1.metric("物种总数", f"{total_species} 种")
if threatened_species > 50:
    with col2:
        st.metric("受威胁物种数", f"{threatened_species} 种", delta="超限", delta_color="inverse")
        st.markdown(f"<div class='alert-text'>🚨 达 {threatened_species} 种！</div>", unsafe_allow_html=True)
else:
    col2.metric("受威胁物种数", f"{threatened_species} 种")

col3.metric("科属数量", f"{families} 科")
col4.metric("平均寿命", f"{avg_lifespan} 年")

st.markdown("<br>", unsafe_allow_html=True)

# ================= 图表通用配置 =================
chart_font_color = '#E0E0E0' if dark_mode else '#2C3E2D'
chart_grid_color = '#333333' if dark_mode else '#F0F0F0'

# 核心修复：增加 legend_font 确保图例文字颜色生效
chart_layout = dict(
    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=50, b=30, l=20, r=10), 
    font=dict(color=chart_font_color),
    title_font=dict(color=chart_font_color),
    legend_font=dict(color=chart_font_color)
)

# 根据模式选择图表色系（暗黑模式下用亮色）
bar_color_seq = px.colors.sequential.Teal_r if dark_mode else px.colors.sequential.Greens_r

# ================= 维度统计区 =================
st.markdown("### 📈 维度统计")
row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    class_counts = filtered_df["class_name"].value_counts().reset_index()
    class_counts.columns = ["纲", "数量"]
    fig_bar = px.bar(class_counts, x="纲", y="数量", title="各纲物种数量对比", color="纲", color_discrete_sequence=bar_color_seq)
    fig_bar.update_layout(**chart_layout)
    fig_bar.update_layout(legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02, font=dict(size=12)))
    fig_bar.update_xaxes(showgrid=True, gridcolor=chart_grid_color)
    fig_bar.update_yaxes(showgrid=True, gridcolor=chart_grid_color)
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_col2:
    iucn_order = ["极危", "濒危", "易危", "近危", "无危", "数据缺乏"]
    iucn_counts = filtered_df["iucn_level"].value_counts().reindex(iucn_order).dropna().reset_index()
    iucn_counts.columns = ["等级", "数量"]
    fig_pie = px.pie(iucn_counts, names="等级", values="数量", hole=0.6, title="IUCN 濒危等级占比", color="等级",
                     color_discrete_map={"极危":"#D32F2F", "濒危":"#F57C00", "易危":"#FBC02D", "近危":"#AFB42B", "无危":"#7CB342", "数据缺乏":"#9E9E9E"})
    fig_pie.update_layout(**chart_layout)
    fig_pie.update_layout(legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02, font=dict(size=12)))
    st.plotly_chart(fig_pie, use_container_width=True)

with row2_col3:
    habitat_counts = filtered_df["habitat"].value_counts().reset_index()
    habitat_counts.columns = ["栖息地", "数量"]
    fig_habitat = px.bar(habitat_counts, x="数量", y="栖息地", orientation='h', title="栖息地分布情况", color="栖息地", color_discrete_sequence=px.colors.qualitative.Set2)
    fig_habitat.update_layout(**chart_layout)
    fig_habitat.update_layout(legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02, font=dict(size=12)))
    fig_habitat.update_xaxes(showgrid=True, gridcolor=chart_grid_color)
    fig_habitat.update_yaxes(showgrid=True, gridcolor=chart_grid_color)
    st.plotly_chart(fig_habitat, use_container_width=True)

# ================= 趋势分析区 =================
st.markdown("### 📉 数据分析")
row3_col1, row3_col2 = st.columns([7, 3])

with row3_col1:
    fig_scatter = px.scatter(filtered_df, x="weight_kg", y="lifespan_years", color="class_name", hover_name="chinese_name", title="体重与寿命关系散点图", labels={"weight_kg": "体重 (kg)", "lifespan_years": "寿命 (年)", "class_name": "纲"})
    fig_scatter.update_layout(**chart_layout)
    fig_scatter.update_layout(
        legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.0, font=dict(size=13), itemwidth=30)
    )
    fig_scatter.update_xaxes(showgrid=True, gridcolor=chart_grid_color)
    fig_scatter.update_yaxes(showgrid=True, gridcolor=chart_grid_color)
    st.plotly_chart(fig_scatter, use_container_width=True)

with row3_col2:
    st.markdown("#### 🏆 寿命最长 Top 5")
    top5 = filtered_df.nlargest(5, "lifespan_years")[["chinese_name", "lifespan_years"]].copy()
    top5.columns = ["动物名称", "寿命 (年)"]
    st.dataframe(top5, hide_index=True, use_container_width=True, height=260)

# ================= 明细数据区 =================
row4_col1, row4_spacer, row4_col2 = st.columns([5.5, 1, 3.5])

with row4_col1:
    st.markdown("### 📋 物种明细")
    detail_df = filtered_df[["chinese_name", "scientific_name", "class_name", "iucn_level", "habitat"]].copy()
    detail_df.columns = ["中文名", "学名", "纲目", "濒危等级", "栖息地"]
    st.dataframe(detail_df, use_container_width=True, height=320)

with row4_col2:
    st.markdown("### 🔍 物种详情卡")
    animal_names = filtered_df["chinese_name"].tolist()
    
    if auto_carousel:
        current_index = int(time.time() / 2) % len(animal_names)
        selected_animal = animal_names[current_index]
        st.info(f"🎞️ 自动轮播中：当前展示 **{selected_animal}**")
    else:
        selected_animal = st.selectbox("选择物种", animal_names, label_visibility="collapsed")
    
    if selected_animal:
        animal_info = filtered_df[filtered_df["chinese_name"] == selected_animal].iloc[0]
        st.info(f"**{animal_info['chinese_name']}** ({animal_info['english_name']})")
        st.write(f"**学名**：*{animal_info['scientific_name']}*")
        st.write(f"**分类**：{animal_info['class_name']} > {animal_info['order_name']} > {animal_info['family_name']}")
        st.write(f"**IUCN等级**：{animal_info['iucn_level']}")
        st.write(f"**分布地区**：{animal_info['region']}")
        st.write(f"**食性**：{animal_info['diet']}")
        st.write(f"**体型**：体长 {animal_info['body_length_m']} 米，体重 {animal_info['weight_kg']} 千克")
        st.write(f"**简介**：{animal_info['description']}")

st.markdown('</div>', unsafe_allow_html=True)

# ================= 数据导出 =================
st.markdown("---")
st.markdown("### 📥 数据导出")
csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(label="下载当前筛选的动物数据 (CSV)", data=csv, file_name='filtered_animals.csv', mime='text/csv')