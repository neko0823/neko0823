"""
たんごたんけん - きょうか神経衰弱ゲーム (Streamlit版)

実行方法:
    pip install streamlit
    streamlit run streamlit_word_memory_game_v2.py
"""

import random
import time

import streamlit as st

# ----------------------------------------------------------------
# 教科ごとのペアデータ
# ----------------------------------------------------------------
SUBJECTS = {
    "国語": {
        "icon": "📖",
        "tag_a": "漢字",
        "tag_b": "よみ",
        "pool": [
            ("図書館", "としょかん"), ("特別", "とくべつ"), ("反対", "はんたい"),
            ("去年", "きょねん"), ("以外", "いがい"), ("世界", "せかい"),
            ("発表", "はっぴょう"), ("教室", "きょうしつ"), ("委員会", "いいんかい"),
            ("運動会", "うんどうかい"), ("宿題", "しゅくだい"), ("給食", "きゅうしょく"),
            ("卒業", "そつぎょう"), ("予定", "よてい"), ("経験", "けいけん"),
            ("未来", "みらい"), ("想像", "そうぞう"), ("説明", "せつめい"),
            ("材料", "ざいりょう"), ("相談", "そうだん"),
        ],
    },
    "数学": {
        "icon": "➗",
        "tag_a": "しき",
        "tag_b": "こたえ",
        "pool": [
            ("7×8", "56"), ("9×6", "54"), ("12+15", "27"), ("100-37", "63"),
            ("144÷12", "12"), ("8×8", "64"), ("15×3", "45"), ("25×4", "100"),
            ("81÷9", "9"), ("6×7", "42"), ("13+28", "41"), ("9×9", "81"),
            ("13×6", "78"), ("14×5", "70"), ("200-85", "115"), ("11×11", "121"),
            ("8×9", "72"), ("18×2", "36"), ("90÷3", "30"), ("33+19", "52"),
        ],
    },
    "理科": {
        "icon": "🔬",
        "tag_a": "元素記号",
        "tag_b": "元素名",
        "pool": [
            ("H", "水素"), ("He", "ヘリウム"), ("O", "酸素"), ("C", "炭素"),
            ("N", "窒素"), ("Na", "ナトリウム"), ("Cl", "塩素"), ("Fe", "鉄"),
            ("Cu", "銅"), ("Ag", "銀"), ("Au", "金"), ("Ca", "カルシウム"),
            ("K", "カリウム"), ("Mg", "マグネシウム"), ("Zn", "亜鉛"),
            ("Al", "アルミニウム"), ("S", "硫黄"), ("P", "リン"),
            ("Ne", "ネオン"), ("Si", "ケイ素"),
        ],
    },
    "社会": {
        "icon": "🌏",
        "tag_a": "都道府県",
        "tag_b": "県庁所在地",
        "pool": [
            ("北海道", "札幌"), ("岩手県", "盛岡"), ("宮城県", "仙台"),
            ("茨城県", "水戸"), ("栃木県", "宇都宮"), ("群馬県", "前橋"),
            ("埼玉県", "さいたま"), ("神奈川県", "横浜"), ("山梨県", "甲府"),
            ("石川県", "金沢"), ("愛知県", "名古屋"), ("三重県", "津"),
            ("滋賀県", "大津"), ("兵庫県", "神戸"), ("島根県", "松江"),
            ("香川県", "高松"), ("愛媛県", "松山"), ("沖縄県", "那覇"),
        ],
    },
    "英語": {
        "icon": "🔤",
        "tag_a": "English",
        "tag_b": "日本語",
        "pool": [
            ("apple", "りんご"), ("dog", "いぬ"), ("cat", "ねこ"), ("book", "ほん"),
            ("water", "みず"), ("school", "がっこう"), ("friend", "ともだち"),
            ("morning", "あさ"), ("night", "よる"), ("family", "かぞく"),
            ("happy", "うれしい"), ("run", "はしる"), ("eat", "たべる"),
            ("sleep", "ねる"), ("big", "おおきい"), ("small", "ちいさい"),
            ("red", "あか"), ("blue", "あお"), ("mountain", "やま"), ("river", "かわ"),
            ("sea", "うみ"), ("sky", "そら"), ("rain", "あめ"), ("snow", "ゆき"),
            ("flower", "はな"), ("tree", "き"), ("bird", "とり"), ("fish", "さかな"),
            ("sun", "たいよう"), ("moon", "つき"),
        ],
    },
}

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
    .subject-btn button {
        height: 100px;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------
# ゲーム状態の初期化
# ----------------------------------------------------------------
def new_game(subject):
    pool = SUBJECTS[subject]["pool"]
    pair_count = min(8, len(pool))
    chosen = random.sample(pool, pair_count)

    cards = []
    for pair_id, (a, b) in enumerate(chosen):
        cards.append({"pair_id": pair_id, "type": "a", "text": a})
        cards.append({"pair_id": pair_id, "type": "b", "text": b})
    random.shuffle(cards)

    st.session_state.subject = subject
    st.session_state.pair_count = pair_count
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

        if st.session_state.matched_pairs == st.session_state.pair_count:
            st.session_state.end_time = time.time()
    else:
        st.session_state.message = "もう一度チャレンジ！"
        st.session_state.pending_hide = [first_index, index]


# ----------------------------------------------------------------
# ホーム画面
# ----------------------------------------------------------------
def render_home():
    st.title("🃏 たんごたんけん")
    st.subheader("きょうかをえらんでね")
    st.caption("好きな教科を選んで、神経衰弱ゲームで楽しく学習しよう！")
    st.write("")

    names = list(SUBJECTS.keys())
    cols = st.columns(3)
    for i, name in enumerate(names):
        icon = SUBJECTS[name]["icon"]
        with cols[i % 3]:
            st.markdown('<div class="subject-btn">', unsafe_allow_html=True)
            if st.button(f"{icon}\n{name}", key=f"subject_{name}", use_container_width=True):
                new_game(name)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------
# ゲーム画面
# ----------------------------------------------------------------
def render_game():
    subject = st.session_state.subject
    info = SUBJECTS[subject]
    pair_count = st.session_state.pair_count

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.title(f"{info['icon']} {subject} 神経衰弱")
    with top_right:
        st.write("")
        if st.button("🏠 ホームに戻る", use_container_width=True):
            go_home()
            st.rerun()

    st.caption(f"{info['tag_a']} と {info['tag_b']} のペアを見つけよう")

    if st.session_state.end_time:
        elapsed = st.session_state.end_time - st.session_state.start_time
    elif st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
    else:
        elapsed = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ペア", f"{st.session_state.matched_pairs}/{pair_count}")
    col2.metric("てすう", st.session_state.moves)
    col3.metric("じかん", f"{int(elapsed)}秒")
    if col4.button("🔄 新しいゲーム", use_container_width=True):
        new_game(subject)
        st.rerun()

    if st.session_state.message:
        st.info(st.session_state.message)

    st.divider()

    if st.session_state.matched_pairs == pair_count:
        total_time = st.session_state.end_time - st.session_state.start_time
        st.success(
            f"クリア！🎉　てすう: {st.session_state.moves}　"
            f"じかん: {total_time:.1f}秒"
        )
        b1, b2 = st.columns(2)
        if b1.button("もう一度あそぶ", use_container_width=True):
            new_game(subject)
            st.rerun()
        if b2.button("他の教科をえらぶ", use_container_width=True):
            go_home()
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
                tag = info["tag_a"] if card["type"] == "a" else info["tag_b"]
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
        "遊び方：カードをクリックして2枚めくり、内容が合っていればペア成立です。"
        f"{pair_count}ペア全部そろえたらクリア！「新しいゲーム」で同じ教科のまま出題し直せます。"
    )


# ----------------------------------------------------------------
# 画面切り替え
# ----------------------------------------------------------------
if st.session_state.screen == "home":
    render_home()
else:
    render_game()