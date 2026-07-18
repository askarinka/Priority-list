from django.urls import path
from . import views

urlpatterns = [
    # Main task list
    path('', views.index, name='index'),
    path('task/add-form/', views.task_add_form, name='task_add_form'),
    path('task/add/', views.task_add, name='task_add'),
    path('task/<int:pk>/', views.task_row, name='task_row'),
    path('task/<int:pk>/edit-form/', views.task_edit_form, name='task_edit_form'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('reorder/', views.task_reorder, name='task_reorder'),
    # Waiting list
    path('waiting/', views.waiting_index, name='waiting_index'),
    path('waiting/add-form/', views.waiting_add_form, name='waiting_add_form'),
    path('waiting/add/', views.waiting_add, name='waiting_add'),
    path('waiting/<int:pk>/', views.waiting_row, name='waiting_row'),
    path('waiting/<int:pk>/edit-form/', views.waiting_edit_form, name='waiting_edit_form'),
    path('waiting/<int:pk>/edit/', views.waiting_edit, name='waiting_edit'),
    path('waiting/<int:pk>/delete/', views.waiting_delete, name='waiting_delete'),
    path('waiting/reorder/', views.waiting_reorder, name='waiting_reorder'),
]
