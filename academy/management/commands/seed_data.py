import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from academy.models import Surah, Halaqah, EnrollmentHistory
from attendance.models import AttendanceRecord
from evaluations.models import EvaluationCriterion, RecitationSession

SURAH_DATA = [
    (1, "الفاتحة", 7, "Meccan", 1, 1),
    (2, "البقرة", 286, "Medinan", 2, 1),
    (3, "آل عمران", 200, "Medinan", 50, 3),
    (4, "النساء", 176, "Medinan", 77, 4),
    (5, "المائدة", 120, "Medinan", 106, 6),
    (6, "الأنعام", 165, "Meccan", 128, 7),
    (7, "الأعراف", 206, "Meccan", 151, 8),
    (8, "الأنفال", 75, "Medinan", 177, 9),
    (9, "التوبة", 129, "Medinan", 187, 10),
    (10, "يونس", 109, "Meccan", 208, 11),
    (11, "هود", 123, "Meccan", 221, 11),
    (12, "يوسف", 111, "Meccan", 235, 12),
    (13, "الرعد", 43, "Medinan", 249, 13),
    (14, "إبراهيم", 52, "Meccan", 255, 13),
    (15, "الحجر", 99, "Meccan", 262, 14),
    (16, "النحل", 128, "Meccan", 267, 14),
    (17, "الإسراء", 111, "Meccan", 282, 15),
    (18, "الكهف", 110, "Meccan", 293, 15),
    (19, "مريم", 98, "Meccan", 305, 16),
    (20, "طه", 135, "Meccan", 312, 16),
    (21, "الأنبياء", 112, "Meccan", 322, 17),
    (22, "الحج", 78, "Medinan", 332, 17),
    (23, "المؤمنون", 118, "Meccan", 342, 18),
    (24, "النور", 64, "Medinan", 350, 18),
    (25, "الفرقان", 77, "Meccan", 359, 18),
    (26, "الشعراء", 227, "Meccan", 367, 19),
    (27, "النمل", 93, "Meccan", 377, 19),
    (28, "القصص", 88, "Meccan", 385, 20),
    (29, "العنكبوت", 69, "Meccan", 396, 20),
    (30, "الروم", 60, "Meccan", 404, 21),
    (31, "لقمان", 34, "Meccan", 411, 21),
    (32, "السجدة", 30, "Meccan", 415, 21),
    (33, "الأحزاب", 73, "Medinan", 418, 21),
    (34, "سبأ", 54, "Meccan", 428, 22),
    (35, "فاطر", 45, "Meccan", 434, 22),
    (36, "يس", 83, "Meccan", 440, 22),
    (37, "الصافات", 182, "Meccan", 446, 23),
    (38, "ص", 88, "Meccan", 453, 23),
    (39, "الزمر", 75, "Meccan", 458, 23),
    (40, "غافر", 85, "Meccan", 467, 24),
    (41, "فصلت", 54, "Meccan", 477, 24),
    (42, "الشورى", 53, "Meccan", 483, 25),
    (43, "الزخرف", 89, "Meccan", 489, 25),
    (44, "الدخان", 59, "Meccan", 496, 25),
    (45, "الجاثية", 37, "Meccan", 499, 25),
    (46, "الأحقاف", 35, "Meccan", 502, 26),
    (47, "محمد", 38, "Medinan", 507, 26),
    (48, "الفتح", 29, "Medinan", 511, 26),
    (49, "الحجرات", 18, "Medinan", 515, 26),
    (50, "ق", 45, "Meccan", 518, 26),
    (51, "الذاريات", 60, "Meccan", 520, 26),
    (52, "الطور", 49, "Meccan", 523, 27),
    (53, "النجم", 62, "Meccan", 526, 27),
    (54, "القمر", 55, "Meccan", 528, 27),
    (55, "الرحمن", 78, "Medinan", 531, 27),
    (56, "الواقعة", 96, "Meccan", 534, 27),
    (57, "الحديد", 29, "Medinan", 537, 27),
    (58, "المجادلة", 22, "Medinan", 542, 28),
    (59, "الحشر", 24, "Medinan", 545, 28),
    (60, "الممتحنة", 13, "Medinan", 549, 28),
    (61, "الصف", 14, "Medinan", 551, 28),
    (62, "الجمعة", 11, "Medinan", 553, 28),
    (63, "المنافقون", 11, "Medinan", 554, 28),
    (64, "التغابن", 18, "Medinan", 556, 28),
    (65, "الطلاق", 12, "Medinan", 558, 28),
    (66, "التحريم", 12, "Medinan", 560, 28),
    (67, "الملك", 30, "Meccan", 562, 29),
    (68, "القلم", 52, "Meccan", 564, 29),
    (69, "الحاقة", 52, "Meccan", 566, 29),
    (70, "المعارج", 44, "Meccan", 568, 29),
    (71, "نوح", 28, "Meccan", 570, 29),
    (72, "الجن", 28, "Meccan", 572, 29),
    (73, "المزمل", 20, "Meccan", 574, 29),
    (74, "المدثر", 56, "Meccan", 575, 29),
    (75, "القيامة", 40, "Meccan", 577, 29),
    (76, "الإنسان", 31, "Medinan", 578, 29),
    (77, "المرسلات", 50, "Meccan", 580, 29),
    (78, "النبأ", 40, "Meccan", 582, 30),
    (79, "النازعات", 46, "Meccan", 583, 30),
    (80, "عبس", 42, "Meccan", 585, 30),
    (81, "التكوير", 29, "Meccan", 586, 30),
    (82, "الانفطار", 19, "Meccan", 587, 30),
    (83, "المطففين", 36, "Meccan", 587, 30),
    (84, "الانشقاق", 25, "Meccan", 589, 30),
    (85, "البروج", 22, "Meccan", 590, 30),
    (86, "الطارق", 17, "Meccan", 591, 30),
    (87, "الأعلى", 19, "Meccan", 591, 30),
    (88, "الغاشية", 26, "Meccan", 592, 30),
    (89, "الفجر", 30, "Meccan", 593, 30),
    (90, "البلد", 20, "Meccan", 594, 30),
    (91, "الشمس", 15, "Meccan", 595, 30),
    (92, "الليل", 21, "Meccan", 595, 30),
    (93, "الضحى", 11, "Meccan", 596, 30),
    (94, "الشرح", 8, "Meccan", 596, 30),
    (95, "التين", 8, "Meccan", 597, 30),
    (96, "العلق", 19, "Meccan", 597, 30),
    (97, "القدر", 5, "Meccan", 598, 30),
    (98, "البينة", 8, "Medinan", 598, 30),
    (99, "الزلزلة", 8, "Medinan", 599, 30),
    (100, "العاديات", 11, "Meccan", 599, 30),
    (101, "القارعة", 11, "Meccan", 600, 30),
    (102, "التكاثر", 8, "Meccan", 600, 30),
    (103, "العصر", 3, "Meccan", 601, 30),
    (104, "الهمزة", 9, "Meccan", 601, 30),
    (105, "الفيل", 5, "Meccan", 601, 30),
    (106, "قريش", 4, "Meccan", 602, 30),
    (107, "الماعون", 7, "Meccan", 602, 30),
    (108, "الكوثر", 3, "Meccan", 602, 30),
    (109, "الكافرون", 6, "Meccan", 603, 30),
    (110, "النصر", 3, "Medinan", 603, 30),
    (111, "المسد", 5, "Meccan", 603, 30),
    (112, "الإخلاص", 4, "Meccan", 604, 30),
    (113, "الفلق", 5, "Meccan", 604, 30),
    (114, "الناس", 6, "Meccan", 604, 30),
]

