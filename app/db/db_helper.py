from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import throw_error

def safe_commit(db):
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        throw_error(f"Database Error: {str(e)}",500)    
    