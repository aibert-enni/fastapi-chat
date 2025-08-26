from ddd_shared.application.usecases.user.results import UserResult
from ddd_shared.infra.domain.enteties.user import User
from shared.users.models import User as UserDB

from .base import BaseMapper


class UserMapper(BaseMapper[User, UserDB, UserResult]):
    domain_cls = User
    db_cls = UserDB
    result_cls = UserResult

    @classmethod
    def to_domain(cls, db_model: UserDB) -> User:
        return User(
            db_model.username,
            db_model.fullname,
            db_model.email,
            db_model.password,
            db_model.is_active,
            db_model.is_superuser,
            db_model.id,
        )

    @classmethod
    def to_result(cls, domain_obj: User) -> UserResult:
        return UserResult(
            id=domain_obj.id,
            username=domain_obj.username,
            fullname=domain_obj.fullname,
            email=domain_obj.email,
            is_active=domain_obj.is_active,
            is_superuser=domain_obj.is_superuser,
        )
