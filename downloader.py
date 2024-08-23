"""
Модуль с классом для загрузки видео YouTube.
Доступна, как загрузка одного видео, так и
плейлиста. В модуле используются следующие библиотеки:
pip install pytube colorama chime;

colorama используется больше для вывода сообщений
в терминал и особой практической ценности, кроме радости
для глаз, не несет;

chime используется для звукового оповещения после загрузки
плейлиста или при выводе ошибки.
"""

import os

from colorama import Fore
from colorama import init
from pytube import exceptions
from pytube import YouTube
from pytube import Playlist
from pytube.cli import on_progress
import chime

init()


class YtDownload:
    def __init__(self, url, res):
        """
        Инициализируются параметры, переданные в класс.
        Выполняется проверка на переданное значение разрешения.
        Значение по умолчанию не подставляется, если передана
        пустая строка, подставляется именно пустая строка.
        :param url: ссылка на видео или плейлист YouTube.
        :param res: желаемое разрешение видео.
        """
        self.url = url
        if res == '':
            self.res = '720p'
        else:
            self.res = f'{res}p'

    def check_res(self, yt):
        """
        Проверка разрешения введенного пользователем. Если требуемое разрешение недоступно,
        либо отсутствует разрешение для видео по умолчанию, возвращается максимально доступное
        разрешение доступное для данного видео.
        :param yt: экземпляр класса YouTube с параметрами.
        :return: возвращает разрешение видео.
        """
        res_list = []
        check_res = yt.streams.filter(progressive=True)

        for item in check_res:
            res_list.append(str(item).split()[3].replace("res=", '').replace('"', ''))
        if self.res not in res_list:
            print(Fore.YELLOW + f'\nЗапрошенное разрешение недоступно\nБудет загружено: {res_list[-1]}\n')
            return res_list[-1]

        return self.res

    def video_download(self, yt, path_save: str):
        """
        Загружает видео, которое передается в экземпляре класса YouTube с параметрами.
        Также передается путь для загрузки видео, который различается, в случае, если
        загружается плейлист.
        Выводиться в терминал информация о видео.
        :param yt: экземпляр класса YouTube с параметрами.
        :param path_save: путь к папке для загрузки видео.
        """
        res = self.check_res(yt)

        print(Fore.GREEN + f'\nЗагружаю видео\n{"-" * 14}\n')
        print(Fore.YELLOW + f'  Название: "{yt.title}"')
        print(Fore.YELLOW + f'  Автор: "{yt.author}"')
        print(Fore.YELLOW + f'  Размер видео: '
                            f'{get_size(yt.streams.filter(progressive=True, resolution=res).first().filesize)}')
        print(Fore.YELLOW + f'  Качество: {res}\n')
        print(Fore.GREEN + f"{'-' * 14}\n")

        yt.streams.filter(progressive=True, resolution=res).first().download(path_save, f'{rep_symbol(yt.title)}.mp4')
        yt.register_on_progress_callback(on_progress)
        srt_download(yt.captions, path_save, rep_symbol(yt.title))

        print(Fore.BLUE + f'Видео загружено в папку: {os.path.join(path_save, f"{rep_symbol(yt.title)}.mp4")}\n')
        chime.theme('big-sur')
        chime.success()

    def playlist_download(self):
        """
        Загрузка плейлиста с видео. Для каждого видео из списка полученного из плейлиста
        создается экземпляр класса YouTube с параметрами. Он передается в функцию загрузки
        видео, где выполняется его загрузка.
        :return: выход из функции.
        """
        try:
            pl = Playlist(self.url)
            width_name = len(Fore.GREEN + f'Загружаю плейлист: "{pl.title}"')
            print(Fore.GREEN + f'\n{"-" * (width_name - 5)}\nЗагружаю плейлист: "{pl.title}"\n{"-" * (width_name - 5)}')
            for url in pl.video_urls:
                yt = YouTube(url, on_progress_callback=on_progress)
                path_save = os.path.join('video', rep_symbol(yt.author), rep_symbol(pl.title))
                self.video_download(yt, path_save)
            print(Fore.GREEN + f'{"-" * (width_name - 5)}\nПлейлист: "{pl.title}" загружен\n{"-" * (width_name - 5)}\n')
            chime.theme('big-sur')
            chime.success()
        except KeyError:
            print(Fore.RED + 'Неверная ссылка')
            chime.theme('mario')
            chime.success()
            return

    def start(self):
        """
        Выполняется проверка, является ли ссылка валидной для YouTube.
        Определяется тип переданной ссылки (плейлист или видео).
        В зависимости назначения ссылки запускается загрузка или
        плейлиста, или создается экземпляр класса YouTube с параметрами,
        устанавливается путь для загрузки видео, запускается функция
        загрузки видео с переданными параметрами.
        :return: выход из функции.
        """
        if 'youtube.com' not in self.url:
            print(Fore.RED + 'Неверная ссылка')
            chime.theme('mario')
            chime.success()
            return

        if 'playlist' in self.url:
            self.playlist_download()
        else:
            try:
                yt = YouTube(self.url, on_progress_callback=on_progress)
                path_save = os.path.join(os.getcwd(), 'video', f'{rep_symbol(yt.author)}')
                self.video_download(yt, path_save)
            except exceptions.RegexMatchError:
                print(Fore.RED + 'Неверная ссылка')
                chime.theme('mario')
                chime.success()
                return


def srt_download(cap, path_save: str, title: str):
    """
    Получает список доступных субтитров, проверяет, есть ли
    субтитры с требуемым языком. Если есть, загружает.
    Для данной функции требуется замена файла captions.py
    в папке библиотеки pytube. Если не заменить, вызывается
    ошибка парсинга. Проблема давняя, но почему-то официально
    не решенная. Однако, на форумах нашел правильный вариант.
    :param cap: список субтитров из видео.
    :param path_save: путь для загрузки субтитров.
    :param title: название для загружаемых субтитров.
    """
    for item in cap.lang_code_index.keys():
        if item == 'a.en' or item == 'en':
            with open(os.path.join(path_save, f'{rep_symbol(title)}.srt'), 'w', encoding='utf-8') as file:
                file.write(cap[item].generate_srt_captions())


def get_size(bts: int, ending='iB'):
    """
    Получает размера файла. Переводит размер в читаемый формат,
    значение возвращает из функции.
    :param bts: размер файла.
    :param ending: суффикс для возвращаемого значения.
    :return: возвращает размер файла в определенном формате.
    """
    size = 1024
    for item in ["", "K", "M", "G", "T", "P"]:
        if bts < size:
            return f"{bts:.2f} {item}{ending}"
        bts /= size


def rep_symbol(text: str):
    """
    Заменяются символы, которые могут вызвать ошибку при сохранении
    видео или создании папки для него.
    :param text: текст для замены символов.
    :return: возвращает результат после замены символов.
    """
    tex = text.replace("'", "").replace('"', '').replace('|', '_').replace(' | ', '_').replace('/', '_'). \
        replace('\\', '_').replace('*', '_').replace('?', '').replace('<', '').replace('>', '_').replace(':', ''). \
        replace(';', '').replace('.', '').strip()
    return tex


def download(url: str, res: str):
    """
    Создает экземпляр класса YtDownload, в который
    передаются полученные параметры. Вызывается функция
    проверки ссылок и определения типа загружаемого видео.
    :param url: ссылка на видео или на плейлист.
    :param res: желаемое качество видео.
    """
    tube = YtDownload(url=url, res=res)
    tube.start()
