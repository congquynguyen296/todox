from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from .models import DBSession, Base

def main(global_config, **settings):
    """
    Hàm này trả về một Pyramid WSGI application.
    """
    # Cấu hình engine cho SQLAlchemy từ file .ini
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    
    # Include các thư viện cần thiết
    config.include('pyramid_jinja2')
    config.include('pyramid_tm')

    # Cấu hình static assets (css, js, images)
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Cấu hình routes
    config.add_route('home', '/')
    
    # API Routes cho Backbone
    # /api/tasks cho GET (list) và POST (create)
    config.add_route('tasks', '/api/tasks')
    # /api/tasks/{id} cho GET (detail), PUT (update), DELETE (delete)
    config.add_route('task', '/api/tasks/{id}')

    # Scan project để tìm các decorator @view_config và @view_defaults
    config.scan()

    return config.make_wsgi_app()
