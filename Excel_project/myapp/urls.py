from django.urls import path
from .views import index, upload_excel, get_sheets, get_columns

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload_excel, name='upload_excel'),
    path('get-sheets/', get_sheets, name='get_sheets'),
    path('get-columns/', get_columns, name='get_columns'),
]
