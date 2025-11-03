# Nền tảng E-commerce "Hộp Quà Bí Ẩn" & Thiện Nguyện (Django)

## Giới thiệu

Đây là một dự án Django xây dựng nền tảng E-commerce cho sản phẩm "Hộp quà bí ẩn" (Mystery Box), kết hợp với hệ thống quyên góp từ thiện và điểm thưởng cho khách hàng. Trang Django Admin được cấu hình đầy đủ để quản lý 17 model nghiệp vụ.

## 🌟 Tính năng chính

- **Quản lý Người dùng:**
  - Sử dụng **Custom User Model** (Email là `USERNAME_FIELD`).
  - Phân quyền người dùng (Khách hàng, Admin).
- **Quản lý Sản phẩm:**
  - Quản lý "Hộp quà bí ẩn" (Product).
  - Thiết lập giá bán và phần trăm trích cho từ thiện.
- **Hệ thống Đơn hàng:**
  - Quản lý giỏ hàng (`ShoppingCart`).
  - Quản lý địa chỉ giao hàng (`ShippingAddress`).
  - Theo dõi chi tiết đơn hàng (`Order`, `OrderDetail`).
  - Lịch sử trạng thái đơn hàng (`OrderStatusHistory`).
- **Hệ thống Thiện nguyện & Minh bạch:**
  - Quản lý chương trình thiện nguyện (`CharityProgram`).
  - Ghi nhận lịch sử quyên góp (`DonationHistory`).
  - Minh bạch giải ngân (`Disbursement`).
- **Hệ thống Điểm thưởng "Điểm Yêu Thương":**
  - Tích điểm cho khách hàng (`LovePointBalance`).
  - Đổi điểm lấy ưu đãi (`Voucher`).
  - Theo dõi lịch sử giao dịch điểm.
- **Quản lý Nội dung:**
  - Hệ thống Blog/Tin tức.
  - Báo cáo minh bạch (`ContentPost`).
- **Trang Admin mạnh mẽ:**
  - 17 model được đăng ký và tùy chỉnh (`list_display`, `search_fields`, `list_filter`).

## 🛠️ Công nghệ sử dụng

- **Backend:** Python 3, Django
- **Cơ sở dữ liệu:** PostgreSQL / MySQL (Khuyến nghị) hoặc SQLite (Development)
- **Xử lý ảnh:** Pillow

## 🚀 Cài đặt và Chạy dự án

### 1. Clone Repository

```bash
git clone [URL_REPOSITORY_CUA_BAN]
cd [TEN_THU_MUC_PROJECT]
```

### 2. Tạo và kích hoạt Môi trường ảo (venv)

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt (Windows)
.\venv\Scripts\activate

# Kích hoạt (macOS/Linux)
source venv/bin/activate
```

### 3. Cài đặt Thư viện

Tạo file `requirements.txt` với nội dung:

```
django
pillow
```

Sau đó, chạy lệnh cài đặt:

```bash
pip install -r requirements.txt
```

### 4. Cấu hình Project Django

Trong file `config/settings.py`:

**a. Đăng ký App `store`:**

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.staticfiles',
    'store',  # <-- Thêm app của bạn
]
```

**b. Thiết lập Custom User Model:**

Thêm vào cuối file `settings.py`:

```python
# config/settings.py
AUTH_USER_MODEL = 'store.User'
```

**c. Cấu hình Media (cho `ImageField`):**

Thêm vào cuối file `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Cập nhật file `config/urls.py` để hiển thị ảnh trong môi trường development:

```python
# config/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 5. Khởi tạo Cơ sở dữ liệu

```bash
# Tạo file migration cho app 'store'
python manage.py makemigrations store

# Áp dụng migration để tạo các bảng
python manage.py migrate
```

### 6. Tạo Superuser (Admin)

```bash
python manage.py createsuperuser
```

Bạn sẽ được yêu cầu nhập Email, Họ tên, Số điện thoại và Mật khẩu.

### 7. Chạy Server

```bash
python manage.py runserver
```

### 🔐 Truy cập Trang Admin

- **URL:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Đăng nhập bằng tài khoản superuser bạn vừa tạo.
