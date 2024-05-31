import os


def get_questions(path):
    for file in os.scandir(path):
        with open(file.path, encoding='KOI8-R') as current_file:
            file_contents = current_file.read()
        paragraphs = file_contents.split('\n\n')
        result = dict()
        for paragraph in paragraphs:
            if paragraph.startswith(('Вопрос', '\nВопрос')):
                question = ' '.join(
                        paragraph.split(':\n')[1].rstrip('\n').split('\n')
                    )
                result[question] = dict(
                    answer=None,
                    short_answer=None,
                )
            if paragraph.startswith('Ответ'):
                answer = ' '.join(
                    paragraph.split(':\n')[1].rstrip('\n').split('\n')
                )
                result[question]['answer'] = answer
                short_answer = answer.split('.')[0]
                result[question]['short_answer'] = short_answer
    return result


if __name__ == '__main__':
    get_questions('quiz-questions/')
