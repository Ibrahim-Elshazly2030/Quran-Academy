from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from accounts.models import User
from academy.models import Halaqah, EnrollmentHistory
from attendance.models import AttendanceRecord
from evaluations.models import RecitationSession

def get_student_comprehensive_data(student_id):
    """
    استخراج السجل التاريخي الشامل الكامل للطالب متضمناً:
    - بيانات الطالب وولي أمره
    - سجل المجموعات والشيوخ عبر تاريخ التحاقه
    - إحصائيات الحضور والغياب والتأخير (بعذر وبدون عذر)
    - سجل التسميع والتقييمات ودرجات التجويد والحفظ
    """
    try:
        student = User.objects.get(id=student_id, role=User.Role.STUDENT)
    except User.DoesNotExist:
        return None

    # 1. سجل المجموعات والشيوخ التاريخي الكامل
    enrollments = EnrollmentHistory.objects.filter(student=student).select_related(
        'halaqah', 'assigned_sheikh', 'created_by'
    ).order_by('-start_date')

    # الحلقة الحالية
    current_enrollment = enrollments.filter(status=EnrollmentHistory.Status.ACTIVE).first()
    current_halaqah = current_enrollment.halaqah if current_enrollment else None
    current_sheikh = current_enrollment.assigned_sheikh or (current_halaqah.teacher if current_halaqah else None)

    # 2. إحصائيات الحضور والغياب والتأخير
    attendance_qs = AttendanceRecord.objects.filter(student=student).select_related('halaqah', 'sheikh').order_by('-date')
    total_sessions = attendance_qs.count()

    present_count = attendance_qs.filter(status=AttendanceRecord.Status.PRESENT).count()
    absent_excused_count = attendance_qs.filter(status=AttendanceRecord.Status.ABSENT_EXCUSED).count()
    absent_unexcused_count = attendance_qs.filter(status=AttendanceRecord.Status.ABSENT_UNEXCUSED).count()
    late_excused_count = attendance_qs.filter(status=AttendanceRecord.Status.LATE_EXCUSED).count()
    late_unexcused_count = attendance_qs.filter(status=AttendanceRecord.Status.LATE_UNEXCUSED).count()
    left_early_count = attendance_qs.filter(status=AttendanceRecord.Status.EXCUSED_LEAVE).count()

    total_delays = attendance_qs.aggregate(total_delay=Sum('delay_minutes'))['total_delay'] or 0

    positive_attendance = present_count + late_excused_count
    attendance_rate = round((positive_attendance / total_sessions * 100), 1) if total_sessions > 0 else 100.0

    # 3. سجل التسميع والتقييمات القرآنية
    recitations_qs = RecitationSession.objects.filter(student=student).select_related(
        'halaqah', 'sheikh', 'surah_from', 'surah_to'
    ).order_by('-date', '-created_at')

    total_recitations = recitations_qs.count()
    total_pages = recitations_qs.aggregate(pages=Sum('pages_completed'))['pages'] or 0.0

    avg_memo = recitations_qs.aggregate(avg=Avg('score_memorization'))['avg'] or 0.0
    avg_tajweed = recitations_qs.aggregate(avg=Avg('score_tajweed'))['avg'] or 0.0
    avg_percentage = recitations_qs.aggregate(avg=Avg('percentage'))['avg'] or 0.0

    grades_distribution = {
        'A_PLUS': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.EXCELLENT_PLUS).count(),
        'A': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.EXCELLENT).count(),
        'B': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.VERY_GOOD).count(),
        'C': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.GOOD).count(),
        'D': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.ACCEPTABLE).count(),
        'F': recitations_qs.filter(rating_grade=RecitationSession.RatingGrade.NEEDS_REPETITION).count(),
    }

    return {
        'student': student,
        'current_halaqah': current_halaqah,
        'current_sheikh': current_sheikh,
        'enrollments': enrollments,
        'attendance_stats': {
            'total_sessions': total_sessions,
            'present_count': present_count,
            'absent_excused_count': absent_excused_count,
            'absent_unexcused_count': absent_unexcused_count,
            'late_excused_count': late_excused_count,
            'late_unexcused_count': late_unexcused_count,
            'left_early_count': left_early_count,
            'total_delay_minutes': total_delays,
            'attendance_rate': attendance_rate,
        },
        'attendance_history': attendance_qs[:30],
        'recitation_stats': {
            'total_recitations': total_recitations,
            'total_pages': round(float(total_pages), 1),
            'avg_memorization': round(float(avg_memo), 1),
            'avg_tajweed': round(float(avg_tajweed), 1),
            'avg_percentage': round(float(avg_percentage), 1),
            'grades_distribution': grades_distribution,
        },
        'recitations_history': recitations_qs,
    }


