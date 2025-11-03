# models.py
import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.conf import settings

# --- Choices ---

class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Khách hàng'
    ADMIN = 'ADMIN', 'Quản trị viên'

class AccountStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Hoạt động'
    DISABLED = 'DISABLED', 'Vô hiệu hóa'

class ProductStatus(models.TextChoices):
    FOR_SALE = 'FOR_SALE', 'Đang bán'
    SOLD_OUT = 'SOLD_OUT', 'Hết hàng'
    DELETED = 'DELETED', 'Đã xóa'

class ReviewStatus(models.TextChoices):
    VISIBLE = 'VISIBLE', 'Đang hiển thị'
    HIDDEN = 'HIDDEN', 'Bị ẩn'

class PaymentMethod(models.TextChoices):
    COD = 'COD', 'Thanh toán khi nhận hàng'
    ONLINE = 'ONLINE', 'Thanh toán trực tuyến'

class OrderStatus(models.TextChoices):
    NEW = 'NEW', 'Mới'
    PENDING = 'PENDING', 'Chờ xác nhận'
    SHIPPING = 'SHIPPING', 'Đang giao'
    DELIVERED = 'DELIVERED', 'Đã giao'
    CANCELLED = 'CANCELLED', 'Đã hủy'

class CharityProgramStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Đang hoạt động'
    PAUSED = 'PAUSED', 'Tạm dừng'
    COMPLETED = 'COMPLETED', 'Kết thúc'

class DonationType(models.TextChoices):
    FROM_PRODUCT = 'FROM_PRODUCT', 'Từ % Sản phẩm'
    FROM_VOUCHER = 'FROM_VOUCHER', 'Từ Ưu đãi 10%'

class PointTransactionType(models.TextChoices):
    EARNED = 'EARNED', 'Cộng điểm'
    SPENT = 'SPENT', 'Trừ điểm'

class VoucherType(models.TextChoices):
    PERCENTAGE = 'PERCENTAGE', 'Theo %'
    FIXED_AMOUNT = 'FIXED_AMOUNT', 'Theo số tiền'

class RedeemedStatus(models.TextChoices):
    NOT_USED = 'NOT_USED', 'Chưa dùng'
    USED = 'USED', 'Đã dùng'
    EXPIRED = 'EXPIRED', 'Hết hạn'

class PostType(models.TextChoices):
    BLOG = 'BLOG', 'Blog'
    NEWS = 'NEWS', 'Tin tức'
    REPORT = 'REPORT', 'Báo cáo Minh bạch'

# --- I. User Management ---

class CustomUserManager(BaseUserManager):
    """
    Quản lý tùy chỉnh cho model User với email là định danh.
    """
    def create_user(self, email, full_name, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('Email là bắt buộc')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('account_status', AccountStatus.ACTIVE)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser phải có is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser phải có is_superuser=True.')

        return self.create_user(email, full_name, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    phone_number = models.CharField(max_length=20, verbose_name="Số điện thoại")
    
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        verbose_name="Vai trò"
    )
    account_status = models.CharField(
        max_length=50,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name="Trạng thái tài khoản"
    )

    # Trường bắt buộc của Django Admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) # Dùng để kiểm soát việc đăng nhập

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number']

    def __str__(self):
        return self.email

class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='shipping_addresses',
        verbose_name="Người dùng"
    )
    recipient_name = models.CharField(max_length=255, verbose_name="Họ tên người nhận")
    phone_number = models.CharField(max_length=20, verbose_name="Số điện thoại")
    province = models.CharField(max_length=100, verbose_name="Tỉnh/Thành")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    ward = models.CharField(max_length=100, verbose_name="Phường/Xã")
    street_address = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    is_default = models.BooleanField(default=False, verbose_name="Là địa chỉ mặc định")

    def __str__(self):
        return f"{self.recipient_name} - {self.street_address}"

class OTPVerification(models.Model):
    email = models.EmailField(verbose_name="Email")
    otp_code = models.CharField(max_length=6, verbose_name="Mã OTP")
    expires_at = models.DateTimeField(verbose_name="Thời gian hết hạn")
    is_used = models.BooleanField(default=False, verbose_name="Đã sử dụng")

    def __str__(self):
        return f"OTP cho {self.email}"

# --- II. Product & Review ---

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên hộp quà")
    description = models.TextField(verbose_name="Mô tả")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá bán")
    charity_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Phần trăm từ thiện",
        help_text="Ví dụ: 10.00 cho 10%"
    )
    image = models.ImageField(upload_to='products/', verbose_name="Hình ảnh đại diện")
    status = models.CharField(
        max_length=50,
        choices=ProductStatus.choices,
        default=ProductStatus.FOR_SALE,
        verbose_name="Trạng thái"
    )

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='reviews',
        verbose_name="Người dùng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Sản phẩm"
    )
    rating = models.IntegerField(verbose_name="Điểm sao (1-5)")
    comment = models.TextField(verbose_name="Bình luận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    display_status = models.CharField(
        max_length=50,
        choices=ReviewStatus.choices,
        default=ReviewStatus.VISIBLE,
        verbose_name="Trạng thái hiển thị"
    )

    def __str__(self):
        return f"Đánh giá cho {self.product.name} bởi {self.user.email}"

# --- III. Order & Payment ---

