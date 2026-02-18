from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from datetime import datetime
from zope.sqlalchemy import register

# Tạo session kết nối database, scoped_session giúp quản lý session trong mô hình đa luồng
DBSession = scoped_session(sessionmaker())
register(DBSession)

# Base class cho các model
Base = declarative_base()

class Task(Base):
    """
    Model đại diện cho bảng 'tasks' trong cơ sở dữ liệu.
    """
    __tablename__ = 'tasks'
    
    # Khóa chính tự động tăng
    id = Column(Integer, primary_key=True)
    # Tiêu đề công việc, không được để trống
    title = Column(Text, nullable=False)
    # Trạng thái hoàn thành, mặc định là False
    completed = Column(Boolean, default=False)
    # Thời gian tạo
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_json(self):
        """
        Helper method để chuyển object thành dictionary, dễ dàng trả về JSON.
        """
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
