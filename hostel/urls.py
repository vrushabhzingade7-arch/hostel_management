from django.urls import path
from . import views

urlpatterns = [

    # ================= HOME =================
    path('', views.user_login, name='home'),

    # ================= AUTH =================
    path('admin_login/', views.admin_login, name='admin_login'),
    path('student_login/', views.student_login, name='student_login'),
    path('logout/', views.user_logout, name='logout'),

    # ================= DASHBOARDS =================
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    # ================= LEAVE SYSTEM =================
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('leave_status/', views.leave_status, name='leave_status'),
    path('leave_requests/', views.leave_requests, name='leave_requests'),

    # APPROVAL SYSTEM
    path(
        'leave/<int:leave_id>/<str:role>/<str:action>/',
        views.approve_leave,
        name='approve_leave'
    ),

    # ================= ATTENDANCE =================
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),

    # ================= ROOM MANAGEMENT =================
    path('room_info/', views.room_info, name='room_info'),
    path('update_room/<int:student_id>/', views.update_room, name='update_room'),
    path('student_room/', views.student_room, name='student_room'),

    # ================= FEES =================
    path('fees_admin/', views.fees_admin, name='fees_admin'),
    path('fees_student/', views.fees_student, name='fees_student'),

    # ================= OUTING =================
    path('outing_student/', views.outing_student, name='outing_student'),
    path('mark_out/', views.mark_out, name='mark_out'),
    path('mark_in/<int:outing_id>/', views.mark_in, name='mark_in'),
    path('outing_admin/', views.outing_admin, name='outing_admin'),

    # ================= FEEDBACK =================
    path('feedback/', views.feedback_submit, name='feedback_submit'),
    path('feedback_admin/', views.feedback_admin, name='feedback_admin'),
]