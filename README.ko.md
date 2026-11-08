# 일본어 단어 퀴즈 (Japanese Vocabulary Quiz)

**English:** [README.md](README.md)

한국어 사용자를 위한 터미널 기반 일본어 단어 퀴즈로, JLPT 급수별로 구성되어 있습니다. 파이썬 표준 라이브러리만으로 만들었습니다 — pip도, 의존성도, 설정도 필요 없습니다.

---

## 만든 이유

단어 연습 도구 없이 일본어 단어를 외우려면 앱을 사거나 스프레드시트를 들여다봐야 합니다. 이 스크립트는 평범한 CSV 파일을 약 40줄의 파이썬으로 대화형 퀴즈로 바꿔 줍니다. 틀리면 바로 그 단어를 다시 풀게 됩니다 — 바로잡기에 가장 좋은 때는 다음 날이 아니라 틀린 직후이기 때문입니다.

---

## 기술 스택

| 구분 | 선택 | 이유 |
|---|---|---|
| 언어 | Python 3 | 어느 컴퓨터에나 있어 설치가 필요 없음 |
| CSV 읽기 | `csv.DictReader` | 헤더를 인식하는 읽기를 한 줄로, 외부 라이브러리 없음 |
| 무작위 섞기 | `random.shuffle` | 리스트를 그 자리에서 섞어 메모리를 적게 씀(복사 없음) |
| 시간 기록 | `datetime` | 별도의 서식 라이브러리 없이 사람이 읽기 쉬운 점수 기록 |

**외부 의존성 0개.** `requirements.txt`를 만든다면 빈 파일이 됩니다.

---

## 시작하기

```bash
# Clone
git clone https://github.com/zaqxsw108091-create/japanese-quiz.git
cd japanese-quiz

# Run
python quiz.py
```

다음과 같은 화면이 나옵니다.

```
레벨 선택 (N5/N4/N3):
```

`N5`, `N4`, `N3` 중 하나를 입력하고 Enter를 누릅니다.

---

## 기능

### JLPT 레벨 선택
실행할 때 난이도를 고릅니다.

| 레벨 | 설명 | 단어 수 (현재) |
|---|---|---|
| N5 | 초급 — 일상 명사, 기본 동사, 음식, 자연 | 75개 |
| N4 | 초중급 — 교통, 장소, 가정, 취미 | 92개 |
| N3 | 중급 — 경제, 사회, 비즈니스, 기술 | 142개 |

### 문제 섞기
매 회차마다 해당 레벨의 단어 전체를 무작위 순서로 냅니다. 단어는 같아도 매번 다르게 풀게 됩니다.

### 틀린 단어 다시 풀기
본 문제가 끝나면 틀린 단어를 모아 바로 다시 냅니다. 따로 표시할 필요 없이, 틀리기만 하면 됩니다.

```
틀린 단어 다시 풀기!
経験 -> 한국어 :
```

### 점수 저장
결과는 시간, 레벨, 점수(맞힌 수/전체)와 함께 `scores.txt`에 덧붙여 기록됩니다. 파일이 계속 쌓이므로 실력이 늘어 가는 것을 직접 확인할 수 있습니다.

> **참고:** 틀린 단어 다시 풀기 회차도 따로 한 줄로 저장되며, 그 점수는 전체 단어 수가 아니라 틀린 단어 수를 기준으로 합니다 (예: `점수: 2/5`).

```
2026-06-05 16:16 | 레벨: N5 | 점수: 5/5
2026-06-05 16:20 | 레벨: N5 | 점수: 5/5
```

---

## 파일 구조

```
japanese-quiz/
├── quiz.py       # All application logic (~40 lines)
├── word.csv      # Vocabulary database (level, japanese, korean)
└── scores.txt    # Auto-generated score log (created on first run)
```

- `quiz.py` — 프로그램 로직 전부 (약 40줄)
- `word.csv` — 단어 데이터 (level, japanese, korean)
- `scores.txt` — 자동으로 만들어지는 점수 기록 (처음 실행할 때 생성)

---

## 코드 설명

### `load_words(filename, level)` — 4~11번째 줄

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

**하는 일:** `word.csv`를 읽어서 요청한 JLPT 레벨에 맞는 줄만 돌려줍니다.

**`csv.DictReader`를 쓰는 이유:** 각 줄이 CSV 헤더(`level`, `japanese`, `korean`)를 키로 하는 `dict`가 됩니다. 그래서 퀴즈 함수에서 `word['japanese']`, `word['korean']`처럼 이름으로 값을 가져올 수 있습니다. `word[1]`처럼 위치 번호로 가져오면 열 순서가 바뀌었을 때 아무 경고 없이 틀린 값을 쓰게 됩니다.

