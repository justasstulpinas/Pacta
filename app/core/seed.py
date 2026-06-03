from sqlalchemy.orm import Session
from sqlalchemy import exc

from app.models.role import Role
from app.models.permission import permission

def seed_rbac(db: Session):
    try:
        if db.query(Role).count() > 0:
            return
    except exc.ProgrammingError:
        db.rollback()
        return
    link_create = permission(code="link:create")
    admin_all = permission(code="admin:all")

    db.add(link_create)
    db.add(admin_all)
    db.flush()

    creator = Role(name="creator")
    admin = Role(name="admin")

    db.add_all([creator, admin])
    db.flush()

    creator.permissions.append(link_create)
    admin.permissions.append(link_create)
    admin.permissions.append(admin_all)

    db.commit()