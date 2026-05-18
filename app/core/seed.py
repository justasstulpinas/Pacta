from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.permission import permission

#  seedo funkcija kuri sukuria pradinius duomenis, jei useris pries tai neturejo duomenu
def seed_rbac(db: Session):
    if db.query(Role).count() > 0:
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