class Order(models.Model):
    order_code = models.CharField(max_length=20, unique=True, verbose_name="Mã đơn hàng")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders',
        verbose_name="Người dùng"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Tổng tiền")
    shipping_address = models.ForeignKey(
        ShippingAddress, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Địa chỉ giao hàng"
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethod.choices,
        verbose_name="Phương thức thanh toán"
    )
    order_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        verbose_name="Trạng thái đơn hàng"
    )
    applied_voucher = models.ForeignKey(
        'RedeemedOffer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders',
        verbose_name="Mã ưu đãi đã áp dụng"
    )
    donate_voucher = models.BooleanField(default=False, verbose_name="Quyên góp ưu đãi")

    def __str__(self):
        return self.order_code

class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='details',
        verbose_name="Đơn hàng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Sản phẩm"
    )
    quantity = models.PositiveIntegerField(verbose_name="Số lượng")
    price_at_purchase = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Giá tại thời điểm mua"
    )

    class Meta:
        unique_together = ('order', 'product') # Đảm bảo mỗi sản phẩm chỉ xuất hiện 1 lần trong đơn

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Đơn: {self.order.order_code})"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='status_history',
        verbose_name="Đơn hàng"
    )
    new_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        verbose_name="Trạng thái mới"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': UserRole.ADMIN},
        verbose_name="Người cập nhật"
    )
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian cập nhật")

    def __str__(self):
        return f"{self.order.order_code} -> {self.new_status}"

class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cart_items',
        verbose_name="Người dùng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"Giỏ hàng của {self.user.email} - {self.product.name}"

# --- IV. Charity & Transparency ---

class CharityProgram(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên chương trình")
    description = models.TextField(verbose_name="Mô tả")
    image = models.ImageField(upload_to='charity_programs/', verbose_name="Hình ảnh")
    target_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Mục tiêu")
    status = models.CharField(
        max_length=50,
        choices=CharityProgramStatus.choices,
        default=CharityProgramStatus.ACTIVE,
        verbose_name="Trạng thái"
    )

    def __str__(self):
        return self.name

class DonationHistory(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='donations',
        verbose_name="Đơn hàng"
    )
    program = models.ForeignKey(
        CharityProgram, 
        on_delete=models.PROTECT, 
        related_name='donations',
        verbose_name="Chương trình"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền quyên góp")
    donation_type = models.CharField(
        max_length=50,
        choices=DonationType.choices,
        verbose_name="Loại quyên góp"
    )

    def __str__(self):
        return f"Quyên góp {self.amount} cho {self.program.name}"

class Disbursement(models.Model):
    program = models.ForeignKey(
        CharityProgram, 
        on_delete=models.PROTECT, 
        related_name='disbursements',
        verbose_name="Chương trình"
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Số tiền giải ngân")
    disbursed_at = models.DateField(verbose_name="Ngày giải ngân")
    recipient_partner = models.CharField(max_length=255, verbose_name="Đối tác nhận")
    notes = models.TextField(verbose_name="Ghi chú")
    proof_link = models.FileField(upload_to='disbursements_proof/', blank=True, null=True, verbose_name="Link chứng từ")

    def __str__(self):
        return f"Giải ngân {self.amount} cho {self.program.name}"

# --- V. Offers & Points ---

class LovePointBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='point_balance',
        verbose_name="Người dùng"
    )
    current_balance = models.PositiveIntegerField(default=0, verbose_name="Tổng điểm hiện tại")

    def __str__(self):
        return f"Điểm của {self.user.email}: {self.current_balance}"

class LovePointHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='point_history',
        verbose_name="Người dùng"
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=PointTransactionType.choices,
        verbose_name="Loại giao dịch"
    )
    points_changed = models.IntegerField(verbose_name="Số điểm thay đổi")
    reason = models.CharField(max_length=255, verbose_name="Lý do")
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giao dịch")

    def __str__(self):
        return f"{self.user.email}: {self.transaction_type} {self.points_changed} điểm"

class Voucher(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên ưu đãi")
    points_required = models.PositiveIntegerField(verbose_name="Số điểm yêu cầu")
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá trị giảm")
    voucher_type = models.CharField(
        max_length=50,
        choices=VoucherType.choices,
        verbose_name="Loại ưu đãi"
    )
    conditions = models.TextField(verbose_name="Điều kiện sử dụng")

    def __str__(self):
        return self.name

class RedeemedOffer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='redeemed_offers',
        verbose_name="Người dùng"
    )
    voucher = models.ForeignKey(
        Voucher, 
        on_delete=models.PROTECT, 
        related_name='redeemed_instances',
        verbose_name="Ưu đãi"
    )
    redeemed_code = models.CharField(max_length=50, unique=True, verbose_name="Mã ưu đãi đã cấp")
    redeemed_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đổi")
    usage_status = models.CharField(
        max_length=50,
        choices=RedeemedStatus.choices,
        default=RedeemedStatus.NOT_USED,
        verbose_name="Trạng thái sử dụng"
    )

    def __str__(self):
        return f"{self.redeemed_code} ({self.user.email})"

# --- VI. Content ---

class ContentPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    featured_image = models.ImageField(upload_to='content_posts/', verbose_name="Ảnh đại diện")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        limit_choices_to={'role': UserRole.ADMIN},
        verbose_name="Tác giả"
    )
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    post_type = models.CharField(
        max_length=50,
        choices=PostType.choices,
        verbose_name="Loại bài viết"
    )

    def __str__(self):
        return self.title