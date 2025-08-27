## Phase 5: Views & Forms Implementation

### Task 5: Create Comprehensive Views and Forms
**Priority**: High | **Estimated Time**: 16 hours

#### Objective
Implement all necessary views and forms to support the complete marketplace functionality, including product browsing, cart management, checkout process, and user account management.

#### Deliverables
- [ ] Template-based views for all pages
- [ ] API views for AJAX functionality
- [ ] Form classes with validation
- [ ] Authentication and permission handling
- [ ] Error handling and user feedback

#### Implementation Steps

1. **Create Form Classes**
   ```python
   # marketplace/forms/__init__.py
   from .product_forms import ProductSearchForm, ProductReviewForm
   from .user_forms import UserRegistrationForm, UserProfileForm, SellerApplicationForm
   from .checkout_forms import ShippingAddressForm, PaymentForm
   
   # marketplace/forms/product_forms.py
   class ProductSearchForm(forms.Form):
       query = forms.CharField(
           max_length=100,
           required=False,
           widget=forms.TextInput(attrs={
               'placeholder': 'Rechercher produits et services...',
               'class': 'form-control search-input'
           })
       )
       category = forms.ModelChoiceField(
           queryset=Category.objects.filter(parent__isnull=True),
           required=False,
           empty_label="Toutes les catégories"
       )
       min_price = forms.DecimalField(required=False, min_value=0)
       max_price = forms.DecimalField(required=False, min_value=0)
       in_stock = forms.BooleanField(required=False)
       
       def clean(self):
           cleaned_data = super().clean()
           min_price = cleaned_data.get('min_price')
           max_price = cleaned_data.get('max_price')
           
           if min_price and max_price and min_price > max_price:
               raise forms.ValidationError("Le prix minimum ne peut pas être supérieur au prix maximum")
   
   class ProductReviewForm(forms.ModelForm):
       class Meta:
           model = Review
           fields = ['rating', 'title', 'comment']
           widgets = {
               'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
               'comment': forms.Textarea(attrs={'rows': 4})
           }
   ```

2. **Implement Template Views**
   ```python
   # marketplace/views/pages.py
   class HomePageView(TemplateView):
       template_name = 'pages/home.html'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context.update({
               'featured_products': Product.objects.featured()[:8],
               'categories': Category.objects.filter(parent__isnull=True),
               'banners': Banner.objects.filter(is_active=True),
               'recent_reviews': Review.objects.select_related('product', 'user').order_by('-created_at')[:6]
           })
           return context
   
   class ProductDetailView(DetailView):
       model = Product
       template_name = 'pages/product_detail.html'
       context_object_name = 'product'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           product = self.object
           
           context.update({
               'related_products': ProductService.get_related_products(product),
               'reviews': product.reviews.select_related('user').order_by('-created_at'),
               'review_form': ProductReviewForm(),
               'can_review': self.can_user_review(product)
           })
           return context
           
       def can_user_review(self, product):
           if not self.request.user.is_authenticated:
               return False
           # Check if user has purchased this product
           return OrderItem.objects.filter(
               order__user=self.request.user,
               product=product,
               order__status='delivered'
           ).exists()
   
   class CategoryListView(ListView):
       model = Product
       template_name = 'pages/category_list.html'
       context_object_name = 'products'
       paginate_by = 24
       
       def get_queryset(self):
           category_slug = self.kwargs.get('slug')
           self.category = get_object_or_404(Category, slug=category_slug)
           
           queryset = Product.objects.filter(category=self.category).available()
           
           # Apply filters from form
           form = ProductSearchForm(self.request.GET)
           if form.is_valid():
               if form.cleaned_data['query']:
                   queryset = queryset.filter(
                       Q(name__icontains=form.cleaned_data['query']) |
                       Q(description__icontains=form.cleaned_data['query'])
                   )
               if form.cleaned_data['min_price']:
                   queryset = queryset.filter(price__gte=form.cleaned_data['min_price'])
               if form.cleaned_data['max_price']:
                   queryset = queryset.filter(price__lte=form.cleaned_data['max_price'])
           
           # Apply sorting
           sort_by = self.request.GET.get('sort', 'popularity')
           if sort_by == 'price_asc':
               queryset = queryset.order_by('price')
           elif sort_by == 'price_desc':
               queryset = queryset.order_by('-price')
           elif sort_by == 'newest':
               queryset = queryset.order_by('-created_at')
           elif sort_by == 'rating':
               queryset = queryset.order_by('-average_rating')
           else:  # popularity
               queryset = queryset.order_by('-view_count', '-created_at')
               
           return queryset
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context.update({
               'category': self.category,
               'search_form': ProductSearchForm(self.request.GET),
               'current_filters': self.request.GET,
               'sellers': User.objects.filter(
                   products__category=self.category
               ).annotate(
                   products_count=Count('products')
               ).distinct()
           })
           return context
   ```

