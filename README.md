# Japanese Vocabulary Quiz

A terminal-based Japanese vocabulary quiz for Korean speakers, organized by JLPT proficiency levels. Built entirely with Python's standard library — no pip, no dependencies, no setup.

---

## Why This Exists

Learning Japanese vocabulary without a drill tool means either buying an app or staring at a spreadsheet. This script turns a plain CSV into an interactive quiz loop in ~40 lines of Python. When you get something wrong, you get tested on it again immediately — the most effective moment for correction is right after failure, not the next day.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3 | Ships on every machine, no install needed |
| CSV parsing | `csv.DictReader` | Header-aware parsing in one line, no third-party lib |
| Randomization | `random.shuffle` | In-place shuffle keeps memory low; no copy |
| Timestamps | `datetime` | Score logs are human-readable without any formatting lib |

**Zero external dependencies.** `requirements.txt` would be an empty file.

---

## Getting Started

```bash
# Clone
git clone https://github.com/zaqxsw108091/japanese-quiz.git
cd japanese-quiz

# Run
python quiz.py
```

You will see:

```
레벨 선택 (N5/N4/N3):
```

Type one of `N5`, `N4`, or `N3` and press Enter.

---

## Features

### JLPT Level Selection
Choose your difficulty on launch:

| Level | Description | Word count (current) |
|---|---|---|
| N5 | Beginner — everyday nouns, basic verbs, food, nature | ~90 words |
| N4 | Elementary — transport, places, household, hobbies | ~100 words |
| N3 | Intermediate — economy, society, business, tech | ~120 words |

### Shuffled Questions
Every session draws from the full word pool for your level and presents them in random order. Same words, different experience each time.

### Wrong-Word Re-quiz
After the main round, any word you answered incorrectly is collected and immediately re-tested. No manual flagging required — getting it wrong is enough.

```
틀린 단어 다시 풀기!
経験 -> 한국어 :
```

### Score Persistence
Results are appended to `scores.txt` with a timestamp, level, and score fraction. The file grows over time, letting you track improvement manually.

```
2026-06-05 16:16 | 레벨: N5 | 점수: 5/5
2026-06-05 16:20 | 레벨: N5 | 점수: 5/5
```

---

## File Structure

```
japanese-quiz/
├── quiz.py       # All application logic (~40 lines)
├── word.csv      # Vocabulary database (level, japanese, korean)
└── scores.txt    # Auto-generated score log (created on first run)
```

---

## Code Walkthrough

### `load_words(filename, level)` — lines 4–11

```python
def load_words(filename, level):
    words = []
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['level'] == level:
                words.append(row)
    return words
```

**What it does:** Reads `word.csv` and returns only the rows matching the requested JLPT level.

**Why `csv.DictReader`:** Each row becomes a `dict` keyed by the CSV header (`level`, `japanese`, `korean`). This means the quiz function can reference `word['japanese']` and `word['korean']` by name rather than by fragile index — `word[1]` would break silently if the column order ever changed.

**Why filter on load rather than storing all words:** The quiz only ever uses one level per session. Loading everything and filtering later would waste memory on larger datasets. Filtering during iteration keeps the footprint minimal.

---

### `save_score(level, score, total)` — lines 12–15

```python
def save_score(level, score, total):
    with open('scores.txt', 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        f.write(f"{now} | 레벨: {level} | 점수: {score}/{total}\n")
```

**What it does:** Appends one line to `scores.txt` every time a quiz round ends.

**Why `'a'` (append) mode:** Opening with `'w'` would erase the entire history on every run. Append mode means the file is a permanent log — open it anytime and see every session you've ever run.

**Why `strftime('%Y-%m-%d %H:%M')`:** ISO-style date format sorts lexicographically, so a simple `sort scores.txt` would put sessions in chronological order without any parsing.

---

### `quiz(words)` — lines 17–31

```python
def quiz(words):
    score = 0
    wrong = []
    random.shuffle(words)
    for word in words:
        answer = input(f"{word['japanese']} -> 한국어 : ")
        if answer == word['korean']:
            print("정답!")
            score += 1
        else:
            print(f"틀림! 정답: {word['korean']}")
            wrong.append(word)
    print(f"\n점수: {score}/{len(words)}")
    save_score(level, score, len(words))
    return wrong
```

**What it does:** Runs an interactive quiz loop over the word list, tracks correct answers, collects wrong answers, saves the score, and returns the wrong words so the caller can re-quiz them.

**Why `random.shuffle(words)` in-place:** `random.sample` would create a new list. `shuffle` mutates the existing list, avoiding an unnecessary allocation. Since the list is already ours after `load_words`, mutation is safe.

**Why return `wrong`:** Returning the wrong-word list rather than handling re-quiz logic inside this function keeps `quiz()` single-purpose. The caller (the main script) decides whether to re-quiz — so `quiz()` can be reused for both the main round and the retry round with the same code path. You can see this in action at line 41: `quiz(wrong)` calls the same function on the filtered list.

---

### Main script — lines 33–41

```python
level = input("레벨 선택 (N5/N4/N3): ")
words = load_words('word.csv', level)
if not words:
    print("해당 레벨 단어 없음")
else:
    wrong = quiz(words)
    if wrong:
        print("\n틀린 단어 다시 풀기!")
        quiz(wrong)
```

**Why check `if not words`:** If the user types `n5` (lowercase) or a typo, `load_words` returns an empty list. Without this guard, `quiz([])` would print `점수: 0/0`, save a meaningless score, and exit — confusing and noisy. The guard gives a clear "no words found" message instead.

**Why not loop the re-quiz:** After one retry pass, the session ends. A second retry pass would require tracking second-round wrong words and risk an infinite loop for words the user genuinely can't answer. The current design keeps the flow predictable: one full pass, one retry, done.

---

## word.csv Format

```csv
level,japanese,korean
N5,犬,개
N4,電車,전철
N3,経験,경험
```

To add vocabulary, append rows following this format. Level must be exactly `N5`, `N4`, or `N3` — the filter is case-sensitive.

---

## Limitations & Possible Extensions

- Answers are matched with `==` (exact string match). `먹다` ≠ `먹다 ` — a trailing space fails. A `.strip()` on the input would fix this.
- `scores.txt` is append-only plain text. For statistics (average score per level, improvement over time), a SQLite database or structured JSON log would be more useful.
- The re-quiz runs only once. Wrapping it in `while wrong:` would drill until the user gets everything right — useful for intensive study sessions.
- No furigana or example sentences. Adding a `reading` column to the CSV and displaying it after a wrong answer would aid memorization.
