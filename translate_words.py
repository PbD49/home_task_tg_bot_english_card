from googletrans import Translator


def translate_text_rus_to_eng(text):
    """
    Переводит текст с русского на английский.

    :param text: Текст для перевода.
    :return: Переведенный текст.
    """
    translator = Translator()
    translated_text = translator.translate(text, src='ru', dest='en')
    return translated_text.text


def translate_text_eng_to_rus(text):
    """
    Переводит текст с английского на русский.

    :param text: Текст для перевода.
    :return: Переведенный текст.
    """
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest='ru')
    return translated_text.text