3. **Implement AJAX Views**
   ```python
   # marketplace/views/ajax.py
   class AddToCartView(LoginRequiredMixin, View):
       def post(self, request):
           try:
               product_id = request.POST.get('product_id')
               quantity = int(request.POST.get('quantity', 1))
               
               product = get_object_or_404(Product, id=product_id)
               
               if quantity > product.available_quantity:
                   return JsonResponse({
                       'success': False,
                       'message': 'Quantité demandée non disponible'
                   })
               
               cart, created = Cart.objects.get_or_create(user=request.user)
               cart_item, item_created = CartItem.objects.get_or_create(
                   cart=cart,
                   product=product,
                   defaults={'quantity': quantity}
               )
               
               if not item_created:
                   cart_item.quantity += quantity
                   cart_item.save()
               
               return JsonResponse({
                   'success': True,
                   'message': 'Produit ajouté au panier',
                   'cart_count': cart.items.count(),
                   'cart_total': str(cart.total_price)
               })
               
           except Exception as e:
               return JsonResponse({
                   'success': False,
                   'message': 'Erreur lors de l\'ajout au panier'
               })
   
   class ProductQuickViewView(DetailView):
       model = Product
       template_name = 'components/product_quick_view.html'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context['is_quick_view'] = True
           return context
   ```

4. **Implement User Account Views**
   ```python
   # marketplace/views/account.py
   class UserRegistrationView(CreateView):
       form_class = UserRegistrationForm
       template_name = 'account/register.html'
       success_url = reverse_lazy('account:profile')
       
       def form_valid(self, form):
           user = form.save()
           login(self.request, user)
           messages.success(self.request, 'Compte créé avec succès!')
           return super().form_valid(form)
   
   class UserProfileView(LoginRequiredMixin, UpdateView):
       model = User
       form_class = UserProfileForm
       template_name = 'account/profile.html'
       success_url = reverse_lazy('account:profile')
       
       def get_object(self):
           return self.request.user
       
       def form_valid(self, form):
           messages.success(self.request, 'Profil mis à jour avec succès!')
           return super().form_valid(form)
   
   class SellerApplicationView(LoginRequiredMixin, CreateView):
       form_class = SellerApplicationForm
       template_name = 'account/become_seller.html'
       success_url = reverse_lazy('account:profile')
       
       def form_valid(self, form):
           vendor_profile = form.save(commit=False)
           vendor_profile.user = self.request.user
           vendor_profile.save()
           
           # Send notification to admin
           send_seller_application_notification.delay(vendor_profile.id)
           
           messages.success(
               self.request, 
               'Votre demande de devenir vendeur a été soumise. Nous vous contacterons bientôt.'
           )
           return super().form_valid(form)
   ```

#### Acceptance Criteria
- [ ] All major pages have functional views
- [ ] Forms include proper validation and error handling
- [ ] AJAX views provide smooth user experience
- [ ] Authentication and permissions properly enforced
- [ ] User feedback through messages system
- [ ] Mobile-responsive templates implemented

---