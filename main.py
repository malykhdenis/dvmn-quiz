import json
import os


if __name__ == '__main__':
    for file in os.scandir('quiz-questions/'):
        with open(file.path, "r", encoding='KOI8-R') as my_file:
            file_contents = my_file.read()
        main_list = file_contents.split('\n\n')
        result = dict()
        i = 0
        while i < len(main_list) - 1:
            if 'Вопрос' in main_list[i]:
                try:
                    result[
                        main_list[i].split(':\n')[1]
                    ] = main_list[i + 1].split(':\n')[1]
                    json_1 = json.dumps(result, indent=4, ensure_ascii=False)
                    print(json_1)
                    i += 2
                    continue
                except IndexError:
                    print(file.path, i)
            i += 1
        with open("questions.json", "w") as outfile:
            json.dump(result, outfile, indent=4)
