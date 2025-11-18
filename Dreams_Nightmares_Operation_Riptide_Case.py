import json
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from matplotlib import font_manager
import matplotlib.pyplot as plt
import os

# ================== 字体 ==================
# 1. 找你下载的字体（名字要和你上传的一样）
font_path = Path(__file__).parent / "NotoSansCJKsc-Regular.otf"

if font_path.exists():
    # 2. 注册字体
    font_manager.fontManager.addfont(str(font_path))
    # 3. 动态获取这个字体真正的名字，避免写错
    font_prop = font_manager.FontProperties(fname=str(font_path))
    font_name = font_prop.get_name()
    # 4. 告诉 matplotlib 用这个
    plt.rcParams["font.family"] = font_name
else:
    # 本地兜底
    win_font_path = r"C:\Windows\Fonts\msyh.ttc"
    if os.path.exists(win_font_path):
        font_manager.fontManager.addfont(win_font_path)
        plt.rcParams["font.family"] = "Microsoft YaHei"
    else:
        plt.rcParams["font.sans-serif"] = ["SimHei"]

# 负号不变方块
plt.rcParams["axes.unicode_minus"] = False

# ================== 基础配置 ==================
API_KEY = st.secrets["API_KEY"]
PRICE_URL = "https://open.steamdt.com/open/cs2/v1/price/single"
DATA_FILE = Path("knives.json")

# ================== 名称映射（刀 + 红皮） ==================
STEAMDT_NAME_MAP = {
    # ===== Shadow Daggers 暗影双匕 =====
    "暗影双匕｜澄澈之水": "★ Shadow Daggers | Bright Water",
    "暗影双匕｜黑色层压板": "★ Shadow Daggers | Black Laminate",
    "暗影双匕｜自由之手": "★ Shadow Daggers | Freehand",
    "暗影双匕｜传说": "★ Shadow Daggers | Lore",
    "暗影双匕｜自动化": "★ Shadow Daggers | Autotronic",
    "暗影双匕｜伽玛多普勒": "★ Shadow Daggers | Gamma Doppler",

    # ===== Bowie Knife 鲍伊猎刀 =====
    "鲍伊猎刀｜澄澈之水": "★ Bowie Knife | Bright Water",
    "鲍伊猎刀｜黑色层压板": "★ Bowie Knife | Black Laminate",
    "鲍伊猎刀｜自由之手": "★ Bowie Knife | Freehand",
    "鲍伊猎刀｜传说": "★ Bowie Knife | Lore",
    "鲍伊猎刀｜自动化": "★ Bowie Knife | Autotronic",
    "鲍伊猎刀｜伽玛多普勒": "★ Bowie Knife | Gamma Doppler",

    # ===== Huntsman Knife 猎杀者匕首 =====
    "猎杀者匕首｜澄澈之水": "★ Huntsman Knife | Bright Water",
    "猎杀者匕首｜黑色层压板": "★ Huntsman Knife | Black Laminate",
    "猎杀者匕首｜自由之手": "★ Huntsman Knife | Freehand",
    "猎杀者匕首｜传说": "★ Huntsman Knife | Lore",
    "猎杀者匕首｜自动化": "★ Huntsman Knife | Autotronic",
    "猎杀者匕首｜伽玛多普勒": "★ Huntsman Knife | Gamma Doppler",

    # ===== Falchion Knife 弯刀 =====
    "弯刀｜黑色层压板": "★ Falchion Knife | Black Laminate",
    "弯刀｜澄澈之水": "★ Falchion Knife | Bright Water",
    "弯刀｜自由之手": "★ Falchion Knife | Freehand",
    "弯刀｜传说": "★ Falchion Knife | Lore",
    "弯刀｜自动化": "★ Falchion Knife | Autotronic",
    "弯刀｜伽玛多普勒": "★ Falchion Knife | Gamma Doppler",

    # ===== Butterfly Knife 蝴蝶刀 =====
    "蝴蝶刀｜黑色层压板": "★ Butterfly Knife | Black Laminate",
    "蝴蝶刀｜澄澈之水": "★ Butterfly Knife | Bright Water",
    "蝴蝶刀｜自由之手": "★ Butterfly Knife | Freehand",
    "蝴蝶刀｜传说": "★ Butterfly Knife | Lore",
    "蝴蝶刀｜自动化": "★ Butterfly Knife | Autotronic",
    "蝴蝶刀｜伽玛多普勒": "★ Butterfly Knife | Gamma Doppler",

    # ===== 红皮材料（枪） =====
    "MP9 | 星使": "MP9 | Starlight Protector",
    "AK-47 | 夜愿": "AK-47 | Nightwish",
    "沙漠之鹰 | 纵横波涛": "Desert Eagle | Ocean Drive",
    "AK-47 | 抽象派 1337": "AK-47 | Leet Museo",
}

