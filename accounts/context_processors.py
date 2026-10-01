def academy_context(request):
    """
    سياق عام للمنظومة القرآنية:
    - يوفر إعدادات المنشأة (الاسم، الشعار، بيانات التواصل) لكل الصفحات والتقارير
    - يسهل فحص الأدوار والوصول لبيانات النظام
    """
    from academy.org_settings import OrganizationSettings

    # جلب إعدادات المنشأة (مع التحقق من إنشاء الجداول)
    try:
        org = OrganizationSettings.get_settings()
    except Exception:
        org = None

    user = request.user
    if user.is_authenticated:
        return {
            'is_admin': user.is_admin_role,
            'is_teacher': user.is_teacher_role,
            'is_student': user.is_student_role,
            'current_user': user,
            'org': org,
            # اختصارات مباشرة للاستخدام في القوالب
            'academy_name': org.name if org else 'منظومة صرح القرآن',
            'academy_slogan': org.slogan if org else 'المنظومة التعليمية لإدارة الحلقات',
            'academy_icon_letter': org.logo_icon_letter if org else 'ق',
        }
    return {
        'is_admin': False,
        'is_teacher': False,
        'is_student': False,
        'current_user': None,
        'org': org,
        'academy_name': org.name if org else 'منظومة صرح القرآن',
        'academy_slogan': org.slogan if org else 'المنظومة التعليمية لإدارة الحلقات',
        'academy_icon_letter': org.logo_icon_letter if org else 'ق',
    }
