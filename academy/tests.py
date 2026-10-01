from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from academy.models import Halaqah, EnrollmentHistory, Surah
from attendance.models import AttendanceRecord
from evaluations.models import RecitationSession, EvaluationCriterion
from reports.services import get_student_comprehensive_data, get_sheikh_comprehensive_data

class QuranAcademySystemTests(TestCase):
    def setUp(self):
        # 1. مستخدمون
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            role=User.Role.ADMIN,
            first_name='المشرف',
            last_name='العام'
        )
        self.sheikh1 = User.objects.create_user(
            username='sheikh1',
            password='password123',
            role=User.Role.TEACHER,
            first_name='الشيخ أحمد',
            last_name='المنشاوي'
        )
        self.sheikh2 = User.objects.create_user(
            username='sheikh2',
            password='password123',
            role=User.Role.TEACHER,
            first_name='الشيخ محمود',
            last_name='الحصري'
        )
        self.student = User.objects.create_user(
            username='student_test',
            password='password123',
            role=User.Role.STUDENT,
            first_name='عمر',
            last_name='عبد الرحمن',
            guardian_name='عبد الرحمن',
            guardian_phone='0501234567'
        )

        # 2. سور ومعايير
        self.surah_fatihah = Surah.objects.create(number=1, name_arabic="الفاتحة", ayah_count=7, start_page=1, juz_number=1)
        self.surah_baqarah = Surah.objects.create(number=2, name_arabic="البقرة", ayah_count=286, start_page=2, juz_number=1)

        # 3. حلقات
        self.halaqah1 = Halaqah.objects.create(
            name="حلقة الشاطبي",
            teacher=self.sheikh1,
            days_schedule="السبت، الإثنين",
            time_period=Halaqah.TimePeriod.ASR
        )
        self.halaqah2 = Halaqah.objects.create(
            name="حلقة نافع",
            teacher=self.sheikh2,
            days_schedule="الأحد، الثلاثاء",
            time_period=Halaqah.TimePeriod.MAGHRIB
        )

        # 4. قيد الطالب في حلقة 1
        self.enrollment1 = EnrollmentHistory.objects.create(
            student=self.student,
            halaqah=self.halaqah1,
            assigned_sheikh=self.sheikh1,
            status=EnrollmentHistory.Status.ACTIVE,
            start_date=timezone.now().date(),
            created_by=self.admin
        )

        self.client = Client()

    def test_user_roles(self):
        self.assertTrue(self.admin.is_admin_role)
        self.assertTrue(self.sheikh1.is_teacher_role)
        self.assertTrue(self.student.is_student_role)

    def test_sheikh_data_isolation(self):
        """التحقق من أن الشيخ لا يستطيع الوصول لحلقة شيخ آخر"""
        self.client.login(username='sheikh2', password='password123')
        # الشيخ 2 يحاول الوصول لحلقة الشيخ 1
        url = reverse('attendance:halaqah_attendance_sheet', kwargs={'halaqah_id': self.halaqah1.id})
        response = self.client.get(url)
        # يجب منعه (403 Forbidden)
        self.assertEqual(response.status_code, 403)

        # بينما الشيخ 1 (صاحب الحلقة) يدخل بنجاح (200 OK)
        self.client.login(username='sheikh1', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_attendance_recording(self):
        """تسجيل الحضور بجميع الحالات: متأخر بعذر مع الدقائق"""
        self.client.login(username='sheikh1', password='password123')
        url = reverse('attendance:halaqah_attendance_sheet', kwargs={'halaqah_id': self.halaqah1.id})
        post_data = {
            'session_date': str(timezone.now().date()),
            f'status_{self.student.id}': AttendanceRecord.Status.LATE_EXCUSED,
            f'delay_{self.student.id}': '25',
            f'notes_{self.student.id}': 'تأخر بعذر المواصلات'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        record = AttendanceRecord.objects.get(student=self.student, halaqah=self.halaqah1)
        self.assertEqual(record.status, AttendanceRecord.Status.LATE_EXCUSED)
        self.assertEqual(record.delay_minutes, 25)
        self.assertEqual(record.notes, 'تأخر بعذر المواصلات')

    def test_recitation_evaluation_score_calculation(self):
        """التحقق من معادلات احتساب درجات التقييم التلقائية والتقدير"""
        rec = RecitationSession(
            student=self.student,
            halaqah=self.halaqah1,
            sheikh=self.sheikh1,
            date=timezone.now().date(),
            recitation_type=RecitationSession.RecitationType.NEW_MEMORIZATION,
            surah_from=self.surah_baqarah,
            ayah_from=1,
            surah_to=self.surah_baqarah,
            ayah_to=20,
            score_memorization=9.5,
            score_tajweed=9.0,
            score_fluency=5.0,
            score_discipline=5.0
        )
        rec.save()

        # المجموع: 9.5 + 9.0 + 5.0 + 5.0 = 28.5 من 30
        self.assertEqual(rec.total_score, 28.5)
        # النسبة: (28.5 / 30) * 100 = 95.0%
        self.assertEqual(rec.percentage, 95.0)
        # التقدير ممتاز مرتفع A+
        self.assertEqual(rec.rating_grade, RecitationSession.RatingGrade.EXCELLENT_PLUS)

    def test_student_transfer_and_history_preservation(self):
        """اختبار نقل الطالب لحلقة أخرى مع حفظ تاريخ الحلقة السابقة بالكامل"""
        self.client.login(username='admin_test', password='password123')
        url = reverse('academy:student_transfer', kwargs={'student_id': self.student.id})
        
        post_data = {
            'new_halaqah': self.halaqah2.id,
            'transfer_reason': 'أتم مستوى الحفظ المطلوب ونُقل لحلقة الإتقان'
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        # التحقق من أن السجل السابق تم إنهاؤه وتوثيقه
        self.enrollment1.refresh_from_db()
        self.assertEqual(self.enrollment1.status, EnrollmentHistory.Status.TRANSFERRED)
        self.assertIsNotNone(self.enrollment1.end_date)

        # التحقق من أن القيد الجديد تم إنشاؤه بحلقة الشيخ 2
        new_enr = EnrollmentHistory.objects.filter(student=self.student, halaqah=self.halaqah2).first()
        self.assertIsNotNone(new_enr)
        self.assertEqual(new_enr.status, EnrollmentHistory.Status.ACTIVE)
        self.assertEqual(new_enr.assigned_sheikh, self.sheikh2)

        # التحقق من التقرير الشامل للطالب أنه يحتوي على الحلقتين والشيوخ الاثنين
        report_data = get_student_comprehensive_data(self.student.id)
        self.assertEqual(report_data['enrollments'].count(), 2)
        sheikh_ids = [e.assigned_sheikh_id for e in report_data['enrollments']]
        self.assertIn(self.sheikh1.id, sheikh_ids)
        self.assertIn(self.sheikh2.id, sheikh_ids)
