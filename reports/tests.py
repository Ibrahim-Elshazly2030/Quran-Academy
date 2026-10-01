from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from academy.models import Halaqah, EnrollmentHistory


class StudentReportAccessTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_access_test',
            password='Teacher123!',
            first_name='عبد',
            last_name='الرحمن',
            role=User.Role.TEACHER,
            is_active=True,
        )
        self.other_teacher = User.objects.create_user(
            username='other_teacher_access_test',
            password='Teacher123!',
            first_name='خالد',
            last_name='السعودي',
            role=User.Role.TEACHER,
            is_active=True,
        )
        self.student = User.objects.create_user(
            username='student_access_test',
            password='Student123!',
            first_name='يوسف',
            last_name='الزهراني',
            role=User.Role.STUDENT,
            is_active=True,
        )
        self.halaqah = Halaqah.objects.create(
            name='حلقة اختبار الوصول',
            teacher=self.teacher,
            is_active=True,
        )
        EnrollmentHistory.objects.create(
            student=self.student,
            halaqah=self.halaqah,
            assigned_sheikh=self.teacher,
            status=EnrollmentHistory.Status.ACTIVE,
        )

    def test_teacher_can_access_his_student_report(self):
        self.client.login(username='teacher_access_test', password='Teacher123!')
        response = self.client.get(reverse('reports:student_report', args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)

    def test_other_teacher_cannot_access_student_report(self):
        self.client.login(username='other_teacher_access_test', password='Teacher123!')
        response = self.client.get(reverse('reports:student_report', args=[self.student.pk]))
        self.assertEqual(response.status_code, 403)
