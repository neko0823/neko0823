import streamlit as st
import random
import time
 
st.set_page_config(page_title="四則演算タイムアタッククイズ", page_icon="🧮")
 
 
# ---------------------------------------------------------
# 初期化
# ---------------------------------------------------------
def init_state():
    defaults = {
        "score": 0,
        "total": 0,
        "quiz_started": False,
        "quiz_finished": False,
        "start_time": None,
        "duration": 30,
        "level": "かんたん",
        "current_problem": None,
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
 
 
init_state()
 
 
# ---------------------------------------------------------
# 問題生成ロジック
# ---------------------------------------------------------
def generate_problem(level: str) -> dict:
    op = random.choice(["+", "-", "×", "÷"])
 
    if op == "+":
        if level == "かんたん":
            a, b = random.randint(1, 9), random.randint(1, 9)
        else:
            a, b = random.randint(10, 99), random.randint(10, 99)
        answer = a + b
 
    elif op == "-":
        if level == "かんたん":
            a, b = random.randint(1, 9), random.randint(1, 9)
        else:
            a, b = random.randint(10, 99), random.randint(10, 99)
        if a < b:
            a, b = b, a  # 答えがマイナスにならないようにする
        answer = a - b
 
    elif op == "×":
        if level == "かんたん":
            a, b = random.randint(1, 9), random.randint(1, 9)
        else:
            a, b = random.randint(2, 12), random.randint(2, 12)
        answer = a * b
 
    else:  # 割り算：必ず割り切れる問題にする
        if level == "かんたん":
            b = random.randint(1, 9)
            answer = random.randint(1, 9)
        else:
            b = random.randint(2, 12)
            answer = random.randint(2, 12)
        a = b * answer
 
    return {"a": a, "b": b, "op": op, "answer": answer}
 
 
def new_problem():
    st.session_state.current_problem = generate_problem(st.session_state.level)
 
 
def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.quiz_finished = False
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.history = []
 
 
# ---------------------------------------------------------
# 画面①：スタート画面
# ---------------------------------------------------------
if not st.session_state.quiz_started and not st.session_state.quiz_finished:
    st.title("🧮 四則演算タイムアタッククイズ")
    st.write("制限時間内に、できるだけ多くの問題に正解しよう！")
 
    st.session_state.level = st.radio(
        "難易度を選んでください", ["かんたん", "むずかしい"], horizontal=True
    )
    st.session_state.duration = st.slider(
        "制限時間（秒）", min_value=10, max_value=120, value=30, step=10
    )
 
    if st.button("スタート ▶", type="primary"):
        reset_quiz()
        st.session_state.quiz_started = True
        st.session_state.start_time = time.time()
        new_problem()
        st.rerun()
 
 
# ---------------------------------------------------------
# 画面②：クイズ本編（タイムアタック中）
# ---------------------------------------------------------
elif st.session_state.quiz_started and not st.session_state.quiz_finished:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0.0, st.session_state.duration - elapsed)
 
    if remaining <= 0:
        st.session_state.quiz_finished = True
        st.session_state.quiz_started = False
        st.rerun()
 
    col1, col2 = st.columns(2)
    col1.metric("⏱ 残り時間", f"{remaining:.1f} 秒")
    col2.metric("✅ スコア", f"{st.session_state.score} / {st.session_state.total} 問")
    st.progress(remaining / st.session_state.duration)
 
    problem = st.session_state.current_problem
    st.header(f"{problem['a']}　{problem['op']}　{problem['b']}　=　？")
 
    # フォームごとにキーを変えることで入力欄をリセットする
    with st.form(key=f"form_{st.session_state.total}", clear_on_submit=True):
        user_answer_text = st.text_input(
            "答えを入力してEnter", placeholder="ここに数字を入力"
        )
        submitted = st.form_submit_button("回答する")
 
        if submitted:
            # 空欄・数字以外が入力された場合は無効な回答として扱う
            try:
                user_answer = int(user_answer_text.strip())
                valid_input = True
            except ValueError:
                user_answer = None
                valid_input = False
 
            if not valid_input:
                st.warning("数字を入力してください。")
            else:
                st.session_state.total += 1
                is_correct = user_answer == problem["answer"]
                if is_correct:
                    st.session_state.score += 1
 
                st.session_state.history.append(
                    {
                        "問題": f"{problem['a']} {problem['op']} {problem['b']}",
                        "あなたの回答": user_answer,
                        "正解": problem["answer"],
                        "結果": "⭕" if is_correct else "❌",
                    }
                )
                new_problem()
                st.rerun()
 
    # タイマー表示を更新するための簡易オートリフレッシュ
    time.sleep(0.2)
    st.rerun()
 
 
# ---------------------------------------------------------
# 画面③：結果発表
# ---------------------------------------------------------
else:
    st.title("⏱ タイムアップ！")
    st.subheader(f"結果：{st.session_state.score} / {st.session_state.total} 問 正解")
 
    if st.session_state.total > 0:
        accuracy = st.session_state.score / st.session_state.total * 100
        st.write(f"正答率：**{accuracy:.1f}%**")
 
    if st.session_state.history:
        st.write("### 回答履歴")
        st.dataframe(st.session_state.history, use_container_width=True)
 
    if st.button("🔁 もう一度挑戦する", type="primary"):
        reset_quiz()
        st.rerun()