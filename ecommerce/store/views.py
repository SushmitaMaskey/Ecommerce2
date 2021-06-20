from .forms import CheckoutForm, CustomerRegistrationForm, CustomerLoginForm, AdminProductCreateForm
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView,FormView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db.models import Q  # helps to form 'or' relation in search
from django.core.paginator import Paginator
import requests as req


class EcomMixin(object):  #to assign customer to the cart. this is inherited by other classes
    def dispatch(self,request, *args, **kwargs):
        cart_id= request.session.get('cart_id')
        if cart_id:
            cart= Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart.customer= request.user.customer
                cart.save()
        return super().dispatch(request,*args, **kwargs)


class HomeView(EcomMixin,TemplateView):
    template_name='home.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        products=Product.objects.all().order_by('-id')
        paginator= Paginator(products,6)
        page_num= self.request.GET.get('page')
        product_list= paginator.get_page(page_num)
        context['product_list']= product_list
        return context


class AboutView(EcomMixin,TemplateView):
    template_name='about.html'

class AllProductView(EcomMixin,TemplateView):
    template_name='allProducts.html'
    def get_context_data(self, **kwargs): 
        context= super().get_context_data(**kwargs)
        context['categories']= Category.objects.all()
        return context

class ProductDetailView(EcomMixin,TemplateView):
    template_name='productDetail.html'
    def get_context_data(self, **kwargs): 
        context= super().get_context_data(**kwargs)
        url_slug= self.kwargs['slug']
        print(url_slug)
        product= Product.objects.get(slug=url_slug)
        product.view_count +=1
        product.save()
        context['product']= product
        return context

class AddToCartView(EcomMixin,TemplateView):
    template_name='addtocart.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        #get the product id
        product_id= self.kwargs['pro_id']

        #get the product object
        product_obj=Product.objects.get(id=product_id)

        #check if cart exists
        cart_id= self.request.session.get('cart_id', None)

        if cart_id:
            cart_obj= Cart.objects.get(id=cart_id)
            this_product_in_cart= cart_obj.cartproduct_set.filter(product=product_obj)
        # if product exists
            if this_product_in_cart.exists():
                cartproduct= this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
        #if product doesnot exist
            else:
                cartproduct= CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, 
                quantity=1, subtotal= product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()

        #if cart does not exist
        else: 
            cart_obj= Cart.objects.create(total=0)
            self.request.session['cart_id']= cart_obj.id
            cartproduct= CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, 
                quantity=1, subtotal= product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context

class MyCartView(EcomMixin,TemplateView):
    template_name= 'myCart.html'
            
    def get_context_data(self, **kwargs): 
        context= super().get_context_data(**kwargs)
        cart_id= self.request.session.get('cart_id', None)
        if cart_id:
            cart= Cart.objects.get(id=cart_id)
            # print(cart.cartproduct_set.all ) 
        else:
            cart= None
        context['cart']= cart

        return context

class ManageCartView(EcomMixin,View):
    def get(self,request, *args, **kwargs):
        print('this is manage cart')
        cp_id= self.kwargs['cp_id']   
        action= request.GET.get('action')
        cp_obj= CartProduct.objects.get(id=cp_id)
        cart_obj= cp_obj.cart       #getting the cart object throught the cartproduct object
        
        if action=='inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action=='dsc':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity==0:
                cp_obj.delete()
        elif action=='rmv':
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect('myCart')


class EmptyCartView(EcomMixin,View):
    def get(self, request, *args, **kwargs):
        cart_id= request.session.get('cart_id', None)
        if cart_id:
            cart= Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete() # using reverse relationship 
            cart.total=0
            cart.save()
        return redirect('myCart') 

class CheckoutView(EcomMixin,CreateView):
    template_name='checkout.html'
    form_class= CheckoutForm
    success_url= reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):  #this function is run first. done to confirm authentication before teh checkout process
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/customerLogin/?next=/checkout/') #next is used to form url and direct them to the next page 
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        cart_id= self.request.session.get('cart_id', None)
        if cart_id:
            cart= Cart.objects.get(id=cart_id)
            context['cart']= cart
        return context

    def form_valid(self, form):     # to fill the other required fields in the form 
        cart_id= self.request.session.get('cart_id')
        if cart_id:
            cart_obj= Cart.objects.get(id=cart_id)
            form.instance.cart=cart_obj
            form.instance.subtotal= cart_obj.total
            form.instance.discount= 0
            form.instance.total= cart_obj.total
            form.instance.order_status= 'Order Received'
            del self.request.session['cart_id']   # deleting the session after the order is placed
            pm= form.cleaned_data.get('payment_method')
            order = form.save()#Overriding the save() method of the parent cause we need order object to get the id
            # print(type(order))
            if pm=='Esewa':
                return redirect(reverse('esewaRequest')+'?o_id='+ str(order.id))
            else:
                pass
        else:
            return redirect('home')
        return super().form_valid(form)

class KhaltiRequestView(View):
    def get(self,request,*args,**kwargs):
        context={
            
        }
        return render(request, 'khaltiRequest.html', context)

class EsewaRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id= request.GET.get('o_id')
        order= Order.objects.get(id=o_id)
        context={
        'order': order
        }
        return render(request, 'esewaRequest.html', context)

