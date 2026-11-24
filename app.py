import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import random
import time

# ================= 页面配置与基础设置 =================
st.set_page_config(page_title="动物百科监控大屏", layout="wide", initial_sidebar_state="expanded")

# ================= 自定义 HTML 表格渲染 =================
def render_html_table(df, is_dark=False):
    if is_dark:
        table_style = "width:100%; border-collapse: collapse; color: #E2E8F0; font-size: 14px;"
        th_style = "padding: 12px; text-align: left; border-bottom: 2px solid #00E5FF; color: #00E5FF; background-color: rgba(0, 229, 255, 0.05);"
        td_style = "padding: 10px 12px; border-bottom: 1px solid #1E293B;"
    else:
        table_style = "width:100%; border-collapse: collapse; color: #2C3E2D; font-size: 14px;"
        th_style = "padding: 12px; text-align: left; border-bottom: 2px solid #2E8B57; color: #1B5E20; background-color: #F1F8E9;"
        td_style = "padding: 10px 12px; border-bottom: 1px solid #E0E0E0;"

    html = f'<table style="{table_style}"><thead><tr>'
    for col in df.columns:
        html += f'<th style="{th_style}">{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td style="{td_style}">{val}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# ================= 基础科普绿模式 CSS =================
st.markdown("""
    <style>
    @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    .fade-in { animation: fadeIn 0.8s ease-in-out; }
    
    @keyframes blink { 0% { color: #D32F2F; } 50% { color: #FF8A80; } 100% { color: #D32F2F; } }
    .alert-text { animation: blink 1s infinite; font-weight: bold; font-size: 20px; }

    .stApp { background-color: #F4F8F4; transition: background-color 0.5s; }
    h1, h2, h3 { color: #1B5E20; font-weight: 600; }
    
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

dark_mode = st.sidebar.checkbox("🌌 炫酷蓝大屏模式", value=False)

# ================= 炫酷蓝动态暗黑主题 CSS =================
if dark_mode:
    st.markdown("""
        <style>
        @keyframes moveBackground {
            from { background-position: 0 0, 0 0, 0 0; }
            to { background-position: 20px 20px, 40px 40px, 40px 40px; }
        }
        
        .stApp { 
            background-color: #0A0E17 !important; 
            background-image: 
                radial-gradient(#00E5FF 1px, transparent 1px),
                linear-gradient(rgba(0, 229, 255, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 229, 255, 0.08) 1px, transparent 1px) !important;
            background-size: 20px 20px, 40px 40px, 40px 40px !important;
            animation: moveBackground 3s linear infinite !important;
        }
        
        h1, h2, h3, p, span, div, label { color: #E2E8F0 !important; }
        
        div[data-testid="stMetric"] { 
            background-color: rgba(15, 23, 42, 0.8) !important; 
            border: 1px solid rgba(0, 229, 255, 0.2) !important;
            border-top: 4px solid #00E5FF !important;
            border-radius: 12px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important; 
        }
        div[data-testid="stPlotlyChart"] { 
            background-color: rgba(15, 23, 42, 0.8) !important; 
            border: 1px solid rgba(0, 229, 255, 0.2) !important; 
            border-radius: 12px !important;
            padding: 15px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        }
        
        [data-testid="stSidebar"] { background-color: #0B1120 !important; border-right: 1px solid #1E293B; }
        div[data-baseweb="select"] > div { background-color: #1E293B !important; border-color: #334155 !important; color: #E2E8F0 !important; border-radius: 8px; }
        div[data-baseweb="select"] svg { fill: #00E5FF !important; color: #00E5FF !important; }
        input { background-color: #1E293B !important; color: #E2E8F0 !important; }
        
        .stDownloadButton > button {
            background-color: #1E293B !important; border: 1px solid #00E5FF !important; 
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
        }
        .stDownloadButton > button * { color: #00E5FF !important; font-weight: bold !important; }
        .stDownloadButton > button:hover { background-color: #00E5FF !important; }
        .stDownloadButton > button:hover * { color: #0A0E17 !important; }

        .detail-card {
            background-color: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(0, 229, 255, 0.2);
            border-left: 4px solid #00E5FF;
            border-radius: 12px;
            padding: 20px;
            margin-top: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        .detail-card p { margin-bottom: 12px !important; font-size: 15px; line-height: 1.5;}
        .detail-card strong { color: #00E5FF !important; }

        /* 下拉弹层核心修复 */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] div,
        div[data-baseweb="popover"] ul[role="listbox"] {
            background-color: #0F172A !important;
            border: none !important;
            outline: none !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"] li {
            background-color: transparent !important;
            color: #E2E8F0 !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            border-radius: 0 !important; 
            margin: 0 !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"] li * {
            color: #E2E8F0 !important;
            background-color: transparent !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"] li:hover {
            background-color: rgba(0, 229, 255, 0.05) !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] {
            background-color: #1E293B !important;
            border-left: 3px solid #00E5FF !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] * {
            color: #00E5FF !important;
            font-weight: bold !important;
        }
        div[data-baseweb="popover"] ul[role="listbox"]::-webkit-scrollbar { width: 6px; }
        div[data-baseweb="popover"] ul[role="listbox"]::-webkit-scrollbar-track { background: transparent; }
        div[data-baseweb="popover"] ul[role="listbox"]::-webkit-scrollbar-thumb {
            background-color: rgba(0, 229, 255, 0.4);
            border-radius: 10px;
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
chart_bg = 'rgba(0,0,0,0)' 
chart_font_color = '#E2E8F0' if dark_mode else '#2C3E2D'
chart_grid_color = '#1E293B' if dark_mode else '#F0F0F0'

chart_layout = dict(
    plot_bgcolor=chart_bg, paper_bgcolor=chart_bg,
    margin=dict(t=50, b=30, l=20, r=10), 
    font=dict(color=chart_font_color),
    title_font=dict(color=chart_font_color),
    legend_font=dict(color=chart_font_color)
)

bar_color_seq = px.colors.sequential.Blues_r if dark_mode else px.colors.sequential.Greens_r
habitat_color_seq = px.colors.sequential.Purples_r if dark_mode else px.colors.qualitative.Set2

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
    
    if dark_mode:
        color_map = {"极危":"#0284C7", "濒危":"#0369A1", "易危":"#075985", "近危":"#0C4A6E", "无危":"#1E3A8A", "数据缺乏":"#334155"}
    else:
        color_map = {"极危":"#D32F2F", "濒危":"#F57C00", "易危":"#FBC02D", "近危":"#AFB42B", "无危":"#7CB342", "数据缺乏":"#9E9E9E"}
        
    fig_pie = px.pie(iucn_counts, names="等级", values="数量", hole=0.6, title="IUCN 濒危等级占比", color="等级", color_discrete_map=color_map)
    fig_pie.update_layout(**chart_layout)
    fig_pie.update_layout(legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02, font=dict(size=12)))
    st.plotly_chart(fig_pie, use_container_width=True)

with row2_col3:
    habitat_counts = filtered_df["habitat"].value_counts().reset_index()
    habitat_counts.columns = ["栖息地", "数量"]
    fig_habitat = px.bar(habitat_counts, x="数量", y="栖息地", orientation='h', title="栖息地分布情况", color="栖息地", color_discrete_sequence=habitat_color_seq)
    fig_habitat.update_layout(**chart_layout)
    fig_habitat.update_layout(legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.02, font=dict(size=12)))
    fig_habitat.update_xaxes(showgrid=True, gridcolor=chart_grid_color)
    fig_habitat.update_yaxes(showgrid=True, gridcolor=chart_grid_color)
    st.plotly_chart(fig_habitat, use_container_width=True)

# ================= 趋势分析区 (核心优化) =================
st.markdown("### 📉 数据分析")
row3_col1, row3_col2 = st.columns([7, 3])

# 1. 先渲染两边的标题，保证在同一高度
with row3_col1:
    st.markdown("#### 体重与寿命关系散点图")
with row3_col2:
    st.markdown("#### 🏆 寿命最长 Top 5")

# 2. 再渲染下方的图表和表格
with row3_col1:
    # 移除了 title 参数，使图表紧贴标题
    fig_scatter = px.scatter(filtered_df, x="weight_kg", y="lifespan_years", color="class_name", hover_name="chinese_name", 
                             labels={"weight_kg": "体重 (kg)", "lifespan_years": "寿命 (年)", "class_name": "纲"})
    
    # 因为没有了标题，上边距(margin t)适当减小一点
    chart_layout_scatter = chart_layout.copy()
    chart_layout_scatter['margin'] = dict(t=10, b=30, l=20, r=10) 
    
    fig_scatter.update_layout(**chart_layout_scatter)
    fig_scatter.update_layout(
        legend=dict(orientation="v", yanchor="top", y=0.98, xanchor="left", x=1.0, font=dict(size=13), itemwidth=30)
    )
    fig_scatter.update_xaxes(showgrid=True, gridcolor=chart_grid_color)
    fig_scatter.update_yaxes(showgrid=True, gridcolor=chart_grid_color)
    st.plotly_chart(fig_scatter, use_container_width=True)

with row3_col2:
    top5 = filtered_df.nlargest(5, "lifespan_years")[["chinese_name", "lifespan_years"]].copy()
    top5.columns = ["动物名称", "寿命 (年)"]
    st.markdown(render_html_table(top5, is_dark=dark_mode), unsafe_allow_html=True)

# ================= 明细数据区 =================
row4_col1, row4_spacer, row4_col2 = st.columns([6, 0.2, 3.8])

with row4_col1:
    st.markdown("### 📋 物种明细")
    detail_df = filtered_df[["chinese_name", "scientific_name", "class_name", "iucn_level", "habitat"]].copy()
    detail_df.columns = ["中文名", "学名", "纲目", "濒危等级", "栖息地"]
    st.markdown(render_html_table(detail_df.head(15), is_dark=dark_mode), unsafe_allow_html=True)
    st.caption("注：仅展示前 15 条数据，可通过侧边栏筛选查看更多。")

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
        
        if dark_mode:
            detail_html = f"""
            <div class="detail-card">
                <h3 style="margin-top:0; color:#00E5FF !important;">{animal_info['chinese_name']} <span style="font-size:16px; color:#94A3B8 !important; font-weight:normal;">({animal_info['english_name']})</span></h3>
                <p><strong>学名：</strong> <i style="color:#E2E8F0 !important;">{animal_info['scientific_name']}</i></p>
                <p><strong>分类：</strong> <span style="color:#E2E8F0 !important;">{animal_info['class_name']} > {animal_info['order_name']} > {animal_info['family_name']}</span></p>
                <p><strong>IUCN等级：</strong> <span style="color:#38BDF8 !important; font-weight:bold;">{animal_info['iucn_level']}</span></p>
                <p><strong>分布地区：</strong> <span style="color:#E2E8F0 !important;">{animal_info['region']}</span></p>
                <p><strong>食性：</strong> <span style="color:#E2E8F0 !important;">{animal_info['diet']}</span></p>
                <p><strong>体型：</strong> <span style="color:#E2E8F0 !important;">体长 {animal_info['body_length_m']} 米，体重 {animal_info['weight_kg']} 千克</span></p>
                <p style="margin-bottom:0;"><strong>简介：</strong> <span style="color:#E2E8F0 !important;">{animal_info['description']}</span></p>
            </div>
            """
            st.markdown(detail_html, unsafe_allow_html=True)
        else:
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
