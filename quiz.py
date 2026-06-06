import csv
import random
from datetime import datetime
def load_words(filename, level) : 
    words = []
    with open(filename, encoding='utf-8') as f : 
        reader = csv. DictReader(f)
        for row in reader : 
            if row['level'] == level : 
                words.append(row)
    return words
def save_score(level, score, total):
    with open('scores.txt', 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        f.write(f"{now} | 레벨: {level} | 점수: {score}/{total}\n")

def quiz(words) : 
    score = 0
    wrong = []
    random.shuffle(words)
    for word in words : 
        answer = input(f"{word['japanese']} -> 한국어 : ")
        if answer == word['korean'] : 
            print("정답!")
            score += 1
        else : 
            print(f"틀림! 정답: {word['korean']}")
            wrong.append(word)
    print(f"\n점수: {score}/{len(words)}")
    save_score(level, score, len(words))
    return wrong

level = input("레벨 선택 (N5/N4/N3): ")
words = load_words('word.csv', level)
if not words : 
    print("해당 레벨 단어 없음")
else : 
     wrong = quiz(words)
     if wrong:
         print("\n틀린 단어 다시 풀기!")
         quiz(wrong)                                