class Command(BaseCommand):
    help = "بذر البيانات التجريبية والتأسيسية للمنظومة القرآنية"

    def handle(self, *args, **options):
        self.stdout.write("جاري إدخال سور القرآن الكريم الـ 114...")
        for num, name, count, place, page, juz in SURAH_DATA:
            Surah.objects.update_or_create(
                number=num,
                defaults={
                    'name_arabic': name,
                    'ayah_count': count,
                    'revelation_place': place,
                    'start_page': page,
                    'juz_number': juz
                }
            )

        self.stdout.write("جاري إنشاء معايير جدول التقييم...")
        criteria = [
            ("جودة الحفظ والضبط", "MEMORIZATION", 10.0, "تقييم عدم النسيان والتردد وحسن الاستحضار", 1),
            ("أحكام التجويد ومخارج الحروف", "TAJWEED", 10.0, "مراعاة أحكام النون الساكنة والتنوين والمدود والمخارج والصفات", 2),
            ("الترتيل والوقف والابتداء", "FLUENCY", 5.0, "جمال الصوت والتأني والوقوف التام والكافي", 3),
            ("الآداب والسلوك القرآني", "DISCIPLINE", 5.0, "الانضباط بالزي والحضور والهدوء داخل الحلقة", 4),
        ]
        for name, code, max_s, desc, order in criteria:
            EvaluationCriterion.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'max_score': max_s,
                    'description': desc,
                    'sort_order': order,
                    'is_active': True
                }
            )

        self.stdout.write("جاري إنشاء المستخدمين التجريبيين (إدارة، شيوخ، طلاب)...")
        # 1. Admin
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                'first_name': "عبد الرحمن",
                'last_name': "السعدي",
                'email': "admin@quran-academy.org",
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': "0501112233"
            }
        )
        admin_user.set_password("admin123")
        admin_user.save()

        # 2. Shuyookh
        sheikh1, _ = User.objects.get_or_create(
            username="sheikh_ahmed",
            defaults={
                'first_name': "أحمد",
                'last_name': "المنشاوي",
                'email': "ahmed.minshawi@quran.org",
                'role': User.Role.TEACHER,
                'phone_number': "0559988771",
                'qualification': "ماجستير القراءات والدراسات القرآنية",
                'years_of_experience': 14,
                'ijazah_details': "إجازة بالسند المتصل بالقراءات العشر الصغرى والكبرى عن كبار قراء الشام ومصر"
            }
        )
        sheikh1.set_password("sheikh123")
        sheikh1.save()

        sheikh2, _ = User.objects.get_or_create(
            username="sheikh_mahmoud",
            defaults={
                'first_name': "محمود",
                'last_name': "الحصري",
                'email': "mahmoud.hosary@quran.org",
                'role': User.Role.TEACHER,
                'phone_number': "0559988772",
                'qualification': "بكالوريوس أصول الدين - قسم التفسير وعلومه",
                'years_of_experience': 9,
                'ijazah_details': "إجازة بروايتي حفص وشعبة عن عاصم، ورواية قالون عن نافع"
            }
        )
        sheikh2.set_password("sheikh123")
        sheikh2.save()

        sheikh3, _ = User.objects.get_or_create(
            username="sheikh_uthman",
            defaults={
                'first_name': "عثمان",
                'last_name': "الصالح",
                'email': "uthman.saleh@quran.org",
                'role': User.Role.TEACHER,
                'phone_number': "0559988773",
                'qualification': "دبلوم معاهد معلمات وإقراء القرآن الكريم",
                'years_of_experience': 6,
                'ijazah_details': "إجازة برواية حفص عن عاصم بالسند المتصل إلى رسول الله صلى الله عليه وسلم"
            }
        )
        sheikh3.set_password("sheikh123")
        sheikh3.save()

        # 3. Students
        students_data = [
            ("student_omar", "عمر", "عبد الرحمن البشير", "عبد الرحمن البشير", "0541112221", "أب", "حافظ لـ 15 جزءاً"),
            ("student_ali", "علي", "محمد الفاسي", "محمد الفاسي", "0541112222", "أب", "حافظ لـ 20 جزءاً"),
            ("student_youssef", "يوسف", "خالد القحطاني", "خالد القحطاني", "0541112223", "أب", "حافظ لـ 5 أجزاء"),
            ("student_anas", "أنس", "بلال التميمي", "بلال التميمي", "0541112224", "أب", "حافظ لـ 7 أجزاء"),
            ("student_hamza", "حمزة", "إبراهيم النجار", "إبراهيم النجار", "0541112225", "أب", "جزء عم وتبارك"),
            ("student_zaid", "زيد", "عبد الله الدوسري", "عبد الله الدوسري", "0541112226", "أب", "مبتدئ - جزء عم"),
        ]

        students_objs = []
        for uname, fname, lname, gname, gphone, grel, level in students_data:
            s_user, _ = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'role': User.Role.STUDENT,
                    'guardian_name': gname,
                    'guardian_phone': gphone,
                    'guardian_relation': grel,
                    'current_memorization_level': level,
                    'phone_number': gphone
                }
            )
            s_user.set_password("student123")
            s_user.save()
            students_objs.append(s_user)

        self.stdout.write("جاري إنشاء الحلقات والمجموعات القرآنية...")
        h1, _ = Halaqah.objects.get_or_create(
            name="حلقة الإمام الشاطبي (المتقنون والمجازون)",
            defaults={
                'teacher': sheikh1,
                'category': Halaqah.Category.KHATMAH,
                'days_schedule': "السبت، الإثنين، الأربعاء",
                'time_period': Halaqah.TimePeriod.ASR,
                'time_detail': "4:30 م - 6:00 م",
                'room_location': "قاعة الترتيل الكبرى - الدور الأول",
                'max_students': 12,
                'description': "حلقة مخصصة للمراجعة الكبرى والإتقان وتثبيت الأجزاء وضبط المتون"
            }
        )

        h2, _ = Halaqah.objects.get_or_create(
            name="حلقة نافع المدني (الحفظ والتأسيس)",
            defaults={
                'teacher': sheikh2,
                'category': Halaqah.Category.GENERAL,
                'days_schedule': "الأحد، الثلاثاء، الخميس",
                'time_period': Halaqah.TimePeriod.MAGHRIB,
                'time_detail': "6:15 م - 7:45 م",
                'room_location': "جناح الحلقات - القاعة رقم 3",
                'max_students': 15,
                'description': "تأسيس الحفظ الجديد وضبط مخارج الحروف وأحكام التجويد"
            }
        )

        h3, _ = Halaqah.objects.get_or_create(
            name="حلقة براعم النور (الناشئة والتلقين)",
            defaults={
                'teacher': sheikh3,
                'category': Halaqah.Category.CHILDREN,
                'days_schedule': "السبت، الإثنين، الأربعاء",
                'time_period': Halaqah.TimePeriod.ASR,
                'time_detail': "4:00 م - 5:15 م",
                'room_location': "قاعة البراعم الذكية",
                'max_students': 10,
                'description': "تلقين قصار السور للبراعم والناشئة مع تعليم آداب القرآن"
            }
        )

        self.stdout.write("جاري توثيق سجلات القيد والانتقال التاريخية للطلاب...")
        # الطالب عمر: كان سابقاً في حلقة نافع المدني مع الشيخ محمود، ثم نُقل إلى حلقة الشاطبي مع الشيخ أحمد!
        omar = students_objs[0]
        # سجل تاريخي سابق
        past_date_start = timezone.now().date() - datetime.timedelta(days=180)
        past_date_end = timezone.now().date() - datetime.timedelta(days=45)
        EnrollmentHistory.objects.get_or_create(
            student=omar,
            halaqah=h2,
            assigned_sheikh=sheikh2,
            start_date=past_date_start,
            defaults={
                'status': EnrollmentHistory.Status.TRANSFERRED,
                'end_date': past_date_end,
                'notes': "أتم حفظ 10 أجزاء بتفوق واجتاز اختبار الترقية، ونُقل بتوصية الشيخ محمود إلى حلقة الشاطبي للإتقان",
                'created_by': admin_user
            }
        )
        # القيد الحالي لعمر في حلقة الشاطبي
        EnrollmentHistory.objects.get_or_create(
            student=omar,
            halaqah=h1,
            assigned_sheikh=sheikh1,
            start_date=past_date_end + datetime.timedelta(days=1),
            defaults={
                'status': EnrollmentHistory.Status.ACTIVE,
                'notes': "التحاق بالحلقة بعد اجتياز متطلبات النقل",
                'created_by': admin_user
            }
        )

        # الطالب علي: نشط في حلقة الشاطبي
        EnrollmentHistory.objects.get_or_create(
            student=students_objs[1],
            halaqah=h1,
            assigned_sheikh=sheikh1,
            start_date=timezone.now().date() - datetime.timedelta(days=120),
            defaults={'status': EnrollmentHistory.Status.ACTIVE, 'created_by': admin_user}
        )

        # الطالب يوسف: نشط في حلقة نافع
        EnrollmentHistory.objects.get_or_create(
            student=students_objs[2],
            halaqah=h2,
            assigned_sheikh=sheikh2,
            start_date=timezone.now().date() - datetime.timedelta(days=90),
            defaults={'status': EnrollmentHistory.Status.ACTIVE, 'created_by': admin_user}
        )

        # الطالب أنس: نشط في حلقة نافع
        EnrollmentHistory.objects.get_or_create(
            student=students_objs[3],
            halaqah=h2,
            assigned_sheikh=sheikh2,
            start_date=timezone.now().date() - datetime.timedelta(days=60),
            defaults={'status': EnrollmentHistory.Status.ACTIVE, 'created_by': admin_user}
        )

        # الطالب حمزة: نشط في حلقة براعم النور
        EnrollmentHistory.objects.get_or_create(
            student=students_objs[4],
            halaqah=h3,
            assigned_sheikh=sheikh3,
            start_date=timezone.now().date() - datetime.timedelta(days=40),
            defaults={'status': EnrollmentHistory.Status.ACTIVE, 'created_by': admin_user}
        )

        # الطالب زيد: نشط في حلقة براعم النور
        EnrollmentHistory.objects.get_or_create(
            student=students_objs[5],
            halaqah=h3,
            assigned_sheikh=sheikh3,
            start_date=timezone.now().date() - datetime.timedelta(days=30),
            defaults={'status': EnrollmentHistory.Status.ACTIVE, 'created_by': admin_user}
        )

        self.stdout.write("جاري إنشاء عينات من سجلات الحضور والغياب والتأخير بعذر وغير عذر...")
        today = timezone.now().date()
        surah_kahf = Surah.objects.get(number=18)
        surah_maryam = Surah.objects.get(number=19)
        surah_baqarah = Surah.objects.get(number=2)
        surah_mulk = Surah.objects.get(number=67)

        # تسجيل حضور الأسبوعين الأخيرين لحلقة الشاطبي (الشيخ أحمد)
        days_offset = [0, 2, 4, 7, 9, 11]
        for offset in days_offset:
            d = today - datetime.timedelta(days=offset)
            
            # عمر: حاضر في أغلب الأيام، ويوم متأخر بعذر
            if offset == 4:
                status = AttendanceRecord.Status.LATE_EXCUSED
                delay = 20
                notes = "تأخر بسبب ظروف المواصلات واعتذر مسبقاً"
            elif offset == 11:
                status = AttendanceRecord.Status.ABSENT_EXCUSED
                delay = 0
                notes = "إجازة مرضية مع إشعار مسبق من ولي الأمر"
            else:
                status = AttendanceRecord.Status.PRESENT
                delay = 0
                notes = "حضور مبكر ومنتظم"

            AttendanceRecord.objects.get_or_create(
                student=omar,
                halaqah=h1,
                date=d,
                defaults={
                    'sheikh': sheikh1,
                    'status': status,
                    'delay_minutes': delay,
                    'notes': notes
                }
            )

            # علي: حاضر مع تأخير بدون عذر في أحد الأيام
            if offset == 2:
                status_ali = AttendanceRecord.Status.LATE_UNEXCUSED
                delay_ali = 15
                notes_ali = "تأخر 15 دقيقة بدون إشعار أو عذر"
            elif offset == 9:
                status_ali = AttendanceRecord.Status.ABSENT_UNEXCUSED
                delay_ali = 0
                notes_ali = "غياب غير مبرر، تم إشعار الإدارة"
            else:
                status_ali = AttendanceRecord.Status.PRESENT
                delay_ali = 0
                notes_ali = "حاضر متفاعل"

            AttendanceRecord.objects.get_or_create(
                student=students_objs[1],
                halaqah=h1,
                date=d,
                defaults={
                    'sheikh': sheikh1,
                    'status': status_ali,
                    'delay_minutes': delay_ali,
                    'notes': notes_ali
                }
            )

        # عينات تسميع وتقييم لعمر في حلقة الشاطبي
        RecitationSession.objects.get_or_create(
            student=omar,
            halaqah=h1,
            sheikh=sheikh1,
            date=today,
            defaults={
                'recitation_type': RecitationSession.RecitationType.NEW_MEMORIZATION,
                'surah_from': surah_kahf,
                'ayah_from': 1,
                'surah_to': surah_kahf,
                'ayah_to': 25,
                'pages_completed': 2.5,
                'score_memorization': 9.5,
                'score_tajweed': 9.0,
                'score_fluency': 5.0,
                'score_discipline': 5.0,
                'hesitations_count': 1,
                'major_mistakes': 0,
                'minor_mistakes': 1,
                'sheikh_notes': "ما شاء الله، إتقان ممتاز واستحضار قوي للآيات مع ترتيل ندي",
                'next_assignment': "سورة الكهف من آية 26 إلى 50 مع مراجعة أول 5 أجزاء"
            }
        )

        RecitationSession.objects.get_or_create(
            student=omar,
            halaqah=h1,
            sheikh=sheikh1,
            date=today - datetime.timedelta(days=2),
            defaults={
                'recitation_type': RecitationSession.RecitationType.NEAR_REVISION,
                'surah_from': surah_maryam,
                'ayah_from': 1,
                'surah_to': surah_maryam,
                'ayah_to': 40,
                'pages_completed': 3.0,
                'score_memorization': 10.0,
                'score_tajweed': 9.5,
                'score_fluency': 5.0,
                'score_discipline': 5.0,
                'hesitations_count': 0,
                'major_mistakes': 0,
                'minor_mistakes': 0,
                'sheikh_notes': "قراءة نموذجية متقنة تبارك الرحمن، ممتاز مرتفع",
                'next_assignment': "إكمال سورة مريم حتى نهايتها"
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Data seeding completed successfully!"))
