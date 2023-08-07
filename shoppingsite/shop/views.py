from itertools import product
from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# def home(request):
#  return render(request, 'shop/home.html')

class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        return render(request, 'shop/home.html',
        {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles':mobiles})


# def product_detail(request):
#  return render(request, 'shop/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            
        return render(request, 'shop/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart})

# def add_to_cart(request):
#  return render(request, 'shop/addtocart.html')


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        # cart_item = Cart.objects.all().count()
        # return{'item_count':cart_item}
        # item_count = cart_item.count()

        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'shop/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':amount})  
        else:
            return render(request, 'shop/emptycart.html')
    
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        # c.quantity-=1
        # c.save()
        if c.quantity > 1:
            c.quantity-=1
            c.save()

        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
    

        data = {
            'amount':amount,
            'totalamount':amount + shipping_amount
        }
        return JsonResponse(data)


def buy_now(request):
 return render(request, 'shop/buynow.html')

# def profile(request):
#  return render(request, 'shop/profile.html')

# def address(request):
#  return render(request, 'shop/address.html')

# def orders(request):
#  return render(request, 'shop/orders.html')

# def change_password(request):
#  return render(request, 'shop/changepassword.html')

# def mobile(request):
#  return render(request, 'shop/mobile.html')

def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'mi' or data == 'realme' or data == 'oppo' or data == 'iphone':
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=10000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=10000)

    return render(request, 'shop/mobile.html', {'mobiles':mobiles})

# def login(request):
#  return render(request, 'shop/login.html')

# def customerregistration(request):
#  return render(request, 'shop/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'shop/customerregistration.html', {'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Conguratulations!! Registered Successfully')
            form.save()
        return render(request, 'shop/customerregistration.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'shop/profile.html', {'form':form, 'active':'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Conguratulations!! Profile Updated Successfully')
        return render(request, 'shop/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'shop/address.html', {'add':add, 'active':'btn-primary' })

# def checkout(request):
#  return render(request, 'shop/checkout.html')

@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        totalamount = amount + shipping_amount
    return render(request, 'shop/checkout.html', {'add':add, 'totalamount':totalamount, 'cart_items':cart_items})

@login_required
def orders(request):
    op =OrderPlaced.objects.filter(user=request.user)
    return render(request, 'shop/orders.html', {'order_placed':op})
    
@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")