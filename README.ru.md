# IP Location

<p align="center">
  <strong>Язык:</strong>
  <a href="README.md">English</a>
  |
  <a href="README.ru.md">Русский</a>
</p>

Десктопное приложение для определения локации по IP-адресу с интерфейсом на PySide6, оформленным в палитре Catppuccin Mocha.

При запуске приложение определяет текущий публичный IP, отправляет его в `ipgeolocationio` и показывает локацию, часовой пояс, провайдера, организацию, координаты и флаг страны, если он доступен.

## Windows-релиз

Для Windows скачайте готовую сборку из GitHub Releases:

1. Скачайте `IP-Location-Windows.zip`.
2. Распакуйте архив в любую локальную папку.
3. Откройте `.env` в распакованной папке `IP Location`.
4. Укажите свой `IPGEOLOCATION_API_KEY`. Получить API-ключ можно здесь: <https://app.ipgeolocation.io/signup>.
5. Запустите `IP Location.exe`.

Папку после распаковки нужно держать целиком. Исполняемый файл использует `_internal/`, `.env` и `style.qss`, которые лежат рядом с ним.

Пример `.env` для Windows-сборки:

```env
IPGEOLOCATION_API_KEY=your_api_key_here
CURRENT_IP_ENDPOINT=https://api.ipify.org
FLAG_IMAGE_ENDPOINT_TEMPLATE=https://flagcdn.com/w80/{country_code}.png
```

## Запуск из исходников

Этот способ нужен, если вы хотите запускать или изменять Python-код.

### Требования

- Python 3.10 или новее
- Доступ в интернет
- API-ключ `ipgeolocationio` с <https://app.ipgeolocation.io/signup>
- Поддержка десктопных окон Qt/PySide6 в системе

Установите Python-зависимости:

```bash
python -m pip install PySide6 ipgeolocation
```

На Linux убедитесь, что приложение запускается в графической сессии и доступны зависимости Qt. На минимальных серверных образах для PySide6 могут понадобиться дополнительные системные пакеты для X11 или Wayland.

### Настройка

Создайте локальный файл `.env` из примера:

Windows PowerShell:

```powershell
Copy-Item example.env .env
```

macOS / Linux:

```bash
cp example.env .env
```

Затем откройте `.env` и укажите свой API-ключ. Получить его можно здесь: <https://app.ipgeolocation.io/signup>:

```env
IPGEOLOCATION_API_KEY=your_api_key_here
CURRENT_IP_ENDPOINT=https://api.ipify.org
FLAG_IMAGE_ENDPOINT_TEMPLATE=https://flagcdn.com/w80/{country_code}.png
```

Переменные:

- `IPGEOLOCATION_API_KEY`: обязательный API-ключ для `ipgeolocationio`.
- `CURRENT_IP_ENDPOINT`: endpoint для определения текущего публичного IP.
- `FLAG_IMAGE_ENDPOINT_TEMPLATE`: шаблон URL для PNG-флага. `{country_code}` заменяется на ISO-код страны в нижнем регистре.

Храните `.env` приватно. В нём находится API-ключ, поэтому этот файл не нужно коммитить.

### Запуск

Из директории проекта:

```bash
python main.py
```

Windows PowerShell:

```powershell
python .\main.py
```

macOS / Linux:

```bash
python3 main.py
```

Кнопка `Search` выполняет поиск по IP из поля ввода. Кнопка `Refresh` обновляет текущие данные о локации во время работы приложения. Если поле ввода пустое, при обновлении приложение заново определит текущий публичный IP.

## Кроссплатформенные заметки

Windows:

- Если команда `python` открывает Microsoft Store или не запускается, установите Python с python.org и включите опцию "Add Python to PATH".
- PySide6 использует нативные окна Qt, поэтому браузер или локальный web-сервер не нужны.

macOS:

- Если используется Python из Homebrew, устанавливайте зависимости командой `python3 -m pip install PySide6 ipgeolocation`.
- На Apple Silicon используйте пакеты той же архитектуры, что и установленный Python-интерпретатор.

Linux:

- Запускайте приложение из графической desktop-сессии.
- При проблемах с Wayland/X11 установите Qt platform packages из репозитория вашего дистрибутива.
- Если приложение не запускается из-за отсутствующего плагина `xcb`, установите стандартные runtime-библиотеки XCB для вашего дистрибутива.

## Файлы проекта

- `main.py`: логика приложения, API-запросы, PySide6-виджеты и загрузка `.env`.
- `style.qss`: Qt stylesheet с плейсхолдерами цветов Catppuccin Mocha.
- `example.env`: шаблон конфигурации.
- `.env`: локальная приватная конфигурация.

## Решение проблем

`Set IPGEOLOCATION_API_KEY in .env.`

Файл `.env` отсутствует или переменная `IPGEOLOCATION_API_KEY` пустая.

`Set CURRENT_IP_ENDPOINT in .env.`

Не задан endpoint для определения текущего публичного IP.

Флаг не отображается:

- Проверьте доступ к домену из `FLAG_IMAGE_ENDPOINT_TEMPLATE`.
- Убедитесь, что ответ geolocation API содержит двухбуквенный код страны.

Локация определяется неточно:

IP-геолокация приблизительна и зависит от данных провайдера. VPN, proxy, мобильные сети и корпоративные сети могут влиять на результат.
