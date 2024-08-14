# 1 скачиваем с ютубе
import pytube
link = "ссылка на видео с Youtube"
yt = pytube. YouTube(link)
stream = yt. streams.first()
stream. download()

#небольшое улучшение верхнего кода
# так можно выбрать качество
stream = yt.streams.filter(res="720p").first()


# 2 еще улучшение скачиваем в самом высоком качестве
from pytube import YouTube

youtube_video_url = input('Вставте ссылку: ')
try:
    yt_obj = YouTube(youtube_video_url)
    video_name = yt_obj.title
    print(f'Сейчас скачается видео "{video_name}".')
    filters = yt_obj.streams.filter (progressive=True, file_extension='mp4')
# скачиваем в самом высоком качестве
    filters.get_highest_resolution().download()
    print(f'Видео "{yt_obj.title}" успешно скачалось.')
except Exception as e:
    print(e)


# 3 обрезаем видео
from pytube import YouTube
from moviepy.editor import VideoFileClip

url = input('Вставте ссылку: ')
# Скачиваем видео
yt = YouTube(url)
video = yt.streams.first()
video.download("скаченное_видео.mp4")
# Открываем видеофайл
clip = VideoFileClip("скаченное_видео.mp4")
# Вырезаем 1 минуту из видео
start_time = 10
end_time = start_time + 60
new_clip = clip.subclip(start_time, end_time)
# Сохраняем новое видео
new_clip.write_videofile("новое_видео.mp4")


# 4 вырезаем звук из видео
from pytube import YouTube
video_url = input('Вставте ссылку: ')
yt = YouTube(video_url)
stream = yt.streams.get_audio_only()
stream.download()

