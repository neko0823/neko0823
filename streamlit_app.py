"""
れきし たんけん - 社会(歴史)神経衰弱ゲーム (Streamlit版)

実行方法:
    pip install streamlit
    streamlit run streamlit_history_memory_game.py
"""

import random
import time

import streamlit as st

# ----------------------------------------------------------------
# 歴史の年号とできごとのペア
# ----------------------------------------------------------------
TAG_A = "年号"
TAG_B = "できごと"

HISTORY_POOL = [
    ("645年", "大化の改新"),
    ("710年", "平城京遷都"),
    ("794年", "平安京遷都"),
    ("1192年", "鎌倉幕府成立"),
    ("1333年", "鎌倉幕府の滅亡"),
    ("1467年", "応仁の乱"),
    ("1543年", "鉄砲伝来"),
    ("1573年", "室町幕府の滅亡"),
    ("1600年", "関ヶ原の戦い"),
    ("1603年", "江戸幕府成立"),
    ("1637年", "島原の乱"),
    ("1853年", "ペリー来航"),
    ("1867年", "大政奉還"),
    ("1868年", "明治維新"),
    ("1889年", "大日本帝国憲法発布"),
    ("1894年", "日清戦争"),
    ("1904年", "日露戦争"),
    ("1923年", "関東大震災"),
    ("1945年", "終戦"),
    ("1964年", "東京オリンピック"),
]

PAIR_COUNT = 8
GRID_COLS = 4

st.set_page_config(page_title="れきしたんけん", page_icon="🏯", layout="centered")

# ----------------------------------------------------------------
# 見た目を少し整えるCSS
# ----------------------------------------------------------------
st.markdown(
    """
    <style>
    div.stButton > button {
        height: 78px;
        width: 100%;
        font-size: 16px;
        font-weight: 700;
        border-radius: 10px;
        white-space: pre-line;
    }
    .start-btn button {
        height: 90px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# ゲーム状態の初期化
# ----------------------------------------------------------------
def new_game():
    chosen = random.sample(HISTORY_POOL, PAIR_COUNT)
    cards = []
    for pair_id, (year, event) in enumerate(chosen):
        cards.append({"pair_id": pair_id, "type": "a", "text": year})
        cards.append({"pair_id": pair_id, "type": "b", "text": event})
    random.shuffle(cards)

    st.session_state.cards = cards
    st.session_state.revealed = [False] * len(cards)
    st.session_state.matched = [False] * len(cards)
    st.session_state.first_index = None
    st.session_state.pending_hide = []
    st.session_state.moves = 0
    st.session_state.matched_pairs = 0
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.message = ""
    st.session_state.screen = "game"


def go_home():
    st.session_state.screen = "home"


if "screen" not in st.session_state:
    st.session_state.screen = "home"


# ----------------------------------------------------------------
# カードクリック時の処理
# ----------------------------------------------------------------
def handle_click(index):
    cards = st.session_state.cards

    # 前回不一致だった2枚をここで裏返す
    if st.session_state.pending_hide:
        for i in st.session_state.pending_hide:
            st.session_state.revealed[i] = False
        st.session_state.pending_hide = []

    if st.session_state.revealed[index] or st.session_state.matched[index]:
        return

    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.session_state.revealed[index] = True

    if st.session_state.first_index is None:
        st.session_state.first_index = index
        st.session_state.message = ""
        return

    first_index = st.session_state.first_index
    st.session_state.first_index = None
    st.session_state.moves += 1

    if cards[first_index]["pair_id"] == cards[index]["pair_id"]:
        st.session_state.matched[first_index] = True
        st.session_state.matched[index] = True
        st.session_state.matched_pairs += 1
        st.session_state.message = "ペア成立！ 🎉"

        if st.session_state.matched_pairs == PAIR_COUNT:
            st.session_state.end_time = time.time()
    else:
        st.session_state.message = "もう一度チャレンジ！"
        st.session_state.pending_hide = [first_index, index]


# ----------------------------------------------------------------
# ホーム画面
# ----------------------------------------------------------------
def render_home():
    st.title("🏯 れきしたんけん")
    st.subheader("社会(歴史)神経衰弱ゲーム")
    st.write(
        f"「{TAG_A}」と「{TAG_B}」のペアを見つけて、日本の歴史を楽しく覚えよう！"
    )
    st.write("")

    st.markdown('<div class="start-btn">', unsafe_allow_html=True)
    if st.button("🎴 スタート", use_container_width=True):
        new_game()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------
# ゲーム画面
# ----------------------------------------------------------------
def render_game():
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.title("🏯 れきしたんけん")
    with top_right:
        st.write("")
        if st.button("🏠 タイトルに戻る", use_container_width=True):
            go_home()
            st.rerun()

    st.caption(f"{TAG_A} と {TAG_B} のペアを見つけよう")

    if st.session_state.end_time:
        elapsed = st.session_state.end_time - st.session_state.start_time
    elif st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
    else:
        elapsed = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ペア", f"{st.session_state.matched_pairs}/{PAIR_COUNT}")
    col2.metric("てすう", st.session_state.moves)
    col3.metric("じかん", f"{int(elapsed)}秒")
    if col4.button("🔄 新しいゲーム", use_container_width=True):
        new_game()
        st.rerun()

    if st.session_state.message:
        st.info(st.session_state.message)

    st.divider()

    if st.session_state.matched_pairs == PAIR_COUNT:
        total_time = st.session_state.end_time - st.session_state.start_time
        st.success(
            f"クリア！🎉　てすう: {st.session_state.moves}　"
            f"じかん: {total_time:.1f}秒"
        )
        if st.button("もう一度あそぶ", use_container_width=True):
            new_game()
            st.rerun()

    # --- カードグリッド ---
    cards = st.session_state.cards
    rows = (len(cards) + GRID_COLS - 1) // GRID_COLS
    for row in range(rows):
        cols = st.columns(GRID_COLS)
        for col_idx in range(GRID_COLS):
            index = row * GRID_COLS + col_idx
            if index >= len(cards):
                continue
            card = cards[index]
            cell = cols[col_idx]

            if st.session_state.matched[index]:
                label = f"✅\n{card['text']}"
            elif st.session_state.revealed[index]:
                tag = TAG_A if card["type"] == "a" else TAG_B
                label = f"[{tag}]\n{card['text']}"
            else:
                label = "❓"

            disabled = st.session_state.revealed[index] or st.session_state.matched[index]

            cell.button(
                label,
                key=f"card_{index}",
                on_click=handle_click,
                args=(index,),
                disabled=disabled,
                use_container_width=True,
            )

    st.divider()
    st.caption(
        "遊び方：カードをクリックして2枚めくり、年号とできごとが合っていればペア成立です。"
        f"{PAIR_COUNT}ペア全部そろえたらクリア！「新しいゲーム」で出題し直せます。"
    )


# ----------------------------------------------------------------
# 画面切り替え
# ----------------------------------------------------------------
if st.session_state.screen == "home":
    render_home()
else:
    render_game()