from django.test import TestCase

from posts.models import Post

Post


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len('yatube'), 6)

    # def test_show_msg(self):
    #     # действительно ли первый аргумент — True?
    #     self.assertTrue(False, msg="Важная проверка на истинность")


codes_ru = {
    "А": ".-",
    "Б": "-...",
    "В": ".--",
    "Г": "--.",
    "Д": "-..",
    "Е": ".",
    "Ж": "...-",
    "З": "--..",
    "И": "..",
    "Й": ".---",
    "К": "-.-",
    "Л": ".-..",
    "М": "--",
    "Н": "-.",
    "О": "---",
    "П": ".--.",
    "Р": ".-.",
    "С": "...",
    "Т": "-",
    "У": "..-",
    "Ф": "..-.",
    "Х": "....",
    "Ц": "-.-.",
    "Ч": "---.",
    "Ш": "----",
    "Щ": "--.-",
    "Ъ": "--.--",
    "Ы": "-.--",
    "Ь": "-..-",
    "Э": "..-..",
    "Ю": "..--",
    "Я": ".-.-",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ".": "......",
    ",": ".-.-.-",
    ":": "---...",
    ";": "-.-.-.",
    "(": "-.--.-",
    ")": "-.--.-",
    "'": ".----.",
    '"': ".-..-.",
    "-": "-....-",
    "/": "-..-.",
    "?": "..--..",
    "!": "--..--",
    "@": ".--.-.",
    "=": "-...-",
    " ": " ",
}

codes_en = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ", ": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
}


def text2morse(msg, lang="ru"):
    # Проверка доступных языков
    if lang not in ("en", "ru"):
        raise ValueError("Language is not supported")
    if lang == "ru":
        codes = codes_ru
    elif lang == "en":
        codes = codes_en
    # Проверка типа входящего сообщения
    if not isinstance(msg, str):
        raise TypeError("Wrong msg type")
    # Проверка разрешенных символов
    for char in set(msg.upper()):
        if char not in codes.keys():
            raise ValueError(
                f"Out of allowed character set: {str(list(codes.keys()))}")
        return " ".join([codes[i] for i in msg.upper()])


# протестируйте работу text2morse()

class TestMorse(TestCase):
    def test_str(self):
        # Проверьте правильность перевода в морзянку строк 'Hello' и 'Привет'
        self.assertEqual(text2morse('Hello', 'en'), '.... . .-.. .-.. ---')
        self.assertEqual(text2morse('Привет', 'ru'), '.--. .-. .. .-- . -')

    def test_wrong_lang(self):
        # Проверьте, порождаются ли исключения, если в аргументе неправильно указан язык для строки
        with self.assertRaises(ValueError):
            text2morse('Hello', 'pl')

    def test_instance(self):
        with self.assertRaises(TypeError):
            text2morse(1234, 'ru')

    text = "Привет!"
    converted = text2morse(text)
    print(f"Ваш текст азбукой Морзе будет: {converted}")
