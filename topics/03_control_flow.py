"""Control flow: conditionals and loops.

Practised combining conditionals and loops to filter and process data.
"""


def grade(score: int) -> str:
    if score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "F"


def main() -> None:
    scores = [45, 72, 63, 88, 51, 39, 67]

    # for loop over a list
    for score in scores:
        print(score, "->", grade(score))

    # while loop
    n = 5
    while n > 0:
        print("countdown", n)
        n -= 1

    # filtering with a loop
    passed = []
    for score in scores:
        if score >= 50:
            passed.append(score)
    print("passed:", passed)

    # range, enumerate, and break/continue
    for i, score in enumerate(scores):
        if score < 50:
            continue          # skip failing scores
        if score >= 85:
            print(f"top score at index {i}: {score}")
            break             # stop at the first very high score

    # for/else: the else runs only if the loop did not break
    for score in scores:
        if score == 100:
            print("perfect score found")
            break
    else:
        print("no perfect score")


if __name__ == "__main__":
    main()