class EsewaVerificationView(View):
    def get(self,request,*args, **kwargs):
        import xml.etree.ElementTree as ET
        
        oid= request.GET.get('oid')
        amt= request.GET.get('amt')
        refId=request.GET.get('refId')
        
        url ="https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amt,
            'scd': 'EPAYTEST',
            'rid': refId,
            'pid': oid,
        }
        resp = req.post(url, d)
        root = ET.fromstring(resp.content) # getting the xml value
        status=root[0].text.strip() #parsing it and stripping the extra lines
        print(status)
        order=Order.objects.get(id=oid)

        if status=='Success':
            order.payment_completed= True
            order.save()
            return redirect('/')
        else:
            return redirect('esewaRequest/?o_id='+ oid)
        

class CustomerRegistrationView(CreateView):
    template_name='customerRegistration.html'
    form_class= CustomerRegistrationForm
    success_url=reverse_lazy('home')

    def form_valid(self, form):
        username= form.cleaned_data.get('username')  #cleaned_data return the validated form values
        password=form.cleaned_data.get('password')
        email=form.cleaned_data.get('email')
        user=User.objects.create_user(username=username, password=password, email=email)
        form.instance.user=user
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_url= self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return self.success_url
        return super().get_success_url()


class CustomerLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('home')

class CustomerLoginView(FormView):
    template_name='customerLogin.html'
    form_class=CustomerLoginForm
    success_url= reverse_lazy('home')

    def form_valid(self, form):
        uname= form.cleaned_data.get('username')
        pword= form.cleaned_data.get('password')
        usr= authenticate(username=uname, password=pword)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error':'Invalid Credentials'})

        return super().form_valid(form)

    def get_success_url(self):   #to override the success_url when required
        next_url= self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return self.success_url
        # return super().get_success_url()

class CustomerProfileView(TemplateView):
    template_name='customerProfile.html'

    def dispatch(self, request, *args, **kwargs):  #this function is run first. done to confirm authentication before teh checkout process
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/customerLogin/?next=/customerProfile/') #next is used to form url and direct them to the next page 
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        customer= self.request.user.customer
        context['customer']=customer
        orders= Order.objects.filter(cart__customer=customer).order_by('-id')  #fieldname__lookuptype=value
        context['orders']=orders
        return context
        
class OrderDetailView(DetailView):
    template_name='orderDetail.html'
    model= Order
    context_object_name = 'order'

    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id= self.kwargs['pk']
            order_obj= Order.objects.get(id=order_id)
            if request.user.customer!= order_obj.cart.customer: #to avoid one customer to view the details of the other customer by changing id in the url
                return redirect('customerProfile')
        else:
            return redirect('/customerLogin/?next=/customerProfile/')  
        return super().dispatch(request, *args, **kwargs)

class AdminLoginView(FormView):
    template_name='AdminPages/adminLogin.html'
    form_class=CustomerLoginForm  #reusing it because of similarity
    success_url=reverse_lazy('adminHome')

    def form_valid(self, form):
        uname= form.cleaned_data.get('username')
        pword= form.cleaned_data.get('password')
        usr= authenticate(username=uname, password=pword)
        print(usr)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error':'Invalid Credentials'})

        return super().form_valid(form)

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/adminLogin/')  
        return super().dispatch(request, *args, **kwargs)   


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name='AdminPages/adminHome.html'

    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs) 
        pendingorders= Order.objects.filter(order_status= 'Order Received').order_by('-id')
        context['pendingorders']=pendingorders
        return context

class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name='AdminPages/adminOrderDetail.html'
    model= Order
    context_object_name= 'order_obj'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['status']= ORDER_STATUS
        return context

class AdminAllOrdersView(AdminRequiredMixin, ListView):
    template_name='AdminPages/adminAllOrders.html'
    queryset= Order.objects.all().order_by('-id')
    context_object_name='orders'

class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id= self.kwargs['pk']
        order_status= request.POST.get('status')
        # print(order_id, order_status)
        order_obj= Order.objects.get(id=order_id)
        order_obj.order_status= order_status
        order_obj.save()
        return redirect(reverse_lazy('adminOrderDetail', kwargs={'pk': self.kwargs['pk']}))

class AdminProductListView(AdminRequiredMixin, ListView):
    template_name='AdminPages/adminProductList.html'
    queryset= Product.objects.all().order_by('-id')
    context_object_name='products'
    # print('hello 1111111111111111111')

class AdminProductCreateView(AdminRequiredMixin, FormView):
    template_name= 'AdminPages/adminProductCreate.html'
    form_class=AdminProductCreateForm
    success_url=reverse_lazy('adminProductList')

    def form_valid(self, form):
        p=form.save()
        images= self.request.FILES.getlist('more_images')
        for i in images:
            ProductImage.objects.create(product=p, images=i)
        return super().form_valid(form)
    
class AdminProductUpdateView(AdminRequiredMixin, UpdateView):
    template_name='AdminPages/productUpdate.html'
    model= Product
    form_class= AdminProductCreateForm
    success_url= reverse_lazy('adminProductList')


class SearchView(TemplateView):
    template_name='search.html'

    def get_context_data(self, **kwargs): 
        context= super().get_context_data(**kwargs)
        keyword= self.request.GET.get('keyword')
        product_list= Product.objects.filter(Q(title__icontains= keyword) | Q(description__icontains=keyword) )
        context['product_list']= product_list
        return context
