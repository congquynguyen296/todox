# Kiến trúc hệ thống
Hệ thống này là một ví dụ điển hình của mô hình **MVT (Model-View-Template)** nhưng được chuyển thể sang dạng **SPA (Single Page Application)**.

```mermaid
graph TD
    User[Người dùng] -->|Thao tác trên UI| ViewJS[Backbone Views]
    ViewJS -->|Sync dữ liệu| CollectionJS[Backbone Collection]
    CollectionJS -->|AJAX (GET, POST, PUT, DELETE)| API[Pyramid Backend]
    API -->|Query/Insert| DB[(SQLite Database)]
    API -->|JSON Response| ViewJS
    ViewJS -->|Render lại HTML| UI[Màn hình]
```

## Luồng hoạt động chính
1. **Khởi động**: Khi truy cập `/`:
   - Pyramid chạy `home_view`, trả về `index.jinja2`.
   - `index.jinja2` tải các file JavaScript (Backbone, JQuery, Underscore).
   - `app.js` khởi chạy, tạo `AppView`.
   - `AppView` gọi `todos.fetch()`.

2. **Fetching Data**:
   - `todos.fetch()` gửi một `GET` request tới `/api/tasks`.
   - Pyramid query database, lấy danh sách tasks, chuyển thành JSON list.
   - Backbone nhận JSON, tạo ra các `Todo` model tương ứng trong bộ nhớ trình duyệt.
   - `AppView` lắng nghe sự kiện `reset` hoặc `add` từ Collection để vẽ lại danh sách `<li>` trên màn hình.

3. **Thao tác người dùng (Ví dụ: Thêm mới)**:
   - Người dùng gõ text và nhấn Enter.
   - `AppView` bắt sự kiện `keypress` -> tạo mới một model `Todo`.
   - Model `Todo` gọi `.save()`.
   - Backbone gửi `POST` request tới `/api/tasks` kèm JSON `{title: "..."}`.
   - Pyramid nhận request, lưu vào DB, trả về JSON của task vừa tạo (bao gồm ID mới sinh).
   - Backbone cập nhật ID đó vào model và vẽ task mới lên màn hình.
