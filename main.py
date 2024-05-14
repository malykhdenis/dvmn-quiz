import os


def get_questions(path):
    for file in os.scandir(path):
        with open(file.path, "r", encoding='KOI8-R') as my_file:
            file_contents = my_file.read()
        main_list = file_contents.split('\n\n')
        result = dict()
        i = 0
        while i < len(main_list) - 1:
            if 'Вопрос' in main_list[i]:
                try:
                    question = ' '.join(
                        main_list[i].split(':\n')[1].rstrip('\n').split('\n')
                    )
                    answer = ' '.join(
                        main_list[i + 1].split(':\n')[1].rstrip('\n').split('\n')
                    )
                    result[question] = answer
                    i += 2
                    continue
                except IndexError:
                    print(file.path, i)
            i += 1
    return result


if __name__ == '__main__':
    get_questions('quiz-questions/')
