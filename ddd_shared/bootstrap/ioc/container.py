from functools import lru_cache

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from ddd_shared.bootstrap.ioc.providers import DBProvider, SettingsProvider
from ddd_shared.bootstrap.ioc.providers.application.services import ServicesProvider
from ddd_shared.bootstrap.ioc.providers.application.usecases import UserUseCaseProvider
from ddd_shared.bootstrap.ioc.providers.application.usecases.email_verification import (
    EmailVerificationUseCasesProvider,
)
from ddd_shared.bootstrap.ioc.providers.infra.repositories import (
    EmailVerificationRepositoryProvider,
    UserRepositoryProvider,
)

REPOSITORY_PROVIDERS: list[Provider] = [
    UserRepositoryProvider(),
    EmailVerificationRepositoryProvider(),
]

USECASE_PROVIDERS: list[Provider] = [
    UserUseCaseProvider(),
    EmailVerificationUseCasesProvider(),
]

PROVIDERS: list[Provider] = [
    SettingsProvider(),
    DBProvider(),
    *REPOSITORY_PROVIDERS,
    ServicesProvider(),
    *USECASE_PROVIDERS,
    FastapiProvider(),
]


@lru_cache(1)
def get_container() -> AsyncContainer:
    container: AsyncContainer = make_async_container(*PROVIDERS)

    return container
