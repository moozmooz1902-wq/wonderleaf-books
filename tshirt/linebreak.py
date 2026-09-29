"""Break a slogan into balanced lines.

Slogans run 3 to 15 words. A greedy wrap gives ragged results ("NEVER
UNDERESTIMATE AN OLD / MAN WITH A MOTORBIKE"), so this picks the split that
makes the lines as even as possible, which is what a real slogan tee does.
"""

def _best_split(words, n):
    """Even split into n lines: minimise the spread of line lengths (DP)."""
    m = len(words)
    if n >= m:
        return [[w] for w in words]
    L = [len(w) for w in words]
    pre = [0]
    for x in L: pre.append(pre[-1] + x + 1)
    target = pre[m] / n
    INF = float("inf")
    # cost[i][k] = best cost splitting words[i:] into k lines
    cost = [[INF] * (n + 1) for _ in range(m + 1)]
    cut  = [[0] * (n + 1) for _ in range(m + 1)]
    cost[m][0] = 0
    for i in range(m - 1, -1, -1):
        for k in range(1, n + 1):
            for j in range(i + 1, m + 1):
                if cost[j][k - 1] == INF: continue
                w = pre[j] - pre[i] - 1
                c = (w - target) ** 2 + cost[j][k - 1]
                if c < cost[i][k]:
                    cost[i][k] = c; cut[i][k] = j
    out, i, k = [], 0, n
    while k > 0:
        j = cut[i][k]
        out.append(words[i:j]); i, k = j, k - 1
    return out


def break_lines(slogan, max_lines=5):
    """Choose a line count that suits the length, then split evenly."""
    words = slogan.split()
    m = len(words)
    n = 2 if m <= 4 else 3 if m <= 6 else 4 if m <= 10 else 5
    n = min(n, max_lines, m)
    return [" ".join(g) for g in _best_split(words, n)]


if __name__ == "__main__":
    for s in ["PEACE LOVE MOTOCROSS",
              "THIS IS WHAT AN AWESOME WELDER LOOKS LIKE",
              "NEVER UNDERESTIMATE AN OLD MAN WITH A MOTORBIKE",
              "WEEKEND FORECAST FISHING WITH A CHANCE OF DRINKING",
              "I GOOGLED MY SYMPTOMS AND IT TURNS OUT I JUST NEED MORE PASSION",
              "PREMIUM QUALITY VINTAGE 1949 AGED TO PERFECTION ALL ORIGINAL PARTS LIMITED EDITION 100 GENUINE",
              "LIECHTENSTEINER ON THE BRAIN"]:
        print(f"\n{s}")
        for ln in break_lines(s): print("   ", ln)
