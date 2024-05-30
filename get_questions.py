import os


def get_questions(path):
    for file in os.scandir(path):
        with open(file.path, "r", encoding='KOI8-R') as file:
            file_contents = file.read()
        main_list = file_contents.split('\n\n')
        result = dict()
        i = 0
        while i < len(main_list) - 1:
            if main_list[i].startswith('Вопрос'):
                try:
                    question = ' '.join(
                        main_list[i].split(':\n')[1].rstrip('\n').split('\n')
                    )
                    result[question] = dict(
                        answer=None,
                        smart_answer=None,
                        comment=None,
                    )
                    answer = ' '.join(
                        main_list[i + 1].split(':\n')[1].rstrip('\n').split('\n')
                    )
                    result[question]['answer'] = answer
                    smart_answer = answer.split('.')[0]
                    result[question]['smart_answer'] = smart_answer
                    if main_list[i + 2].startswith('Комментарий'):
                        comment = ' '.join(
                            main_list[i + 2].split(':\n')[1].rstrip('\n').split('\n')
                        )
                        result[question]['comment'] = comment
                        i += 1
                    i += 2
                    continue
                except IndexError:
                    print(file.path, i)
            i += 1
    return result


if __name__ == '__main__':
    get_questions('quiz-questions/')
