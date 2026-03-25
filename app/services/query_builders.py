from sqlalchemy.orm import Query

from app.models.contract_template import ContractTemplate
from app.models.filled_contract import FilledContract



def base_template_query(query: Query):
    return query.filter(ContractTemplate.is_deleted == False)


def template_by_id(query: Query, template_id: int):
    return query.filter(ContractTemplate.id == template_id)


def submission_by_template(query: Query, template_id: int):
    return query.filter(FilledContract.template_id == template_id)


def submission_status_filter(query: Query, status: str | None):
    if status:
        return query.filter(FilledContract.status == status)
    return query

def owner_scope(query: Query, owner_id: int):
    return query.filter(ContractTemplate.owner_id == owner_id)  
