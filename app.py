import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 页面配置：沉浸式暗黑模式
st.set_page_config(page_title="Risk Terminal Dark", layout="wide")

# 2. 深度定制 CSS (Bloomberg 终端风格)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&display=swap');
    
    /* 背景与全局文字 */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Q萌标题保持，但颜色换成荧光色 */
    h1 {
        font-family: 'ZCOOL KuaiLe', cursive;
        color: #00D1FF;
        text-shadow: 0px 0px 10px rgba(0,209,255,0.3);
    }
    
    /* 卡片美化：深色半透明毛玻璃 */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border-radius: 20px;
        padding: 20px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* 调整 Tab 颜色适配暗黑模式 */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #8B949E; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #58A6FF; }
    
    /* 隐藏顶部白条 */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📟 个人资产风险监控终端")

# --- 侧边栏：核心设置 ---
with st.sidebar:
    st.markdown("### 🛰️ 终端配置")
    currency = st.selectbox("基准币种", ["CNY", "USD", "JPY"])
    ex_rate = st.number_input("实时汇率 (USD/CNY)", value=7.23)
    inflation = st.slider("预期通胀 (%)", 1, 10, 3)
    st.divider()
    risk_pref = st.select_slider("风险容忍度", options=["极低", "均衡", "激进"])

# --- 资产录入 ---
col_in, col_main = st.columns([1, 2], gap="large")
with col_in:
    st.markdown("### 📥 数据注入")
    cash = st.number_input("🏦 现金存款", value=300000, step=10000)
    stocks = st.number_input("📈 权益类 (股票/基金)", value=150000, step=10000)
    crypto = st.number_input("🧪 另类资产 (币/黄金)", value=20000, step=2000)
    others = st.number_input("🛡️ 固收/债基", value=80000, step=5000)

# --- 核心逻辑计算 ---
total = cash + stocks + crypto + others
# 风险加权计算
volatility = (stocks * 0.5 + crypto * 1.5 + others * 0.1) / total
health_score = max(int(100 - volatility * 120), 0)
if risk_pref == "极低": health_score = max(health_score - 10, 0)

# --- 右侧：可视化面板 ---
with col_main:
    tab_dist, tab_risk = st.tabs(["构成比例", "风险维度"])
    
    with tab_dist:
        labels = ["现金", "权益", "另类", "固收"]
        values = [cash, stocks, crypto, others]
        # 暗黑系马卡龙色 (带透明度)
        colors = ['rgba(121, 82, 179, 0.8)', 'rgba(56, 139, 253, 0.8)', 
                  'rgba(248, 81, 73, 0.8)', 'rgba(63, 185, 80, 0.8)']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.6,
                                         textinfo='label+percent', textposition='outside',
                                         marker=dict(colors=colors, line=dict(color='#0E1117', width=2)),
                                         hoverinfo='none')])
        fig_pie.update_layout(showlegend=False, height=450, 
                              paper_bgcolor='rgba(0,0,0,0)', 
                              font=dict(color='#E0E0E0'))
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab_risk:
        # 雷达图：衡量真正的风控维度
        categories = ['流动性', '防御力', '进攻力', '抗通胀', '抗风险']
        radar_values = [
            (cash/total)*10, 
            (others/total)*10, 
            (stocks/total)*10, 
            (crypto/total + stocks/total)*8,
            (health_score/10)
        ]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=radar_values, theta=categories, fill='toself',
                                            line_color='#58A6FF', fillcolor='rgba(88, 166, 255, 0.2)'))
        fig_radar.update_layout(polar=dict(
                                    bgcolor="#161B22",
                                    radialaxis=dict(visible=True, range=[0, 10], gridcolor="#30363D"),
                                    angularaxis=dict(gridcolor="#30363D")),
                                showlegend=False, height=450, 
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#E0E0E0'))
        st.plotly_chart(fig_radar, use_container_width=True)

# --- 底部：关键指标 ---
st.divider()
c1, c2, c3, c4 = st.columns(4)

# 货币符号映射
sym = {"CNY": "¥", "USD": "$", "JPY": "¥"}[currency]
val_display = total if currency == "CNY" else total / ex_rate

c1.metric("总资产折算", f"{sym}{val_display:,.0f}")
c2.metric("健康指数", f"{health_score}%")

# 5年后购买力：考虑通胀后的实际价值
real_value = total * ((1 - inflation/100) ** 5)
c3.metric("5年后购买力", f"{sym}{real_value/ (1 if currency=='CNY' else ex_rate):,.0f}", f"-{inflation}%/yr")

c4.metric("风险预判", "PASS" if health_score > 70 else "REBALANCING", 
          delta="偏高" if health_score < 70 else "稳健", delta_color="inverse")

# --- 专家建议栏 ---
st.markdown("### 💡 终端诊断意见")
if health_score < 60:
    st.error(f"当前【{risk_pref}】模型检测到严重的风险暴露。建议削减另类资产，将现金比例提升至总资产的 30% 以上。")
else:
    st.success(f"资产韧性良好。当前配置足以抵御约 {inflation+2}% 的年化波动损耗。")