def get_sheikh_comprehensive_data(sheikh_id):
    """
    استخراج السجل التاريخي الشامل للشيخ متضمناً:
    - بيانات الشيخ ومؤهلاته وسند إجازاته
    - الحلقات والمجموعات الحالية والسابقة
    - الطلاب الذين درسهم حالياً وسابقاً
    - مؤشرات الحضور والتسميع لحلقاته
    """
    try:
        sheikh = User.objects.get(id=sheikh_id, role=User.Role.TEACHER)
    except User.DoesNotExist:
        return None

    # الحلقات الحالية المشرف عليها
    halaqat = Halaqah.objects.filter(teacher=sheikh).order_by('-is_active', 'name')
    active_halaqat = halaqat.filter(is_active=True)

    # الطلاب الحاليون في جميع حلقاته النشطة
    active_enrollments = EnrollmentHistory.objects.filter(
        halaqah__in=active_halaqat,
        status=EnrollmentHistory.Status.ACTIVE
    ).select_related('student', 'halaqah').order_by('halaqah__name', 'student__first_name')

    # جميع الطلاب عبر التاريخ (بما في ذلك من تخرج أو انتقل)
    all_historical_enrollments = EnrollmentHistory.objects.filter(
        Q(assigned_sheikh=sheikh) | Q(halaqah__teacher=sheikh)
    ).select_related('student', 'halaqah').order_by('-start_date')

    total_distinct_students = all_historical_enrollments.values('student').distinct().count()

    # سجلات الحضور التي رصدها الشيخ
    attendance_records = AttendanceRecord.objects.filter(
        Q(sheikh=sheikh) | Q(halaqah__teacher=sheikh)
    )
    total_attendance_marked = attendance_records.count()
    present_marked = attendance_records.filter(status=AttendanceRecord.Status.PRESENT).count()
    sheikh_group_attendance_rate = round((present_marked / total_attendance_marked * 100), 1) if total_attendance_marked > 0 else 100.0

    # جلسات التقييم والتسميع التي نفذها الشيخ
    recitations = RecitationSession.objects.filter(
        Q(sheikh=sheikh) | Q(halaqah__teacher=sheikh)
    ).select_related('student', 'halaqah', 'surah_from', 'surah_to').order_by('-date')

    total_recitations_evaluated = recitations.count()
    total_pages_listened = recitations.aggregate(pages=Sum('pages_completed'))['pages'] or 0.0
    avg_grade_given = recitations.aggregate(avg=Avg('percentage'))['avg'] or 0.0

    return {
        'sheikh': sheikh,
        'halaqat': halaqat,
        'active_halaqat_count': active_halaqat.count(),
        'active_students_count': active_enrollments.count(),
        'total_distinct_students': total_distinct_students,
        'active_enrollments': active_enrollments,
        'historical_enrollments': all_historical_enrollments[:50],
        'total_attendance_marked': total_attendance_marked,
        'attendance_rate': sheikh_group_attendance_rate,
        'total_recitations_evaluated': total_recitations_evaluated,
        'total_pages_listened': round(float(total_pages_listened), 1),
        'avg_grade_given': round(float(avg_grade_given), 1),
        'recent_recitations': recitations[:25],
    }


def get_academy_overview_stats():
    """إحصائيات المنظومة العامة للإدارة"""
    total_students = User.objects.filter(role=User.Role.STUDENT, is_active=True).count()
    total_sheikhs = User.objects.filter(role=User.Role.TEACHER, is_active=True).count()
    total_halaqat = Halaqah.objects.filter(is_active=True).count()
    total_recitations = RecitationSession.objects.count()
    total_pages = RecitationSession.objects.aggregate(p=Sum('pages_completed'))['p'] or 0.0

    # نسبة حضور اليوم
    today = timezone.now().date()
    today_records = AttendanceRecord.objects.filter(date=today)
    today_total = today_records.count()
    today_present = today_records.filter(status__in=[AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE_EXCUSED]).count()
    today_rate = round((today_present / today_total * 100), 1) if today_total > 0 else 0.0

    return {
        'total_students': total_students,
        'total_sheikhs': total_sheikhs,
        'total_halaqat': total_halaqat,
        'total_recitations': total_recitations,
        'total_pages': round(float(total_pages), 1),
        'today_attendance_total': today_total,
        'today_attendance_present': today_present,
        'today_attendance_rate': today_rate,
    }
