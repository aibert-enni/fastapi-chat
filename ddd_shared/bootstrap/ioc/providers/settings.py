from dishka import Provider, Scope, provide

from shared.settings import CommonSettings


class SettingsProvider(Provider):
    scope = Scope.APP

    @provide
    def base(self) -> CommonSettings:
        settings = CommonSettings()
        return settings
