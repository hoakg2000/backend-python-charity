# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, ShippingAddress, OTPVerification,
    Product, Review,
    Order, OrderDetail, OrderStatusHistory, ShoppingCart,
    CharityProgram, DonationHistory, Disbursement,
    LovePointBalance, LovePointHistory, Voucher, RedeemedOffer,
    ContentPost
)

# --- I. User Management ---

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Tùy chỉnh Admin cho Custom User Model.
    """
    # Các trường hiển thị trong danh sách
    list_display = ('email', 'full_name', 'phone_number', 'role', 'account_status', 'is_staff')
    list_filter = ('role', 'account_status', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('email',)

    # Tùy chỉnh các trường khi Edit
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Thông tin cá nhân', {'fields': ('full_name', 'phone_number')}),
        ('Phân quyền & Trạng thái', {
            'fields': (
                'role', 'account_status', 'is_active', 
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Thời gian quan trọng', {'fields': ('last_login',)}),
    )
    
    # Tùy chỉnh các trường khi Add (Tạo mới)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'full_name', 'phone_number', 'role', 'account_status', 
                'is_staff', 'is_superuser', 'password'
            ),
        }),
    )

    # Bắt buộc cho Custom User Model
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient_name', 'province', 'district', 'is_default')
    search_fields = ('user__email', 'recipient_name', 'phone_number')
    list_filter = ('is_default', 'province')

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'expires_at', 'is_used')
    search_fields = ('email',)
    list_filter = ('is_used',)

# --- II. Product & Review ---

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status', 'charity_percentage')
    search_fields = ('name', 'description')
    list_filter = ('status',)
    list_editable = ('price', 'status') # Cho phép sửa nhanh

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'display_status')
    search_fields = ('user__email', 'product__name', 'comment')
    list_filter = ('display_status', 'rating')
    list_editable = ('display_status',)

# --- III. Order & Payment ---

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    readonly_fields = ('product', 'quantity', 'price_at_purchase')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'user', 'total_amount', 'order_status', 'payment_method', 'created_at')
    search_fields = ('order_code', 'user__email')
    list_filter = ('order_status', 'payment_method', 'created_at', 'donate_voucher')
    list_editable = ('order_status',)
    readonly_fields = ('order_code', 'user', 'total_amount', 'shipping_address', 'applied_voucher')
    inlines = [OrderDetailInline] # Hiển thị chi tiết đơn hàng ngay trong trang Order

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    search_fields = ('order__order_code', 'product__name')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'new_status', 'updated_by', 'updated_at')
    search_fields = ('order__order_code',)
    list_filter = ('new_status',)

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__email', 'product__name')

# --- IV. Charity & Transparency ---

@admin.register(CharityProgram)
class CharityProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'status')
    search_fields = ('name', 'description')
    list_filter = ('status',)

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'program', 'amount', 'donation_type')
    search_fields = ('order__order_code', 'program__name')
    list_filter = ('donation_type', 'program')

@admin.register(Disbursement)
class DisbursementAdmin(admin.ModelAdmin):
    list_display = ('program', 'amount', 'disbursed_at', 'recipient_partner')
    search_fields = ('program__name', 'recipient_partner')
    list_filter = ('disbursed_at',)

# --- V. Offers & Points ---

@admin.register(LovePointBalance)
class LovePointBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_balance')
    search_fields = ('user__email',)

@admin.register(LovePointHistory)
class LovePointHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'points_changed', 'reason', 'transaction_date')
    search_fields = ('user__email', 'reason')
    list_filter = ('transaction_type', 'transaction_date')

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('name', 'voucher_type', 'points_required', 'discount_value')
    search_fields = ('name',)
    list_filter = ('voucher_type',)

@admin.register(RedeemedOffer)
class RedeemedOfferAdmin(admin.ModelAdmin):
    list_display = ('redeemed_code', 'user', 'voucher', 'usage_status', 'redeemed_at')
    search_fields = ('redeemed_code', 'user__email', 'voucher__name')
    list_filter = ('usage_status',)

# --- VI. Content ---

@admin.register(ContentPost)
class ContentPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'published_at')
    search_fields = ('title', 'content', 'author__email')
    list_filter = ('post_type', 'author')