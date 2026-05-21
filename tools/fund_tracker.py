import datetime
import json
import os
import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="300ETF定投多维追踪", layout="wide")
st.title("📈 华泰 300ETF 联接C - 全方位数据监控")
st.caption("数据自动更新 | 暂停状态跨会话持久化 | 当前环境：Streamlit 2026 标准")

# ──────────────────────────────────────────────────────────────
# 基础配置
# ──────────────────────────────────────────────────────────────
FUND_CODE  = "006131"
START_DATE = "2026-03-09"

# 暂停状态持久化文件（与脚本同目录）
PAUSE_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pause_state.json")

# ──────────────────────────────────────────────────────────────
# 暂停状态：读 / 写 / 工具函数
# ──────────────────────────────────────────────────────────────
# pause_state.json 结构：
#   {
#     "is_paused": bool,
#     "current_pause_start": "YYYY-MM-DD" | null,
#     "history": [
#       {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
#       ...
#     ]
#   }

def _load_pause_state() -> dict:
    if os.path.exists(PAUSE_STATE_FILE):
        with open(PAUSE_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"is_paused": False, "current_pause_start": None, "history": []}


def _save_pause_state(state: dict) -> None:
    with open(PAUSE_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _pause_intervals(state: dict) -> list:
    """
    返回完整区间列表 [(start_str, end_str), ...]。
    当前仍在暂停时，end 取今天。
    """
    today_str = datetime.date.today().isoformat()
    intervals = [(r["start"], r["end"]) for r in state["history"]]
    if state["is_paused"] and state["current_pause_start"]:
        intervals.append((state["current_pause_start"], today_str))
    return intervals


# ──────────────────────────────────────────────────────────────
# 侧边栏：配置 + 暂停开关
# ──────────────────────────────────────────────────────────────
pause_state = _load_pause_state()

with st.sidebar:
    st.header("配置参数")
    WEEKLY_AMOUNT = st.number_input("每周定投金额 (元)", value=300, step=50)

    st.divider()
    st.subheader("⏸ 定投暂停控制")

    if pause_state["is_paused"]:
        st.error(f"**当前状态：已暂停**\n\n暂停开始：`{pause_state['current_pause_start']}`")
        if st.button("▶️ 恢复定投", width="stretch", type="primary"):
            today_str = datetime.date.today().isoformat()
            # 将当前暂停段写入历史
            pause_state["history"].append({
                "start": pause_state["current_pause_start"],
                "end":   today_str,
            })
            pause_state["is_paused"] = False
            pause_state["current_pause_start"] = None
            _save_pause_state(pause_state)
            st.cache_data.clear()
            st.rerun()
    else:
        st.success("**当前状态：正在定投**")
        if st.button("⏸ 开始暂停定投", width="stretch"):
            pause_state["is_paused"] = True
            pause_state["current_pause_start"] = datetime.date.today().isoformat()
            _save_pause_state(pause_state)
            st.cache_data.clear()
            st.rerun()

    # 历史暂停记录折叠展示
    if pause_state["history"]:
        with st.expander(f"历史暂停记录（{len(pause_state['history'])} 次）"):
            for r in reversed(pause_state["history"]):
                st.markdown(f"- {r['start']} → {r['end']}")

    st.info("💡 若周一休市，系统将自动顺延至本周第一个交易日买入。")


# ──────────────────────────────────────────────────────────────
# 数据处理函数
# ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_investment_data(
    code: str,
    start_date: str,
    amount: float,
    pause_intervals_json: str,  # JSON 字符串，保证 cache key 可哈希
) -> pd.DataFrame:
    """
    按 ISO 周历逐周扫描净值，生成定投 / 暂停记录。

    暂停规则：
      某周【首个交易日】落在任意暂停区间 → 整周跳过。
      支持多段不连续暂停，跨会话状态自动读取。
    """
    raw: list = json.loads(pause_intervals_json)
    parsed: list = [
        (datetime.date.fromisoformat(s), datetime.date.fromisoformat(e))
        for s, e in raw
    ]

    def _in_any_pause(d: datetime.date) -> bool:
        return any(s <= d <= e for s, e in parsed)

    # 拉取净值
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
    except Exception as ex:
        st.error(f"获取数据失败: {ex}")
        return pd.DataFrame()

    df["净值日期"] = pd.to_datetime(df["净值日期"])
    df = (
        df[df["净值日期"] >= pd.to_datetime(start_date)]
        .sort_values("净值日期")
        .reset_index(drop=True)
    )
    if df.empty:
        return df

    df["year_week"] = df["净值日期"].dt.strftime("%G-%V")

    total_shares      = 0.0
    total_investment  = 0.0
    last_handled_week = None

    df["是否买入日"]   = False
    df["是否暂停周"]   = False
    df["本次买入份额"] = 0.0
    df["累计投入"]     = 0.0
    df["当前市值"]     = 0.0
    df["累计净收益"]   = 0.0

    for i, row in df.iterrows():
        current_week = row["year_week"]
        trade_date   = row["净值日期"].date()

        # 每周只在首个交易日决策一次
        if current_week != last_handled_week:
            last_handled_week = current_week

            if _in_any_pause(trade_date):
                df.at[i, "是否暂停周"] = True
            else:
                shares = amount / row["单位净值"]
                total_shares     += shares
                total_investment += amount
                df.at[i, "是否买入日"]   = True
                df.at[i, "本次买入份额"] = shares

        df.at[i, "累计投入"]   = total_investment
        df.at[i, "当前市值"]   = total_shares * row["单位净值"]
        df.at[i, "累计净收益"] = df.at[i, "当前市值"] - total_investment

    return df