# ================== 默认数据 ==================
DEFAULT_KNIVES = [
    # Shadow Daggers
    {"name": "暗影双匕｜澄澈之水", "min_price": 0},
    {"name": "暗影双匕｜黑色层压板", "min_price": 0},
    {"name": "暗影双匕｜自由之手", "min_price": 0},
    {"name": "暗影双匕｜传说", "min_price": 0},
    {"name": "暗影双匕｜自动化", "min_price": 0},
    {"name": "暗影双匕｜伽玛多普勒", "min_price": 0},

    # Bowie Knife
    {"name": "鲍伊猎刀｜澄澈之水", "min_price": 0},
    {"name": "鲍伊猎刀｜黑色层压板", "min_price": 0},
    {"name": "鲍伊猎刀｜自由之手", "min_price": 0},
    {"name": "鲍伊猎刀｜传说", "min_price": 0},
    {"name": "鲍伊猎刀｜自动化", "min_price": 0},
    {"name": "鲍伊猎刀｜伽玛多普勒", "min_price": 0},

    # Huntsman Knife
    {"name": "猎杀者匕首｜澄澈之水", "min_price": 0},
    {"name": "猎杀者匕首｜黑色层压板", "min_price": 0},
    {"name": "猎杀者匕首｜自由之手", "min_price": 0},
    {"name": "猎杀者匕首｜传说", "min_price": 0},
    {"name": "猎杀者匕首｜自动化", "min_price": 0},
    {"name": "猎杀者匕首｜伽玛多普勒", "min_price": 0},

    # Falchion Knife
    {"name": "弯刀｜黑色层压板", "min_price": 0},
    {"name": "弯刀｜澄澈之水", "min_price": 0},
    {"name": "弯刀｜自由之手", "min_price": 0},
    {"name": "弯刀｜传说", "min_price": 0},
    {"name": "弯刀｜自动化", "min_price": 0},
    {"name": "弯刀｜伽玛多普勒", "min_price": 0},

    # Butterfly Knife
    {"name": "蝴蝶刀｜黑色层压板", "min_price": 0},
    {"name": "蝴蝶刀｜澄澈之水", "min_price": 0},
    {"name": "蝴蝶刀｜自由之手", "min_price": 0},
    {"name": "蝴蝶刀｜传说", "min_price": 0},
    {"name": "蝴蝶刀｜自动化", "min_price": 0},
    {"name": "蝴蝶刀｜伽玛多普勒", "min_price": 0},
]

DEFAULT_WEAPONS = [
    {"name": "MP9 | 星使", "min_price": 0},
    {"name": "AK-47 | 夜愿", "min_price": 0},
    {"name": "沙漠之鹰 | 纵横波涛", "min_price": 0},
    {"name": "AK-47 | 抽象派 1337", "min_price": 0},
]

# ================== 材料枪磨损区间 ==================
WEAR_RANGE = {
    "MP9 | 星使": (0.0, 0.80),
    "AK-47 | 夜愿": (0.0, 1.0),
    "AK-47 | 抽象派 1337": (0.0, 0.65),
    "沙漠之鹰 | 纵横波涛": (0.0, 1.0),
}

# 中文档位 -> 英文磨损名
TIER_EN_MAP = {
    "崭新出厂 (FN)": "Factory New",
    "略有磨损 (MW)": "Minimal Wear",
    "久经沙场 (FT)": "Field-Tested",
    "破损不堪 (WW)": "Well-Worn",
    "战痕累累 (BS)": "Battle-Scarred",
}

