from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import DBAPIError
from .models import DBSession, Task

# Cấu hình view mặc định cho route '/', trả về template HTML chính
@view_config(route_name='home', renderer='templates/index.jinja2')
def home_view(request):
    """
    View chính để render trang Single Page Application.
    Backend chỉ cần trả về khung HTML, phần còn lại do Backbone xử lý.
    """
    return {'p project': 'todox'}

# Cấu hình cho API tasks
# route_name='tasks' được định nghĩa trong __init__.py
# renderer='json' tự động chuyển dict trả về thành JSON response
@view_defaults(route_name='tasks', renderer='json')
class TasksView:
    def __init__(self, request):
        self.request = request

    # GET /api/tasks - Lấy danh sách công việc
    @view_config(request_method='GET')
    def collection_get(self):
        try:
            tasks = DBSession.query(Task).order_by(Task.created_at.desc()).all()
            return [task.to_json() for task in tasks]
        except DBAPIError:
            return Response("Database error", status=500)

    # POST /api/tasks - Tạo công việc mới
    @view_config(request_method='POST')
    def collection_post(self):
        try:
            # Lấy dữ liệu JSON từ request body
            data = self.request.json_body
            if 'title' not in data or not data['title'].strip():
                 return Response("Title is required", status=400)
            
            new_task = Task(title=data['title'])
            DBSession.add(new_task)
            DBSession.flush() # Flush để lấy ID mới tạo
            return new_task.to_json()
        except DBAPIError:
             return Response("Database error", status=500)

# Cấu hình cho API task chi tiết (theo ID)
@view_defaults(route_name='task', renderer='json')
class TaskView:
    def __init__(self, request):
        self.request = request
        self.task_id = int(request.matchdict['id'])

    # Helper để lấy task theo ID
    def _get_task(self):
        return DBSession.query(Task).filter(Task.id == self.task_id).first()

    # GET /api/tasks/{id}
    @view_config(request_method='GET')
    def get(self):
        task = self._get_task()
        if not task:
            return Response("Task not found", status=404)
        return task.to_json()

    # PUT /api/tasks/{id} - Cập nhật công việc
    @view_config(request_method='PUT')
    def put(self):
        task = self._get_task()
        if not task:
            return Response("Task not found", status=404)
        
        data = self.request.json_body
        
        # Cập nhật các trường nếu có trong request
        if 'title' in data:
            task.title = data['title']
        if 'completed' in data:
            task.completed = data['completed']
            
        DBSession.add(task)
        self.request.response.status_int = 200 # OK
        return task.to_json()

    # DELETE /api/tasks/{id} - Xóa công việc
    @view_config(request_method='DELETE')
    def delete(self):
        task = self._get_task()
        if not task:
            return Response("Task not found", status=404)
        
        DBSession.delete(task)
        return Response(status=204) # No Content
