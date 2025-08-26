from dataclasses import asdict
from typing import Generic, Type, TypeVar

DBModel = TypeVar("DBModel")
DomainModel = TypeVar("DomainModel")
ResultModel = TypeVar("ResultModel")


class BaseMapper(Generic[DomainModel, DBModel, ResultModel]):
    domain_cls: Type[DomainModel]
    db_cls: Type[DBModel]
    result_cls: Type[ResultModel]

    @classmethod
    def to_domain(cls, db_obj: DBModel) -> DomainModel:
        return cls.domain_cls(**asdict(db_obj))

    @classmethod
    def to_db(cls, domain_obj: DomainModel) -> DBModel:
        return cls.db_cls(**asdict(domain_obj))

    @classmethod
    def to_result(cls, domain_obj: DomainModel) -> ResultModel:
        return cls.result_cls(**asdict(domain_obj))
