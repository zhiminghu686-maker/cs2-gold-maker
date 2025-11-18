import streamlit as st

import Snakebite_Recoil_Case
import Spectrum_Case
import Dreams_Nightmares_Operation_Riptide_Case
import Revolution_Clutch_Case

st.set_page_config(page_title="CS2 炼金工具合集", layout="wide")

# 初始化页面状态
if "page" not in st.session_state:
    st.session_state.page = "home"


# ========== 主逻辑：页面切换 ==========
if st.session_state.page == "home":

    st.title("🧰 CS2 炼金工具合集")
    st.markdown("请选择一个功能进入：")
    st.write("")

    # 四个按钮大卡片布局
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🐍 蛇噬 / 反冲 手套炼金", use_container_width=True):
            st.session_state.page = "snake"

    with col2:
        if st.button("✨ 光谱武器箱 炼刀", use_container_width=True):
            st.session_state.page = "spectrum"

    with col1:
        if st.button("😈 梦魇 / 激流大行动 炼刀", use_container_width=True):
            st.session_state.page = "nightmare"

    with col2:
        if st.button("💀 命悬 / 变革 手套炼金", use_container_width=True):
            st.session_state.page = "revolution"

# ========== 各自页面 ==========
elif st.session_state.page == "snake":
    st.button("⬅ 返回首页", on_click=lambda: st.session_state.update({"page": "home"}))
    Snakebite_Recoil_Case.render()

elif st.session_state.page == "spectrum":
    st.button("⬅ 返回首页", on_click=lambda: st.session_state.update({"page": "home"}))
    Spectrum_Case.render()

elif st.session_state.page == "nightmare":
    st.button("⬅ 返回首页", on_click=lambda: st.session_state.update({"page": "home"}))
    Dreams_Nightmares_Operation_Riptide_Case.render()

elif st.session_state.page == "revolution":
    st.button("⬅ 返回首页", on_click=lambda: st.session_state.update({"page": "home"}))
    Revolution_Clutch_Case.render()
