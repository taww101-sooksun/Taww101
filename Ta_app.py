from math import floor

GOLDEN = 1.61803398875


# ----------------------------------
# สร้างลำดับ
# ----------------------------------

def build_sequence(start, count=15):

    seq = [start, start]

    while len(seq) < count:
        seq.append(seq[-1] + seq[-2])

    return seq


# ----------------------------------
# หา ratio ที่ใกล้ 1.618
# ----------------------------------

def best_ratio(seq):

    best = None

    for i in range(1, len(seq)):

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


# ----------------------------------
# วนรอบ
# ----------------------------------

def cycle(value, cycle):

    remain = value % cycle

    if remain == 0:
        remain = cycle

    rounds = floor((value-1)/cycle)+1

    return remain, rounds


# ===========================================
# ทดลอง
# ===========================================

day = 6
month = 5
zodiac = 1
moon = 18

systems = {

    "DAY":(day,7),

    "MONTH":(month,12),

    "ZODIAC":(zodiac,12),

    "MOON":(moon,29.530588)

}

for name,(start,cycle_length) in systems.items():

    print("="*60)

    print(name)

    seq = build_sequence(start)

    print(seq)

    best = best_ratio(seq)

    print()

    print("Closest Ratio")

    print(best["before"],"/",best["after"])

    print(best["ratio"])

    print()

    print("Cycle")

    for n in seq:

        remain,rounds = cycle(n,cycle_length)

        print(

            f"{n:8.3f}"

            f" -> "

            f"{remain:8.3f}"

            f" รอบ {rounds}"

    )
