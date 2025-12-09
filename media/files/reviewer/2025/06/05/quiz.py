import string
from typing import List
import random

def load_questions(file_path):
    questions = []
    correct_answers = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if " - " in line:
                line2 = line.split(" - ")
                questions.append(line2[0])
                correct_answers.append(line2[1])
            else:
                print(f"Format noto'g'ri yoki bo'sh satr: {line}")
        return questions, correct_answers

def randomized(questions,answeres):
    uzunlik = (len(questions))
    x = [i for i in range(0,uzunlik)]
    random.shuffle(x)
    r_answeres = [None for i in range(uzunlik)]
    r_questions = [None for i in range(uzunlik)]
    for i in range(uzunlik):
            r_questions[i] = questions[x[i]]
            r_answeres[i] = answeres[x[i]]
    return r_questions, r_answeres

def run_quiz(questions, answers):
    error_quest = []
    error_ans = []
    print("Testni boshlaymiz!!!")
    n = len(questions)
    for i in range(0,n):
        javob = input(f"{questions[i]} = ")
        if javob == answers[i]:
            print("To'g'ri !!!\n")
        else:
            print(f"Xato !!!\nTo'g'ri javob : {answers[i]}\n")
            error_quest.append(questions[i])
            error_ans.append(answers[i])
    return error_quest, error_ans

if __name__ == "__main__":
    # file_path = "D:\\obsidian\\Inter_National\\vocabulary\\Beginner\\Unit-6\\quiz_unit_6.md"
    # file_path = "/mnt/d/repos/obsidian/Inter_National/Elementary/exam/verb1_verb2_verb3.md"
    file_path = "/mnt/d/repos/obsidian/Inter_National/Pre-Intermediate/vocabulary/unit_11.md"
    #file_path = "/mnt/d/obsidian/Inter_National/Beginner/vocabulary/Unit-9/quiz_voc_22_eating_out.md"
    x, y = load_questions(file_path)
    loop = "yes"
    while loop and x:
        xx, yy = randomized(x,y)
        error_quest, error_ans = run_quiz(yy,xx)
        print("\nXato javoblar.")
        for i in range(len(error_quest)):
            print(f"{error_quest[i]} - {error_ans[i]}")
        loop = input("Xato savollarni takrorlashni istaysizmi? : ")
        y = error_quest
        x = error_ans