# ================== 刀固定磨损区间 + 各外观分档 ==================
KNIFE_MIN = 0.00
KNIFE_MAX = 1.00

KNIFE_TIER = {
    "崭新出厂 (FN)": (0.00, 0.07),
    "略有磨损 (MW)": (0.07, 0.15),
    "久经沙场 (FT)": (0.15, 0.38),
    "破损不堪 (WW)": (0.38, 0.45),
    "战痕累累 (BS)": (0.45, 1.00),
}

# 伽玛多普勒专用区间
GAMMA_TIER = {
    "崭新出厂 (FN)": (0.00, 0.07),
    "略有磨损 (MW)": (0.07, 0.08),
}

# ========== 工具函数：材料磨损 -> 刀磨损 ==========
def mat_float_to_knife_float(material_name: str, mat_float: float):
    if material_name not in WEAR_RANGE:
        return None
    m_min, m_max = WEAR_RANGE[material_name]
    if m_max <= m_min:
        return None

    mf = max(m_min, min(m_max, mat_float))
    mf = max(0.0, min(1.0, mf))
    return round(mf, 6)


def classify_knife_tier(knife_float: float):
    for tier_name, (lo, hi) in KNIFE_TIER.items():
        if lo <= knife_float <= hi:
            return tier_name
    return None


def calc_max_material_float_for_knife_tier(
    material_name: str,
    target_knife_max: float,
    gamma_mode: bool = False,
):
    """
    给定：材料枪 + 想要的刀成色的上限
    返回：这把材料枪最高能用多少磨损（考虑成品刀区间）
    """
    if material_name not in WEAR_RANGE:
        return None

    mat_min, mat_max = WEAR_RANGE[material_name]

    if gamma_mode:
        out_min, out_max = 0.0, 0.08
    else:
        out_min, out_max = KNIFE_MIN, KNIFE_MAX

    if out_max <= out_min:
        return None

    ratio = (target_knife_max - out_min) / (out_max - out_min)
    if ratio < 0:
        return None
    ratio = min(ratio, 1.0)

    mat_float = mat_min + ratio * (mat_max - mat_min)
    return min(mat_float, mat_max)


def build_market_hash(ch_name: str, tier_name_cn: str | None):
    """
    中文名 + 磨损档位 -> marketHashName
    - 伽玛多普勒始终 Factory New
    - 刀用档位，枪 tier_name_cn None 时默认 FT
    """
    base = STEAMDT_NAME_MAP.get(ch_name)
    if not base:
        return None

    # 枪 or 未指定档位 => 默认 Field-Tested
    if tier_name_cn is None:
        return base + " (Field-Tested)"

    # 伽玛多普勒强制 Factory New
    if "Gamma Doppler" in base:
        return base + " (Factory New)"

    tier_en = TIER_EN_MAP[tier_name_cn]
    return base + f" ({tier_en})"


# ================== 文件读写 ==================
def load_data():
    if not DATA_FILE.exists():
        return DEFAULT_KNIVES, DEFAULT_WEAPONS
    with DATA_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data, DEFAULT_WEAPONS
    return data.get("knives", DEFAULT_KNIVES), data.get("weapons", DEFAULT_WEAPONS)


def save_data(knives, weapons):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump({"knives": knives, "weapons": weapons}, f, ensure_ascii=False, indent=2)


# ================== 拉价 ==================
def fetch_lowest_price(market_hash):
    try:
        r = requests.get(
            PRICE_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"marketHashName": market_hash},
            timeout=10,
        )
        data = r.json()
        if not data.get("success"):
            return None
        prices = [p.get("sellPrice") for p in data.get("data", []) if p.get("sellPrice")]
        return min(prices) if prices else None
    except Exception:
        return None


def update_all(items, tier_name_cn: str | None = None):
    """
    批量刷新价格：
    - items 可以是刀或枪
    - tier_name_cn 是刀磨损档位（枪传 None）
    """
    updated = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for i in items:
            mh = build_market_hash(i["name"], tier_name_cn)
            if mh:
                futs[ex.submit(fetch_lowest_price, mh)] = i

        for fut in as_completed(futs):
            item = futs[fut]
            p = fut.result()
            if p:
                item["min_price"] = float(p)
                updated += 1
    return updated


