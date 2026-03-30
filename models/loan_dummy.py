from sqlalchemy import Column, Integer, String, Float
from db.database import Base

class DummyLoan(Base):
    __tablename__ = "dummy_loans"
    
    id = Column(Integer, primary_key=True, index=True)
    borrower_name = Column(String, nullable=False)
    aadhar_number = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_status = Column(String, default="APPROVED")   # must match what your service checks