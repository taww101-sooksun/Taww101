from math import floor


GOLDEN = 1.61803398875


# ===========================================
# สร้างลำดับ Fibonacci แบบเริ่มจากค่า
# ===========================================

def build_sequence(start, count=15):

    seq = [start, start]

    while len(seq) < count:
        seq.append(seq[-1] + seq[-2])

    return seq



# ===========================================
# หาอัตราส่วนที่ใกล้ Golden Ratio ที่สุด
# ===========================================

def best_ratio(seq):

    best = None

    for i in range(1, len(seq)):

        if seq[i-1] == 0:
            continue

        ratio = seq[i] / seq[i-1]

        diff = abs(ratio - GOLDEN)

        if best is None or diff < best["diff"]:

            best = {
                "index": i,
                "before": seq[i-1],
                "after": seq[i],
                "ratio": ratio,
                "diff": diff
            }

    return best



# ===========================================
# คำนวณรอบ
# ===========================================

def cycle(value, cycle_length):

    remain = value % cycle_length

    if remain == 0:
        remain = cycle_length

    rounds = floor((value - 1) / cycle_length) + 1

    return remain, rounds



# ===========================================
# รวมคะแนน Golden
# ===========================================

def golden_score(seq):

    best = best_ratio(seq)

    if best is None:
        return 0

    score = 1 - best["diff"]

    if score < 0:
        score = 0

    return score



# ===========================================
# ค่าทดลอง
# ===========================================

day = 6
month = 5
zodiac = 1
moon = 18



systems = {

    "DAY": (day, 7),

    "MONTH": (month, 12),

    "ZODIAC": (zodiac, 12),

    "MOON": (moon, 29.530588)

}



# ===========================================
# เริ่มวิเคราะห์
# ===========================================

total_score = 0


for name, (start, cycle_length) in systems.items():

    print("=" * 60)

    print(name)

    print("Start =", start)

    print()


    seq = build_sequence(start)


    print("Sequence")

    print(seq)


    print()


    best = best_ratio(seq)


    print("Closest Golden Ratio")

    print("--------------------")

    print(
        best["before"],
        "/",
        best["after"]
    )

    print(
        "Ratio =",
        best["ratio"]
    )

    print(
        "Difference =",
        best["diff"]
    )


    score = golden_score(seq)

    total_score += score


    print()

    print("Golden Score =", score)


    print()

    print("Cycle")

    print("--------------------")


    for n in seq:

        remain, rounds = cycle(
            n,
            cycle_length
        )

        print(
            f"{n:10.3f}",
            "->",
            f"{remain:10.3f}",
            "รอบ",
            rounds
        )


print()

print("=" * 60)

print("TOTAL GOLDEN SCORE")

print(total_score)

print("=" * 60)
