import logging

from app.extensions import db
from app.models import Category

logger = logging.getLogger(__name__)


def create_category(name: str) -> Category:
    """Create a new category."""
    cat = Category(name=name)
    db.session.add(cat)
    db.session.commit()
    logger.info(f'Category created: {name}')
    return cat


def update_category(category: Category, name: str) -> Category:
    """Update a category name."""
    category.name = name
    db.session.commit()
    logger.info(f'Category updated: {category.name}')
    return category


def delete_category(category: Category) -> None:
    """Delete a category."""
    db.session.delete(category)
    db.session.commit()
    logger.info(f'Category deleted: {category.id}')
