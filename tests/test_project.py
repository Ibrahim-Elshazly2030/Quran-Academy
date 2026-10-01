from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User
from academy.models import Halaqah, Surah, EnrollmentHistory
from attendance.models import AttendanceRecord
from evaluations.models import EvaluationCriterion, RecitationSession


class CoreProjectTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='StrongPass123!',
            first_name='Ali',
            last_name='Ahmed',
            role=User.Role.TEACHER,
            email='teacher1@example.com',
        )
        self.student = User.objects.create_user(
            username='student1',
            password='StrongPass123!',
            first_name='Samir',
            last_name='Khalid',
            role=User.Role.STUDENT,
            email='student1@example.com',
        )

        self.halaqah = Halaqah.objects.create(
            name='حلقة الصباح',
            teacher=self.teacher,
            category=Halaqah.Category.GENERAL,
            max_students=12,
        )

        self.surah_1 = Surah.objects.create(
            number=1,
            name_arabic='الفاتحة',
            ayah_count=7,
            revelation_place='Meccan',
        )
        self.surah_2 = Surah.objects.create(
            number=2,
            name_arabic='البقرة',
            ayah_count=286,
            revelation_place='Medinan',
        )

        self.criterion = EvaluationCriterion.objects.create(
            name='التحفيظ',
            code='MEM-001',
            max_score=10,
            description='تقييم الحفظ والضبط.',
        )

    def test_user_role_and_display_properties(self):
        self.assertTrue(self.teacher.is_teacher_role)
        self.assertFalse(self.teacher.is_student_role)
        self.assertEqual(self.teacher.display_name, 'Ali Ahmed')
        self.assertIn(self.teacher.get_role_display(), ['شيخ / معلم محفظ', 'مدير / مشرف إداري'])

    def test_halaqah_enrollment_tracking(self):
        EnrollmentHistory.objects.create(
            student=self.student,
            halaqah=self.halaqah,
            assigned_sheikh=self.teacher,
            status=EnrollmentHistory.Status.ACTIVE,
            notes='مستمر في الحلقة',
        )

        self.assertEqual(self.halaqah.current_students_count, 1)
        self.assertIn('حلقة الصباح', str(self.halaqah))

    def test_attendance_record_properties(self):
        record = AttendanceRecord.objects.create(
            student=self.student,
            halaqah=self.halaqah,
            sheikh=self.teacher,
            status=AttendanceRecord.Status.PRESENT,
            delay_minutes=0,
            notes='حاضر بانتظام',
        )

        self.assertTrue(record.is_positive_attendance)
        self.assertEqual(record.badge_class, 'badge-success')
        self.assertEqual(str(record).startswith(self.student.display_name), True)

    def test_evaluation_criterion_creation(self):
        self.assertEqual(self.criterion.code, 'MEM-001')
        self.assertEqual(float(self.criterion.max_score), 10.0)
        self.assertIn('التحفيظ', str(self.criterion))

    def test_recitation_session_calculates_total_score_and_grade(self):
        recitation = RecitationSession.objects.create(
            student=self.student,
            halaqah=self.halaqah,
            sheikh=self.teacher,
            recitation_type=RecitationSession.RecitationType.NEW_MEMORIZATION,
            surah_from=self.surah_1,
            ayah_from=1,
            surah_to=self.surah_2,
            ayah_to=5,
            pages_completed=2.5,
            score_memorization=9.0,
            score_tajweed=8.0,
            score_fluency=4.0,
            score_discipline=4.0,
            hesitations_count=1,
            major_mistakes=0,
            minor_mistakes=1,
            sheikh_notes='مستوى جيد جدًا',
            next_assignment='تكرار الآيات 1 إلى 10',
        )

        self.assertEqual(float(recitation.total_score), 25.0)
        self.assertEqual(float(recitation.percentage), 83.3)
        self.assertEqual(recitation.rating_grade, RecitationSession.RatingGrade.VERY_GOOD)
        self.assertIn('البقرة', recitation.location_display)

    def test_login_page_loads(self):
        client = Client()
        response = client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_root_redirects_to_dashboard(self):
        client = Client()
        response = client.get(reverse('root'), follow=False)
        self.assertIn(response.status_code, (301, 302))
