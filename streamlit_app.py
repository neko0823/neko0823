"""
たんごたんけん - 英単語神経衰弱ゲーム (Streamlit版)

実行方法:
    pip install streamlit
    streamlit run streamlit_word_memory_game.py
"""

import random
import time

import streamlit as st

# ----------------------------------------------------------------
# 単語プール（英語⇔日本語）
# ----------------------------------------------------------------
WORD_POOL = [
    ("apple", "りんご"), ("dog", "いぬ"), ("cat", "ねこ"), ("book", "ほん"),
    ("water", "みず"), ("school", "がっこう"), ("friend", "ともだち"),
    ("morning", "あさ"), ("night", "よる"), ("family", "かぞく"),
    ("happy", "うれしい"), ("run", "はしる"), ("eat", "たべる"),
    ("sleep", "ねる"), ("big", "おおきい"), ("small", "ちいさい"),
    ("red", "あか"), ("blue", "あお"), ("mountain", "やま"), ("river", "かわ"),
    ("sea", "うみ"), ("sky", "そら"), ("rain", "あめ"), ("snow", "ゆき"),
    ("flower", "はな"), ("tree", "き"), ("bird", "とり"), ("fish", "さかな"),
    ("sun", "たいよう"), ("moon", "つき"),
]

PAIR_COUNT = 8
GRID_COLS = 4

st.set_page_config(page_title="たんごたんけん", page_icon="🃏", layout="centered")

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
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# ゲーム状態の初期化
# ----------------------------------------------------------------
def new_game():
    chosen = random.sample(WORD_POOL, PAIR_COUNT)
    cards = []
    for pair_id, (en, ja) in enumerate(chosen):
        cards.append({"pair_id": pair_id, "type": "en", "text": en})
        cards.append({"pair_id": pair_id, "type": "ja", "text": ja})
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


if "cards" not in st.session_state:
    new_game()


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
# 画面表示
# ----------------------------------------------------------------
st.title("🃏 たんごたんけん")
st.caption("英単語と日本語のペアを見つけよう（神経衰弱ゲーム）")

# --- ステータス表示 ---
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

# --- クリア表示 ---
if st.session_state.matched_pairs == PAIR_COUNT:
    total_time = st.session_state.end_time - st.session_state.start_time
    st.success(
        f"クリア！🎉　てすう: {st.session_state.moves}　"
        f"じかん: {total_time:.1f}秒"
    )
    if st.button("もう一度あそぶ", use_container_width=True):
        new_game()
        st.rerun()

# --- カードグリッド（4x4） ---
cards = st.session_state.cards
for row in range(GRID_COLS):
    cols = st.columns(GRID_COLS)
    for col_idx in range(GRID_COLS):
        index = row * GRID_COLS + col_idx
        card = cards[index]
        cell = cols[col_idx]

        if st.session_state.matched[index]:
            label = f"✅\n{card['text']}"
        elif st.session_state.revealed[index]:
            tag = "EN" if card["type"] == "en" else "JA"
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
    "遊び方：カードをクリックして2枚めくり、英語と日本語の意味が合っていればペア成立です。"
    "8ペア全部そろえたらクリア！「新しいゲーム」でいつでも単語を入れ替えられます。"
)