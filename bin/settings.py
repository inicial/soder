from betterconf import Config, field
from betterconf.config import AbstractProvider


class ConfigProvider(AbstractProvider):  # наследуемся от абстрактного класса
    SETTINGS_FILE = "conf.ini"  # путь до файла с настройками

    def __init__(self):
        with open(self.SETTINGS_FILE, "r") as f:
            self._settings = json.load(f)  # открываем и читаем

    def get(self, name):
        return self._settings.get(name)  # если значение есть - возвращаем его, иначе - None. Библиотека будет выбрасывать свою исключением, если получит None.

provider = ()


class EditorConfig(Config):
    lines = field("linenumbers", default="True")
