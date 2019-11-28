from django.urls import path
from . import views
from . import views_image as views_image

app_name = 'select'

urlpatterns = [
    # path('', views.index, name='index'),
    path('product/',views.CpmProduct.as_view(),name="product"),
    path('add_one/',views.CpmAddOneProduct.as_view(),name="add_one"),
    path('add_one_success/',views.CpmAddOneProductSuccess.as_view(),name="add_one_success"),
    path('add_one_type/',views.CpmAddOneKindProduct.as_view(),name="add_one_type"),
    path('edit_one/',views.CpmEditOneProduct.as_view(),name="edit_one"),

    
    path('p_list/',views.CpmProductSelectList.as_view(),name="p_list"),


    path('pingshen/',views.CpmProductSelectListPingshen.as_view(),name="pingshen"),
    path('cancel_product/',views.CpmProductCancelOne.as_view(),name="cancel_product"),


    path('add_sku/',views.CpmProductSelectListAddSKU.as_view(),name="add_sku"),
    path('add_sku_detail/',views.CpmProductSelectListAddSKUEdit.as_view(),name="add_sku_detail"),
    path('edit_sku/',views.CpmProductEditGoodsSku.as_view(),name="edit_sku"),



    
    path('cpm_category/',views.CpmQueryCategory.as_view(),name="cpm_category"),
] + [
        path('img_upload/',views_image.ImageUpload.as_view(),name="img_upload"),
        path('img_search/',views_image.ImageSearch.as_view(),name="img_search"),
]
