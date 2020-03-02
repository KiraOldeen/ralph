# Руководство по внесению вклада в разработку (rev. 1.4)

- [Создание ишью](#Создание-ишью)
- [Локальная разработка](#Локальная-разработка)
- [Соглашения](#Соглашения)
	- [Работа с ветками](#Работа-с-ветками)
	- [Наименование коммитов](#Наименование-коммитов)

## Создание ишью

Если вы нашли баг, косяк, недоработку, или хотели бы предложить новую функцию, вам нужно открыть ишью. (Вам понадобится аккаунт на Github, если его еще нет, зарегистрируйтесь [здесь](https://github.com/join)). Для создания ишью зайдите на [специальную страницу в репозитории](https://github.com/dadyarri/ralph/issues), ознакомьтесь с существующими ишью, и если похожей на вашу проблему, еще не описано нажмите на кнопку **New**.

По возможности ишью должно быть написано на английском языке, но при отстутвии возможности свободно говорить по-английски, можно все написать на русском (переводчиками пользоваться нежелательно).

Укажите название проблемы/новой функции (её краткое описание в поле *Title*), и максимально подробное описание в поле *Leave a comment*

Вы можете оставить фотографии, скриншоты (для багов это особенно важно), поле комментария поддерживает разметку Markdown. Шпаргалку по Markdown можно изучить [здесь](https://github.com/sandino/Markdown-Cheatsheet)

Описание бага должно содержать шаги для его повторения, чтобы разработчик мог убедиться в наличии бага и провести его поиск в коде.

В ближайшее время разработчик изучит вашу проблему и займется её решением.

## Локальная разработка

Чтобы получить свежую копию репозитория вам нужно форкнуть репозиторий в свой аккаунт на GitHub (используя кнопку Fork), затем уже свою копию репозитория склонировать на рабочую машину

`git clone https://github.com/<ваш_ник>/ralph`

***Важно!*** Делая свои изменения вы должны прислушиваться к соглашениям, перечисленным в разделе [Соглашения](#Соглашения), в противном случае, ваш пул реквест скорее всего, будет отклонён.

Завершив работу над вашими улучшениями нужно выгрузить репозиторий на удаленный сервер

`git push origin master`

Затем перейдя в основной репозиторий нужно открыть пулреквест (запрос на слияние)

Если вы недавно выгрузили свои изменения на Github вы должны увидеть вверху страницы с репозиторием предложение пулреквеста

Нажмите на кнопку *Open pull request*, укажите название и описание пулреквеста и подтвердите создание запроса.

## Соглашения

### Работа с ветками

Изменяя репозиторий, вы не должны работать с веткой *master*.  
Вам нужно создать свою ветку с именем, которое будет зависеть от того, что предстоит сделать:
- Фикс ишью: *<ваш_ник>/<номер_версии_в_которую_войдет_фикс>/fix-#<номер_ишью>*.
- Новая фишка: *<ваш_ник>/<номер_версии_в_которую_войдет_фикс>/<краткое_описание_фишки>*

Номер разрабатываемой версии можно спросить у мэйнтэйнера репозитория [в Telegram (самый надёжный способ)](https://tele.click/dadyarri).  
Туда же можно задавать любые вопросы по коду, тестированию и пр.

Таких веток может быть несколько. Каждую из них нужно создавать из мастера.

Затем, когда работа с веткой будет завершена, нужно из мастера создать новую ветку с именем *wip/<номер_версии>*, в неё слить все ваши ветки, выгрузить её на GitHub, и создать запрос на слияние

### Наименование коммитов

1. По возможности коммит должен содержать изменения только одного файла (если это не рефактор, например).

2. Имя коммита должно быть на английском, начинаться с заглавной буквы, заканчиваться точкой и содержать краткое описание изменений, сделанных в этом коммите

3. Имя коммита не должно содержать глаголов в страдательном залоге (вместо *Added* нужно использовать *Add*, например).

4. Если коммит решает проблему, указанную в [issue](https://github.com/dadyarri/ralph/issues), нужно упомянуть в имени коммита номер этого ишью через знак решетки (например: *Fix issue #100 (<краткое описание ишью>).*)

5. В каждом коммите должно быть одно изменение, которое можно трактовать коротко и однозначно. Не допускаются коммиты, изменяющие 20 файлов с именем *"A lot of fixes."*