# ──────────────────────────────────────────────────────────────
# 加载数据
# ──────────────────────────────────────────────────────────────
intervals_json = json.dumps(_pause_intervals(pause_state), ensure_ascii=False)
data = get_investment_data(FUND_CODE, START_DATE, WEEKLY_AMOUNT, intervals_json)

# ──────────────────────────────────────────────────────────────
# 主界面
# ──────────────────────────────────────────────────────────────
if not data.empty:

    if pause_state["is_paused"]:
        st.warning(
            f"⏸ **定投暂停中**，自 **{pause_state['current_pause_start']}** 起生效。"
            "  关闭页面后状态自动保持，点击侧边栏「▶️ 恢复定投」可继续。"
        )

    # 核心指标
    latest       = data.iloc[-1]
    profit       = latest["累计净收益"]
    profit_rate  = (profit / latest["累计投入"] * 100) if latest["累计投入"] > 0 else 0
    paused_weeks = int(data["是否暂停周"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("当前单位净值", f"{latest['单位净值']:.4f}")
    c2.metric("累计投入本金", f"¥{latest['累计投入']:.2f}")
    c3.metric("累计净收益",   f"¥{profit:.2f}", f"{profit_rate:.2f}%")
    c4.metric("已暂停周数",   f"{paused_weeks} 周")

    st.divider()

    # ── 图表 1：净值走势 ───────────────────────────────────────
    st.subheader("1. 基金净值走势")
    nav_min, nav_max = data["单位净值"].min(), data["单位净值"].max()
    padding = (nav_max - nav_min) * 0.1

    fig_nav = go.Figure()
    fig_nav.add_trace(go.Scatter(
        x=data["净值日期"], y=data["单位净值"],
        mode="lines", name="单位净值",
        line=dict(color="#1f77b4", width=2),
        fill="tozeroy", fillcolor="rgba(31,119,180,0.05)",
    ))

    # 已结束暂停段 → 灰色区域
    for seg in pause_state["history"]:
        fig_nav.add_vrect(
            x0=seg["start"], x1=seg["end"],
            fillcolor="rgba(128,128,128,0.12)", line_width=0,
            annotation_text="已暂停", annotation_position="top left",
            annotation=dict(font_size=10, font_color="gray"),
        )
    # 当前进行中暂停 → 红色区域
    if pause_state["is_paused"] and pause_state["current_pause_start"]:
        fig_nav.add_vrect(
            x0=pause_state["current_pause_start"],
            x1=datetime.date.today().isoformat(),
            fillcolor="rgba(220,53,69,0.10)", line_width=0,
            annotation_text="暂停中", annotation_position="top left",
            annotation=dict(font_size=10, font_color="crimson"),
        )

    fig_nav.update_layout(
        hovermode="x unified", height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(range=[nav_min - padding, nav_max + padding], tickformat=".4f"),
    )
    st.plotly_chart(fig_nav, width="stretch")

    # ── 图表 2：资产增长对比 ───────────────────────────────────
    st.subheader("2. 资产规模增长 (本金 vs 市值)")
    fig_assets = go.Figure()
    fig_assets.add_trace(go.Scatter(
        x=data["净值日期"], y=data["累计投入"],
        name="累计本金", line=dict(color="#7f7f7f", dash="dot"),
    ))
    fig_assets.add_trace(go.Scatter(
        x=data["净值日期"], y=data["当前市值"],
        name="资产总市值", line=dict(color="#ff7f0e", width=3),
    ))
    fig_assets.add_trace(go.Scatter(
        x=data["净值日期"], y=data["累计净收益"],
        name="累计净收益 (右轴)",
        line=dict(color="#2ca02c"), yaxis="y2", opacity=0.8,
    ))
    fig_assets.update_layout(
        hovermode="x unified", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="总金额 (元)"),
        yaxis2=dict(title="净利润 (元)", overlaying="y", side="right", showgrid=False),
    )
    st.plotly_chart(fig_assets, width="stretch")

    # ── 明细表格 ──────────────────────────────────────────────
    st.divider()
    tab_buy, tab_pause_log = st.tabs(["📅 定投记录明细", "⏸ 暂停记录"])

    with tab_buy:
        buy_df = data[data["是否买入日"]].copy()
        if not buy_df.empty:
            disp = buy_df[["净值日期", "单位净值", "本次买入份额"]].copy()
            disp["投入本金"] = WEEKLY_AMOUNT
            disp["累计份额"] = buy_df["本次买入份额"].cumsum().values
            disp = disp.sort_values("净值日期", ascending=False)
            st.dataframe(
                disp,
                column_config={
                    "净值日期":     st.column_config.DateColumn("成交日期",  format="YYYY-MM-DD"),
                    "单位净值":     st.column_config.NumberColumn("成交价格", format="%.4f"),
                    "投入本金":     st.column_config.NumberColumn("投入金额", format="¥%.2f"),
                    "本次买入份额": st.column_config.NumberColumn("新增份额", format="%.2f 份"),
                    "累计份额":     st.column_config.NumberColumn("累计份额", format="%.2f 份"),
                },
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("本统计区间内暂无定投记录。")

    with tab_pause_log:
        pause_rows = data[data["是否暂停周"]].copy()
        if not pause_rows.empty:
            p_disp = pause_rows[["净值日期", "单位净值", "year_week"]].rename(
                columns={"净值日期": "跳过日期", "单位净值": "当日净值", "year_week": "周号"}
            ).copy()
            p_disp["跳过金额"] = WEEKLY_AMOUNT
            p_disp = p_disp.sort_values("跳过日期", ascending=False)
            st.dataframe(
                p_disp,
                column_config={
                    "跳过日期": st.column_config.DateColumn("跳过日期", format="YYYY-MM-DD"),
                    "周号":     st.column_config.TextColumn("ISO 周号"),
                    "当日净值": st.column_config.NumberColumn("当日净值", format="%.4f"),
                    "跳过金额": st.column_config.NumberColumn("跳过金额", format="¥%.2f"),
                },
                hide_index=True,
                width="stretch",
            )
            total_skipped = len(p_disp) * WEEKLY_AMOUNT
            st.caption(f"共跳过 {len(p_disp)} 周，累计少投入 ¥{total_skipped:.2f}")
        else:
            st.info("暂无暂停记录。")

else:
    st.warning("未检索到相关数据。")