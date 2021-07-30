from django.urls import path
from django.urls.resolvers import URLPattern
from .views import *
from . import views

# app_name='store'

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('allProducts/', AllProductView.as_view(), name='allProducts'),
    path('productDetail/<slug:slug>/', ProductDetailView.as_view(), name='productDetail'),
    path('addtocart<int:pro_id>', AddToCartView.as_view(), name='addToCart'),
    path('myCart/', MyCartView.as_view(), name= 'myCart'),
    path('manageCart/<int:cp_id>', ManageCartView.as_view(),name='manageCart'),
    path('emptyCart/', EmptyCartView.as_view(), name='emptyCart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('khaltiRequest/', KhaltiRequestView.as_view(), name='khaltiRequest'),

    path('esewaRequest/', EsewaRequestView.as_view(), name='esewaRequest'),
    path('esewaVerify/', EsewaVerificationView.as_view(), name='esewaVerify'),

    path('customerRegistration/', CustomerRegistrationView.as_view(), name='customerRegistration'),
    path('customerLogout/', CustomerLogoutView.as_view(), name='customerLogout'),
    path('customerLogin/', CustomerLoginView.as_view(), name='customerLogin'),
    path('customerProfile/', CustomerProfileView.as_view(), name='customerProfile'),
    path('customerProfile/orderDetail-<int:pk>/',OrderDetailView.as_view(), name='orderDetail'),
    path('search/', SearchView.as_view(), name='search'),
    path('passwordReset/', PasswordResetView.as_view(), name='passwordReset'),
    path('password-change/<email>/<token>/', PasswordChangeView.as_view(), name='passwordChange'),

    #admin pages
    path('adminLogin/', AdminLoginView.as_view(), name='adminLogin'),
    path('adminHome/',AdminHomeView.as_view(), name='adminHome'),
    path('adminHome/orderDetail-<int:pk>/',AdminOrderDetailView.as_view(), name='adminOrderDetail' ),
    path('adminHome/allOrders/', AdminAllOrdersView.as_view(), name='adminAllOrders'),
    path('adminOrderStatus-<int:pk>-change/',AdminOrderStatusChangeView.as_view(), name='orderStatusChange'),
    path('adminProductList/', AdminProductListView.as_view(), name='adminProductList'),
    path('adminProductCreate/', AdminProductCreateView.as_view(), name='adminProductCreate'),
    path('adminProductUpdate/<slug>/', AdminProductUpdateView.as_view(),name='adminProductUpdate'),

    path('loadMore',views.LoadMore, name='load-more'),




]