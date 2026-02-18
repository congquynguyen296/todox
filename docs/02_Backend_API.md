# Backend API & Logic Chi tiết
Tài liệu này giải thích từng dòng code quan trọng trong phần Backend (Pyramid).

## 1. Data Model (`todox/models.py`)
Đây là nơi định nghĩa cấu trúc dữ liệu. Chúng ta dùng **SQLAlchemy** (ORM).

### Class `Task`
```python
class Task(Base):
    __tablename__ = 'tasks' # Tên bảng trong database
    # Các cột (Columns)
    id = Column(Integer, primary_key=True)      # ID tự tăng
    title = Column(Text, nullable=False)        # Nội dung task
    completed = Column(Boolean, default=False)  # Trạng thái hoàn thành
    created_at = Column(DateTime, default=datetime.utcnow) # Thời gian tạo

    # Phương thức quan trọng nhất: to_json()
    # Vì API trả về JSON cho Backbone, và SQLAlchemy object không thể tự chuyển thành JSON
    # nên ta cần hàm này để map object -> dictionary.
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            # Chuyển datetime sang chuỗi chuẩn ISO để JS dễ đọc
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

## 2. Views & API Endpoints (`todox/views.py`)
Đây là trái tim của Backend, nơi xử lý request và trả về response.

### Controller: `TasksView` (Xử lý danh sách)
Lớp này xử lý các request tới `/api/tasks`.

#### `GET /api/tasks`
Lấy toàn bộ danh sách công việc.
```python
@view_config(request_method='GET')
def get(self):
    # Query toàn bộ bảng Task, sắp xếp giảm dần theo thời gian tạo
    tasks = DBSession.query(Task).order_by(Task.created_at.desc()).all()
    # Lặp qua từng task object và gọi to_json() để tạo thành list JSON
    return [t.to_json() for t in tasks]
```

#### `POST /api/tasks`
Tạo mới một công việc.
```python
@view_config(request_method='POST')
def post(self):
    # self.request.json_body: Pyramid tự động parse JSON gửi từ Backbone thành Python Dict
    json_data = self.request.json_body
    title = json_data.get('title')
    
    # Validate dữ liệu cơ bản
    if not title:
        return Response(status=400, json_body={'error': 'Title is required'})

    # Tạo object mới nhưng CHƯA lưu vào DB ngay lập tức
    new_task = Task(title=title)
    DBSession.add(new_task)
    
    # flush() cực kỳ quan trọng: Nó đẩy SQL INSERT xuống DB để lấy về ID tự tăng
    # nhưng chưa commit transaction (transaction được quản lý bởi `pyramid_tm`)
    DBSession.flush()
    
    # Trả về task vừa tạo (kèm ID) để Backbone cập nhật lại model ở client
    return new_task.to_json()
```

### Controller: `TaskView` (Xử lý từng item)
Lớp này xử lý các request tới `/api/tasks/{id}`.

#### `_get_task()` (Helper)
```python
def _get_task(self):
    # self.task_id được lấy từ URL (ví dụ: /api/tasks/10 -> id=10)
    # Hàm này tìm task theo ID, trả về None nếu không thấy
    return DBSession.query(Task).filter(Task.id == self.task_id).first()
```

#### `PUT /api/tasks/{id}`
Cập nhật trạng thái hoặc nội dung của một task. Backone gửi request này khi bạn tick checkbox hoặc sửa title.
```python
@view_config(request_method='PUT')
def put(self):
    task = self._get_task()
    if not task:
        return Response(status=404, json_body={'error': 'Task not found'})
        
    json_data = self.request.json_body
    
    # Chỉ cập nhật những trường có gửi lên
    if 'title' in json_data:
        task.title = json_data['title']
    if 'completed' in json_data:
        task.completed = json_data['completed']
    
    DBSession.add(task)
    # Không cần return body cho PUT theo chuẩn REST, nhưng Backbone thích nhận lại model cập nhật
    return task.to_json()
```

#### `DELETE /api/tasks/{id}`
Xóa một task.
```python
@view_config(request_method='DELETE')
def delete(self):
    task = self._get_task()
    if not task:
        return Response(status=404)
        
    # Lệnh xóa trong SQLAlchemy
    DBSession.delete(task)
    
    # Trả về 204 No Content báo hiệu thành công và không có dữ liệu trả về
    return Response(status=204)
```
