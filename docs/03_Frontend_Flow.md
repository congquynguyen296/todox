# Frontend Flow Chi tiết (Backbone.js)
Backbone tổ chức code theo mô hình **MVC** (Model-View-Controller, nhưng trong Backbone gọi là Router).

## 1. Model (`static/js/models/todo.js`)
Đại diện cho 1 công việc duy nhất.

```javascript
app.Todo = Backbone.Model.extend({
    // Giá trị mặc định khi tạo mới model mà không truyền tham số
    defaults: {
        title: '',
        completed: false
    },

    // Hàm tiện ích để đảo ngược trạng thái completed
    toggle: function () {
        // .save() sẽ kích hoạt request PUT lên server
        this.save({
            completed: !this.get('completed')
        });
    }
});
```

## 2. Collection (`static/js/collections/todos.js`)
Danh sách các Models. Đây là cầu nối chính với API Backend.

```javascript
var Todos = Backbone.Collection.extend({
    model: app.Todo, // Chỉ định Collection này chứa các model kiểu app.Todo

    // QUAN TRỌNG: URL này bảo Backbone biết phải gọi API nào
    // fetch() -> GET /api/tasks
    // create() -> POST /api/tasks
    url: '/api/tasks',

    // Hàm lọc các task đã xong
    completed: function () {
        return this.where({completed: true});
    },

    // Hàm lọc các task chưa xong
    remaining: function () {
        return this.where({completed: false});
    },
    
    // ...
});
```

## 3. Views (Giao diện)

### `TodosView` (`static/js/views/todo.js`) -> `app.TodoView`
Quản lý giao diện của **MỘT** dòng task (`<li>`).

- **Events**:
    - `click .toggle`: Khi click checkbox -> gọi hàm `toggleCompleted`.
    - `dblclick label`: Khi double click -> vào chế độ sửa (`edit`).
    - `click .destroy`: Khi click nút xóa -> gọi hàm `clear`.

- **Chi tiết hàm `clear`**:
```javascript
clear: function () {
    // .destroy() sẽ gửi request DELETE /api/tasks/{id} lên server
    // Sau khi server trả lời thành công, model sẽ bị xóa khỏi Collection
    // View lắng nghe sự kiện 'destroy' của model để tự remove thẻ <li> khỏi DOM
    this.model.destroy();
}
```

### `AppView` (`static/js/views/app.js`)
Quản lý giao diện tổng thể của ứng dụng.

- **Initialize**:
```javascript
initialize: function () {
    // ... cache các selector
    
    // Lắng nghe sự kiện từ Collection
    this.listenTo(app.todos, 'add', this.addOne); // Khi có task mới -> thêm <li>
    this.listenTo(app.todos, 'reset', this.addAll); // Khi nạp lại danh sách -> vẽ lại hết
    
    // FETCH DỮ LIỆU LẦN ĐẦU
    // {reset: true} để kích hoạt sự kiện 'reset' sau khi tải xong
    app.todos.fetch({reset: true});
}
```

- **createOnEnter**:
```javascript
createOnEnter: function (e) {
    if (e.which !== 13 || !this.$input.val().trim()) {
        return;
    }

    // .create() làm 2 việc:
    // 1. Tạo model mới và thêm vào Collection
    // 2. Gửi POST request lên server để lưu
    app.todos.create(this.newAttributes());
    
    // Xóa trắng ô input
    this.$input.val('');
}
```

## 4. Router (`static/js/routers/router.js`)
Xử lý URL hash (phần sau dấu `#`).

```javascript
routes: {
    '*filter': 'setFilter' // Bắt tất cả các hash, ví dụ #/active, #/completed
},

setFilter: function (param) {
    // Lưu filter hiện tại vào biến toàn cục app.TodoFilter
    app.TodoFilter = param || '';

    // Kích hoạt sự kiện 'filter' trên Collection
    // Các View đang lắng nghe sự kiện này sẽ tự ẩn/hiện task tương ứng
    window.app.todos.trigger('filter');
}
```
