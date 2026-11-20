"""Лабораторная работа № 6. Алгоритмы сортировки и бинарного поиска.

Вариант А (база) + Вариант Б (исследование).
Запуск:  python main.py
Результаты сохраняются в папку results/ (CSV, Markdown-таблица, график, отчёт по упражнениям).
"""
import csv
import platform
import statistics
import sys
from datetime import date
from pathlib import Path
from random import Random
from time import perf_counter

OUT = Path(__file__).parent / "results"


# ----------------------------------------------------------------------------
# 1. Основные алгоритмы (без sorted(), list.sort() и готовых функций поиска)
# ----------------------------------------------------------------------------
def insertion_sort(values):
    """Возвращает НОВЫЙ список, отсортированный по возрастанию."""
    result = values[:]
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result


def binary_search(sorted_values, target):
    """Итеративный бинарный поиск. Индекс target или -1."""
    left, right = 0, len(sorted_values) - 1
    while left <= right:
        middle = (left + right) // 2
        value = sorted_values[middle]
        if value == target:
            return middle
        if value < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def binary_search_trace(a, target):
    """Бинарный поиск с выводом left / middle / right на каждой итерации."""
    left, right = 0, len(a) - 1
    while left <= right:
        middle = (left + right) // 2
        print(f"    left={left}, middle={middle}, right={right}, value={a[middle]}")
        if a[middle] == target:
            return middle
        if a[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    print(f"    left={left} > right={right}: область поиска пуста")
    return -1


def linear_search(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def lower_bound(a, target):
    """Индекс первого элемента, не меньшего target."""
    left, right = 0, len(a)
    while left < right:
        middle = (left + right) // 2
        if a[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left


def upper_bound(a, target):
    """Индекс первого элемента, строго большего target."""
    left, right = 0, len(a)
    while left < right:
        middle = (left + right) // 2
        if a[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left


# ----------------------------------------------------------------------------
# 2. Контрольные тесты
# ----------------------------------------------------------------------------
def check_algorithms():
    tests = [
        [], [7], [3, 1, 2], [1, 2, 3], [3, 2, 1],
        [5, 1, 5, 2, 5], [-2, 0, -1, 4],
    ]
    for data in tests:
        original = data[:]
        assert insertion_sort(data) == sorted(data), data   # sorted() — только эталон
        assert data == original, "исходный список изменён"

    data = [-10, -3, 0, 4, 4, 9, 20]
    assert binary_search(data, -10) == 0
    assert data[binary_search(data, 4)] == 4
    assert binary_search(data, 20) == 6
    assert binary_search(data, 100) == -1
    assert binary_search([], 1) == -1
    assert binary_search([5], 5) == 0 and binary_search([5], 4) == -1

    a = [1, 2, 2, 2, 5]
    assert lower_bound(a, 2) == 1 and lower_bound(a, 3) == 4 and lower_bound(a, 9) == 5
    assert upper_bound(a, 2) == 4
    print("Контрольные тесты пройдены")


# ----------------------------------------------------------------------------
# 3. Эксперимент
# ----------------------------------------------------------------------------
def make_data(kind, n, rng):
    if kind == "случайный":
        return [rng.randint(-10**6, 10**6) for _ in range(n)]
    if kind == "отсортированный":
        return list(range(n))
    if kind == "обратный":
        return list(range(n, 0, -1))
    if kind == "с повторами":
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


def timed(func, *args):
    start = perf_counter()
    func(*args)
    return (perf_counter() - start) * 1000  # мс


def run_case(kind, n, repeats=3, seed=42):
    rng = Random(seed)
    data = make_data(kind, n, rng)
    ordered = sorted(data)  # эталон для запросов (не измеряется)
    queries = [rng.choice(ordered) for _ in range(1000)]

    def search_all():
        for t in queries:
            binary_search(ordered, t)

    ins, bui, bin_ = [], [], []
    for _ in range(repeats):
        ins.append(timed(insertion_sort, data))
        bui.append(timed(sorted, data))
        bin_.append(timed(search_all))
    assert insertion_sort(data) == ordered
    return ins, bui, bin_


def stat(xs):
    return statistics.mean(xs), (statistics.stdev(xs) if len(xs) > 1 else 0.0)


CASES = [
    ("случайный", 100), ("случайный", 1000), ("случайный", 5000), ("случайный", 10000),
    ("отсортированный", 1000), ("обратный", 1000), ("с повторами", 1000),
    ("отсортированный", 10000), ("обратный", 5000),
]


def benchmark():
    rows = []
    print(f"\n{'N':>6} | {'тип данных':<16} | {'insertion, мс':>16} | {'sorted(), мс':>14} | {'binary 1000, мс':>16}")
    print("-" * 80)
    for kind, n in CASES:
        ins, bui, bs = run_case(kind, n)
        (im, isd), (bm, _), (sm, _) = stat(ins), stat(bui), stat(bs)
        rows.append({
            "N": n, "type": kind,
            "insertion_ms": round(im, 3), "insertion_std": round(isd, 3),
            "insertion_min": round(min(ins), 3), "insertion_max": round(max(ins), 3),
            "sorted_ms": round(bm, 4), "binary_1000_ms": round(sm, 3),
        })
        print(f"{n:>6} | {kind:<16} | {im:>9.3f} ±{isd:>5.2f} | {bm:>14.4f} | {sm:>16.3f}")
    return rows


def search_comparison():
    """Вариант Б: линейный vs бинарный поиск, 1000 одинаковых запросов."""
    rng = Random(42)
    lines = []
    print(f"\n{'N':>8} | {'linear, мс':>12} | {'binary, мс':>12} | {'ускорение':>10}")
    print("-" * 52)
    for n in (100, 1000, 10000, 100000):
        data = list(range(n))
        queries = [rng.randint(0, n - 1) for _ in range(1000)]

        def run(f):
            best = float("inf")
            for _ in range(3):
                s = perf_counter()
                for q in queries:
                    f(data, q)
                best = min(best, (perf_counter() - s) * 1000)
            return best

        lin, bn = run(linear_search), run(binary_search)
        lines.append((n, lin, bn))
        print(f"{n:>8} | {lin:>12.3f} | {bn:>12.3f} | {lin / bn:>9.1f}x")
    return lines


def save_results(rows, cmp_rows):
    OUT.mkdir(exist_ok=True)
    with open(OUT / "results.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
        w.writeheader()
        w.writerows(rows)

    md = [f"Среда: {platform.processor() or platform.machine()}, {platform.system()} {platform.release()}, "
          f"Python {platform.python_version()}, дата {date.today():%d.%m.%Y}. Среднее из 3 запусков.\n",
          "| N | Тип данных | Insertion sort, мс (± std) | sorted(), мс | Binary search 1000 запросов, мс |",
          "|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['N']} | {r['type']} | {r['insertion_ms']} ± {r['insertion_std']} "
                  f"| {r['sorted_ms']} | {r['binary_1000_ms']} |")
    md += ["", "Линейный vs бинарный поиск (1000 запросов):", "",
           "| N | linear, мс | binary, мс | ускорение |", "|---|---|---|---|"]
    for n, lin, bn in cmp_rows:
        md.append(f"| {n} | {lin:.3f} | {bn:.3f} | {lin / bn:.1f}x |")
    (OUT / "results.md").write_text("\n".join(md), encoding="utf-8")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rnd = [r for r in rows if r["type"] == "случайный"]
        ns = [r["N"] for r in rnd]
        ts = [r["insertion_ms"] for r in rnd]
        k = ts[-1] / ns[-1] ** 2
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.plot(ns, ts, "o-", label="insertion sort (измерено)")
        ax.plot(ns, [k * n * n for n in ns], "--", label="c·N² (теория)")
        ax.set_xlabel("N")
        ax.set_ylabel("Время, мс")
        ax.set_title("Сортировка вставками, случайные данные")
        ax.grid(alpha=.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "plot_insertion.png", dpi=150)
        print(f"\nГрафик сохранён: {OUT / 'plot_insertion.png'}")
    except ImportError:
        print("matplotlib не установлен — график пропущен (pip install matplotlib)")


# ----------------------------------------------------------------------------
# 4. Обязательные упражнения 1-7 (вывод в консоль)
# ----------------------------------------------------------------------------
def exercises():
    print("\n=== Упражнение 1. Трассировка сортировки [7, 4, 6, 2, 5] ===")
    a = [7, 4, 6, 2, 5]
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
        print(f"  i={i}, key={key}: префикс {a[:i + 1]}, хвост {a[i + 1:]}")

    print("\n=== Упражнение 2. Инвариант цикла ===")
    print("  Перед итерацией i элементы a[0..i-1] упорядочены. Сдвиг больших элементов вправо\n"
          "  и вставка key в освободившуюся позицию делают упорядоченным a[0..i]; при i=n\n"
          "  весь массив отсортирован.")

    print("\n=== Упражнение 3. Бинарный поиск [2,5,8,11,15,19,23,31] ===")
    arr = [2, 5, 8, 11, 15, 19, 23, 31]
    for t in (19, 20):
        print(f"  target={t}:")
        print(f"  результат: {binary_search_trace(arr, t)}")

    print("\n=== Упражнение 4. Неотсортированный вход ===")
    bad = [5, 1, 4, 2, 3]
    print(f"  binary_search({bad}, 1) = {binary_search(bad, 1)}  (элемент есть на индексе 1!)")
    print("  Причина: middle=2 (4>1) -> правая граница уходит влево, но порядок нарушен,\n"
          "  поэтому вывод «слева все меньше» неверен и элемент отбрасывается.")

    print("\n=== Упражнение 5. lower_bound / upper_bound [1,2,2,2,5,8], target=2 ===")
    b = [1, 2, 2, 2, 5, 8]
    print(f"  lower_bound={lower_bound(b, 2)}, upper_bound={upper_bound(b, 2)}, "
          f"количество вхождений={upper_bound(b, 2) - lower_bound(b, 2)}")

    print("\n=== Упражнение 6. График: см. results/plot_insertion.png ===")

    print("\n=== Упражнение 7. insertion_sort vs sorted() на 20 случайных списках ===")
    rng = Random(7)
    for _ in range(20):
        lst = [rng.randint(-100, 100) for _ in range(rng.randint(0, 60))]
        assert insertion_sort(lst) == sorted(lst)
    print("  20/20 списков совпали с эталоном — assert пройден")

    print("\n=== Вариант Б: трассировка поиска в [3,8,12,17,21,25,30] ===")
    s = [3, 8, 12, 17, 21, 25, 30]
    for t in (21, 20):
        print(f"  target={t}:")
        print(f"  результат: {binary_search_trace(s, t)}")


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}, {platform.system()} {platform.release()}")
    check_algorithms()
    exercises()
    rows = benchmark()
    cmp_rows = search_comparison()
    save_results(rows, cmp_rows)
    print(f"\nТаблицы для отчёта: {OUT / 'results.md'}, {OUT / 'results.csv'}")
    print("Готово.")