# ================== 页面渲染函数 ==================
def render():
    """
    😈 梦魇 / 激流大行动 炼刀 页面
    只在 main.py 里调用：page_nightmare_riptide.render()
    """

    # 1. 初始化本页面自己的状态（night_ 前缀）
    if "night_knives" not in st.session_state or "night_weapons" not in st.session_state:
        k, w = load_data()
        st.session_state.night_knives = k
        st.session_state.night_weapons = w

    knives = st.session_state.night_knives
    weapons = st.session_state.night_weapons

    # 2. 页面标题
    st.title("🎮 CS2 梦魇 / 激流大行动 炼金收益展示")

    # ================== Sidebar：刀 ==================
    st.sidebar.subheader("🔪 刀操作")
    knife_names = [k["name"] for k in knives]
    sel_knife = st.sidebar.selectbox(
        "选择刀：",
        knife_names,
        key="night_sel_knife"
    )
    cur_knife = next(k for k in knives if k["name"] == sel_knife)

    knife_tier_choice = st.sidebar.selectbox(
        "刀磨损档位（用于拉价和图表）",
        list(KNIFE_TIER.keys()),
        index=2,
        key="night_knife_tier_choice"
    )

    col1, col2 = st.sidebar.columns(2)
    btn_k1 = col1.button("🔪 刷新当前刀", key="night_btn_knife_one")
    btn_k2 = col2.button("🔁 刷新全部刀", key="night_btn_knife_all")

    if btn_k1:
        mh = build_market_hash(cur_knife["name"], knife_tier_choice)
        if mh:
            p = fetch_lowest_price(mh)
            if p:
                cur_knife["min_price"] = float(p)
                st.sidebar.success(f"✅ 刀已更新：{p}")
            else:
                st.sidebar.error("❌ 刀没拉到价格")
        else:
            st.sidebar.error("❌ 没配置映射")

    if btn_k2:
        with st.spinner("⚙️ 正在刷新所有刀..."):
            n = update_all(knives, knife_tier_choice)
        st.sidebar.success(f"✅ 已刷新 {n} 把刀")

    st.sidebar.markdown(f"当前刀价：**{cur_knife['min_price']:.2f}** 元")

    # ================== Sidebar：枪 ==================
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔫 枪操作")

    weapon_names = [w["name"] for w in weapons]
    sel_weapon = st.sidebar.selectbox(
        "选择枪：",
        weapon_names,
        key="night_sel_weapon"
    )
    cur_weapon = next(w for w in weapons if w["name"] == sel_weapon)

    weapon_tier_choice = st.sidebar.selectbox(
        "枪磨损档位（用于拉价和图表）",
        list(TIER_EN_MAP.keys()),
        index=2,
        key="night_weapon_tier_choice"
    )

    col3, col4 = st.sidebar.columns(2)
    btn_w1 = col3.button("🔫 刷新当前枪", key="night_btn_weapon_one")
    btn_w2 = col4.button("💥 刷新全部枪", key="night_btn_weapon_all")

    if btn_w1:
        mh = build_market_hash(cur_weapon["name"], weapon_tier_choice)
        if mh:
            p = fetch_lowest_price(mh)
            if p:
                cur_weapon["min_price"] = float(p)
                st.sidebar.success("✅ 当前这把枪已更新")
            else:
                st.sidebar.error("❌ 枪没拉到价格")
        else:
            st.sidebar.error("❌ 这把枪没配置映射")

    if btn_w2:
        with st.spinner("⚙️ 正在刷新所有枪..."):
            n = update_all(weapons, weapon_tier_choice)
        st.sidebar.success(f"✅ 已刷新 {n} 把枪")

    st.sidebar.markdown(f"当前枪价：**{cur_weapon['min_price']:.2f}** 元")

    # 状态更新后保存
    save_data(knives, weapons)

    # ================== 主区：反推材料最大磨损 ==================
    st.subheader("🧮 想要这种刀外观，我的材料枪最多能用多少磨损？")

    gamma_mode = st.checkbox(
        "切换为伽玛多普勒模式（只算 FN / MW）",
        value=False,
        key="night_gamma_mode"
    )

    col_a, col_b = st.columns(2)
    with col_a:
        sel_mat = st.selectbox(
            "选择材料枪：",
            list(WEAR_RANGE.keys()),
            key="night_mat_for_inverse"
        )

    with col_b:
        if gamma_mode:
            sel_tier = st.selectbox(
                "想要的伽玛外观：",
                list(GAMMA_TIER.keys()),
                key="night_gamma_tier"
            )
            tier_min, tier_max = GAMMA_TIER[sel_tier]
        else:
            sel_tier = st.selectbox(
                "想要的刀外观：",
                list(KNIFE_TIER.keys()),
                key="night_knife_target_tier"
            )
            tier_min, tier_max = KNIFE_TIER[sel_tier]

    if st.button("计算最大可用材料磨损", key="night_btn_calc_inverse"):
        res = calc_max_material_float_for_knife_tier(sel_mat, tier_max, gamma_mode=gamma_mode)
        if res is None:
            st.error("无法计算，请检查区间。")
        else:
            target_name = "伽玛多普勒" if gamma_mode else "这把刀"
            st.success(
                f"要合出 **{sel_tier}** 的{target_name}，"
                f"{sel_mat} 的磨损应 ≤ **{res:.6f}**"
            )
            st.caption("建议再多留 0.001~0.003 安全余量。")

    # ================== 主区：刀价格图表 ==================
    st.subheader(f"📊 刀价格展示图（当前档位：{knife_tier_choice}）")

    k_names = [k["name"] for k in knives]
    k_prices = [k["min_price"] for k in knives]
    avg_knife_price = sum(k_prices) / len(k_prices) if k_prices else 0

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(k_names, k_prices)

    ax.set_xticks(range(len(k_names)))
    ax.set_xticklabels(k_names, rotation=45, ha="right")
    ax.set_ylabel("价格 (¥)")
    ax.set_title(f"刀价格展示 - {knife_tier_choice}")

    for i, v in enumerate(k_prices):
        ax.text(i, v, f"{v:.0f}", ha="center", va="bottom", fontsize=8)

    ax.axhline(avg_knife_price, linestyle="--", linewidth=1)
    ax.text(
        len(k_names) - 0.5,
        avg_knife_price,
        f"平均价：{avg_knife_price:.1f}",
        ha="right",
        va="bottom",
        fontsize=8,
    )

    st.pyplot(fig)

    # ================== 主区：枪价格图表 ==================
    st.subheader("📊 炼金红皮价格展示图")

    w_names = [w["name"] for w in weapons]
    w_prices = [w["min_price"] for w in weapons]
    avg_knife_div_5 = avg_knife_price / 5 if avg_knife_price else 0

    combined = list(zip(w_names, w_prices))
    combined.sort(key=lambda x: x[1])
    sorted_names = [c[0] for c in combined]
    sorted_prices = [c[1] for c in combined]

    fig2, ax2 = plt.subplots(figsize=(6, 3))
    x = range(len(sorted_names))
    ax2.bar(x, sorted_prices)

    ax2.set_xticks(x)
    ax2.set_xticklabels(sorted_names, rotation=30, ha="right")
    ax2.set_ylabel("价格 (¥)")
    ax2.set_title("枪械价格展示")

    for i, v in enumerate(sorted_prices):
        ax2.text(i, v, f"{v:.0f}", ha="center", va="bottom", fontsize=8)

    ax2.axhline(avg_knife_div_5, linestyle="--", linewidth=1)
    ax2.text(
        len(sorted_names) - 0.2,
        avg_knife_div_5,
        f"炼刀平均价格：{avg_knife_div_5:.1f}",
        ha="right",
        va="bottom",
        fontsize=8,
    )

    st.pyplot(fig2)

    # ================== 主区：表格 ==================
    st.subheader("🔪 刀价格表")
    st.dataframe(
        [{"刀": k["name"], "最低价": k["min_price"]} for k in knives],
        use_container_width=True,
    )

    st.subheader("🔫 炼金红皮价格表")
    st.dataframe(
        [{"枪": w["name"], "最低价": w["min_price"]} for w in weapons],
        use_container_width=True,
    )