**모든 단어를 저장하지 않고 읽을 때 거르는 이유:** 한 회차에는 한 레벨만 씁니다. 전부 읽은 뒤 나중에 거르면 데이터가 클 때 메모리를 낭비합니다. 읽으면서 거르면 필요한 만큼만 씁니다.

---

### `save_score(level, score, total)` — 12~15번째 줄

```python
def save_score(level, score, total):
    with open('scores.txt', 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        f.write(f"{now} | 레벨: {level} | 점수: {score}/{total}\n")
```

**하는 일:** 퀴즈 회차가 끝날 때마다 `scores.txt`에 한 줄을 덧붙입니다.

**`'a'`(덧붙이기) 모드를 쓰는 이유:** `'w'`로 열면 실행할 때마다 기록이 전부 지워집니다. 덧붙이기 모드에서는 파일이 영구 기록이 되어, 언제 열어 봐도 지금까지의 모든 회차를 볼 수 있습니다.

**`strftime('%Y-%m-%d %H:%M')`을 쓰는 이유:** ISO 방식 날짜는 글자 순서대로 정렬해도 날짜순이 되므로, 따로 해석하지 않고 `sort scores.txt`만 해도 회차가 시간순으로 정렬됩니다.

---

### `quiz(words)` — 17~31번째 줄

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

**하는 일:** 단어 목록으로 대화형 퀴즈를 진행하면서 맞힌 수를 세고, 틀린 단어를 모으고, 점수를 저장한 뒤, 틀린 단어를 돌려줍니다. 그래서 부르는 쪽에서 다시 풀게 할 수 있습니다.

**`random.shuffle(words)`로 그 자리에서 섞는 이유:** `random.sample`은 새 리스트를 만듭니다. `shuffle`은 기존 리스트를 직접 바꾸므로 불필요한 메모리 할당이 없습니다. 이 리스트는 `load_words`가 새로 만든 것이라 바꿔도 안전합니다.

**`wrong`을 돌려주는 이유:** 다시 풀기 로직을 이 함수 안에 넣지 않고 틀린 단어 목록을 돌려주면, `quiz()`는 한 가지 일만 하게 됩니다. 다시 풀지 말지는 부르는 쪽(메인 스크립트)이 정합니다. 그래서 본 회차와 다시 풀기 회차에 `quiz()`를 똑같이 쓸 수 있습니다. 41번째 줄의 `quiz(wrong)`이 같은 함수를 틀린 단어 목록에 다시 부르는 부분입니다.

---

### 메인 스크립트 — 33~41번째 줄

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

**`if not words`를 확인하는 이유:** 사용자가 `n5`(소문자)나 오타를 입력하면 `load_words`가 빈 리스트를 돌려줍니다. 이 확인이 없으면 `quiz([])`가 `점수: 0/0`을 출력하고, 의미 없는 점수를 저장하고 끝나 버려 헷갈리고 기록만 지저분해집니다. 이 확인 덕분에 "해당 레벨 단어 없음"이라는 분명한 메시지가 나옵니다.

**다시 풀기를 반복하지 않는 이유:** 한 번 다시 풀고 나면 회차가 끝납니다. 두 번째 다시 풀기를 하려면 두 번째 회차에서 틀린 단어도 따로 관리해야 하고, 정말 모르는 단어가 있으면 끝없이 반복될 위험이 있습니다. 지금 구조는 흐름이 예측 가능합니다. 한 번 전체를 풀고, 한 번 다시 풀고, 끝.

---

## word.csv 형식

```csv
level,japanese,korean
N5,犬,개
N4,電車,전철
N3,経験,경험
```

단어를 추가하려면 이 형식대로 줄을 덧붙이면 됩니다. 레벨은 정확히 `N5`, `N4`, `N3` 중 하나여야 합니다 — 대소문자를 구분합니다.

---

## 한계와 확장 아이디어

- 답은 `==`(문자열이 완전히 같은지)로 비교합니다. `먹다` ≠ `먹다 ` — 뒤에 공백이 하나 있어도 틀립니다. 입력에 `.strip()`을 붙이면 해결됩니다.
- `scores.txt`는 덧붙이기만 하는 일반 텍스트입니다. 통계(레벨별 평균 점수, 시간에 따른 향상)를 내려면 SQLite 데이터베이스나 구조화된 JSON 기록이 더 유용합니다.
- 다시 풀기는 한 번만 진행됩니다. `while wrong:`으로 감싸면 전부 맞힐 때까지 반복할 수 있어 집중 학습에 유용합니다.
- 후리가나나 예문이 없습니다. CSV에 `reading` 열을 추가하고 틀렸을 때 보여 주면 암기에 도움이 됩니다.
