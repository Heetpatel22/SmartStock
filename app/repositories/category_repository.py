"""
Category repository implementing ICategoryRepository.
Encapsulates all SQLAlchemy data access for Category models.
"""

from typing import List, Optional
from app import db
from app.core.interfaces import ICategoryRepository
from app.models import Category


class CategoryRepository(ICategoryRepository):
    """Concrete repository for Category operations."""

    def __init__(self, session=None):
        self._session = session or db.session

    def get_all(self) -> List[Category]:
        return self._session.query(Category).order_by(Category.name).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self._session.get(Category, category_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self._session.query(Category).filter(Category.name.ilike(name.strip())).first()

    def save(self, category: Category) -> Category:
        self._session.add(category)
        self._session.flush()
        return category

    def delete(self, category: Category) -> None:
        self._session.delete(category)
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()

