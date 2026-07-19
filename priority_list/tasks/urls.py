from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/add-form/', views.task_add_form, name='task_add_form'),
    path('task/add/', views.task_add, name='task_add'),
    path('task/<int:pk>/', views.task_row, name='task_row'),
    path('task/<int:pk>/edit-form/', views.task_edit_form, name='task_edit_form'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('reorder/', views.task_reorder, name='task_reorder'),
]
