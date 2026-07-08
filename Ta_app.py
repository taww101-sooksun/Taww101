import streamlit as st
from math import floor

GOLDEN = 1.61803398875


# ===============================
# สร้างลำดับ
# ===============================
def build_sequence(start, count=15):
    seq = [start, start]

    while len(seq) < count:
        seq.append(seq[-1] + seq[-2])

    return seq


# ===============================
# หา Golden Ratio
# ===============================
def best_ratio(seq):

    best = None

    for i in range(1, len(seq)):

        if seq[i - 1] == 0:
            continue

        ratio = seq[i] / seq[i - 1]
        diff = abs(ratio - GOLDEN)

        if best is None or diff < best["diff"]:
            best = {
                "before": seq[i - 1],
                "after": seq[i],
                "ratio": ratio,
                "diff": diff,
            }

    return best


# ===============================
# Cycle
# ===============================
def cycle(value, cycle_length):

    remain = value % cycle_length

    if remain == 0:
        remain = cycle_length

    rounds = floor((value - 1) / cycle_length) + 1

    return remain, rounds


# ===============================
# Golden Score
# ===============================
def golden_score(seq):

    best = best_ratio(seq)

    if best is None:
        return 0

    score = max(0, 1 - best["diff"])

    return score


# ===============================
# หน้าเว็บ
# ===============================

st.set_page_config(page_title="Golden Ratio Analyzer", layout="wide")

st.title("✨ Golden Ratio Analyzer")

st.write("วิเคราะห์ลำดับ Fibonacci และ Golden Ratio")


# ===============================
# รับค่า
# ===============================

day = st.number_input("Day", 1, 31, 6)

month = st.number_input("Month", 1, 12, 5)

zodiac = st.number_input("Zodiac", 1, 12, 1)

moon = st.number_input("Moon Age", 1.0, 30.0, 18.0)


systems = {

    "DAY": (day, 7),

    "MONTH": (month, 12),

    "ZODIAC": (zodiac, 12),

    "MOON": (moon, 29.530588)

}


if st.button("วิเคราะห์"):

    total_score = 0

    for name, (start, cycle_length) in systems.items():

        st.header(name)

        seq = build_sequence(start)

        st.write("### Sequence")

        st.write(seq)

        best = best_ratio(seq)

        st.write("### Closest Golden Ratio")

        st.write(
            f'{best["before"]} / {best["after"]}'
        )

        st.write(
            f'Ratio : {best["ratio"]:.10f}'
        )

        st.write(
            f'Difference : {best["diff"]:.10f}'
        )

        score = golden_score(seq)

        total_score += score

        st.success(f"Golden Score : {score:.6f}")

        rows = []

        for n in seq:

            remain, rounds = cycle(n, cycle_length)

            rows.append({

                "Value": round(n, 3),

                "Remain": round(remain, 3),

                "Rounds": rounds

            })

        st.write("### Cycle")

        st.table(rows)

        st.divider()

    st.header("TOTAL GOLDEN SCORE")

    st.success(round(total_score, 6))
