from datetime import datetime, timezone
from functools import lru_cache

def calculate_grade(marks, system='pakistan'):
    marks = float(marks)
    if system == 'pakistan':
        if marks >= 85:   return {'grade': 'A+', 'gpa': 4.0, 'letter': 'A+', 'status': 'Excellent'}
        elif marks >= 80: return {'grade': 'A',  'gpa': 4.0, 'letter': 'A',  'status': 'Excellent'}
        elif marks >= 75: return {'grade': 'A-', 'gpa': 3.7, 'letter': 'A-', 'status': 'Very Good'}
        elif marks >= 71: return {'grade': 'B+', 'gpa': 3.3, 'letter': 'B+', 'status': 'Good'}
        elif marks >= 68: return {'grade': 'B',  'gpa': 3.0, 'letter': 'B',  'status': 'Good'}
        elif marks >= 64: return {'grade': 'B-', 'gpa': 2.7, 'letter': 'B-', 'status': 'Above Average'}
        elif marks >= 61: return {'grade': 'C+', 'gpa': 2.3, 'letter': 'C+', 'status': 'Average'}
        elif marks >= 58: return {'grade': 'C',  'gpa': 2.0, 'letter': 'C',  'status': 'Average'}
        elif marks >= 54: return {'grade': 'C-', 'gpa': 1.7, 'letter': 'C-', 'status': 'Below Average'}
        elif marks >= 50: return {'grade': 'D',  'gpa': 1.0, 'letter': 'D',  'status': 'Pass'}
        else:             return {'grade': 'F',  'gpa': 0.0, 'letter': 'F',  'status': 'Fail'}
    elif system == 'usa':
        if marks >= 93:   return {'grade': 'A',  'gpa': 4.0, 'letter': 'A',  'status': 'Excellent'}
        elif marks >= 90: return {'grade': 'A-', 'gpa': 3.7, 'letter': 'A-', 'status': 'Excellent'}
        elif marks >= 87: return {'grade': 'B+', 'gpa': 3.3, 'letter': 'B+', 'status': 'Good'}
        elif marks >= 83: return {'grade': 'B',  'gpa': 3.0, 'letter': 'B',  'status': 'Good'}
        elif marks >= 80: return {'grade': 'B-', 'gpa': 2.7, 'letter': 'B-', 'status': 'Good'}
        elif marks >= 77: return {'grade': 'C+', 'gpa': 2.3, 'letter': 'C+', 'status': 'Average'}
        elif marks >= 73: return {'grade': 'C',  'gpa': 2.0, 'letter': 'C',  'status': 'Average'}
        elif marks >= 70: return {'grade': 'C-', 'gpa': 1.7, 'letter': 'C-', 'status': 'Average'}
        elif marks >= 60: return {'grade': 'D',  'gpa': 1.0, 'letter': 'D',  'status': 'Pass'}
        else:             return {'grade': 'F',  'gpa': 0.0, 'letter': 'F',  'status': 'Fail'}
    elif system == 'uk':
        if marks >= 70:   return {'grade': 'First',        'gpa': 4.0, 'letter': '1st', 'status': 'Excellent'}
        elif marks >= 60: return {'grade': 'Upper Second', 'gpa': 3.3, 'letter': '2:1', 'status': 'Very Good'}
        elif marks >= 50: return {'grade': 'Lower Second', 'gpa': 2.7, 'letter': '2:2', 'status': 'Good'}
        elif marks >= 40: return {'grade': 'Third',        'gpa': 2.0, 'letter': '3rd', 'status': 'Pass'}
        else:             return {'grade': 'Fail',         'gpa': 0.0, 'letter': 'F',   'status': 'Fail'}
    elif system == 'india':
        if marks >= 90:   return {'grade': 'O',  'gpa': 10.0, 'letter': 'O',  'status': 'Outstanding'}
        elif marks >= 80: return {'grade': 'A+', 'gpa': 9.0,  'letter': 'A+', 'status': 'Excellent'}
        elif marks >= 70: return {'grade': 'A',  'gpa': 8.0,  'letter': 'A',  'status': 'Very Good'}
        elif marks >= 60: return {'grade': 'B+', 'gpa': 7.0,  'letter': 'B+', 'status': 'Good'}
        elif marks >= 50: return {'grade': 'B',  'gpa': 6.0,  'letter': 'B',  'status': 'Average'}
        elif marks >= 40: return {'grade': 'C',  'gpa': 5.0,  'letter': 'C',  'status': 'Pass'}
        else:             return {'grade': 'F',  'gpa': 0.0,  'letter': 'F',  'status': 'Fail'}
    elif system == 'germany':
        if marks >= 95:   return {'grade': '1.0', 'gpa': 4.0, 'letter': 'A', 'status': 'Sehr Gut'}
        elif marks >= 90: return {'grade': '1.3', 'gpa': 3.7, 'letter': 'A', 'status': 'Sehr Gut'}
        elif marks >= 85: return {'grade': '1.7', 'gpa': 3.3, 'letter': 'B', 'status': 'Gut'}
        elif marks >= 80: return {'grade': '2.0', 'gpa': 3.0, 'letter': 'B', 'status': 'Gut'}
        elif marks >= 75: return {'grade': '2.3', 'gpa': 2.7, 'letter': 'B', 'status': 'Gut'}
        elif marks >= 70: return {'grade': '2.7', 'gpa': 2.3, 'letter': 'C', 'status': 'Befriedigend'}
        elif marks >= 65: return {'grade': '3.0', 'gpa': 2.0, 'letter': 'C', 'status': 'Befriedigend'}
        elif marks >= 60: return {'grade': '3.3', 'gpa': 1.7, 'letter': 'C', 'status': 'Befriedigend'}
        elif marks >= 50: return {'grade': '4.0', 'gpa': 1.0, 'letter': 'D', 'status': 'Ausreichend'}
        else:             return {'grade': '5.0', 'gpa': 0.0, 'letter': 'F', 'status': 'Nicht Bestanden'}
    elif system == 'australia':
        if marks >= 85:   return {'grade': 'HD', 'gpa': 4.0, 'letter': 'HD', 'status': 'High Distinction'}
        elif marks >= 75: return {'grade': 'D',  'gpa': 3.0, 'letter': 'D',  'status': 'Distinction'}
        elif marks >= 65: return {'grade': 'C',  'gpa': 2.0, 'letter': 'C',  'status': 'Credit'}
        elif marks >= 50: return {'grade': 'P',  'gpa': 1.0, 'letter': 'P',  'status': 'Pass'}
        else:             return {'grade': 'F',  'gpa': 0.0, 'letter': 'F',  'status': 'Fail'}
    else:
        return {'error': 'Unknown grading system'}

def what_if_simulator(subjects_data, system='pakistan'):
    total_points = 0
    total_credits = 0
    breakdown = []
    for subj in subjects_data:
        marks      = float(subj.get('marks', 0))
        credits    = int(subj.get('credit_hrs', 3))
        grade_info = calculate_grade(marks, system)
        gpa        = grade_info.get('gpa', 0)
        total_points  += gpa * credits
        total_credits += credits
        breakdown.append({
            'subject':    subj.get('name', 'Subject'),
            'marks':      marks,
            'grade':      grade_info.get('grade'),
            'gpa_points': gpa,
            'credits':    credits
        })
    predicted_gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    return {
        'predicted_gpa': predicted_gpa,
        'total_credits': total_credits,
        'system':        system,
        'breakdown':     breakdown
    }

def exam_countdown(exam_date_str):
    try:
        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
        exam_date = exam_date.replace(tzinfo=timezone.utc)
        now       = datetime.now(timezone.utc)
        diff      = exam_date - now
        if diff.total_seconds() < 0:
            return {'status': 'past', 'message': 'Exam date has passed!'}
        total_seconds = int(diff.total_seconds())
        days    = diff.days
        hours   = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600)  // 60
        if days <= 3:    urgency = 'critical'
        elif days <= 7:  urgency = 'high'
        elif days <= 14: urgency = 'medium'
        else:            urgency = 'low'
        return {
            'days': days, 'hours': hours,
            'minutes': minutes, 'urgency': urgency,
            'message': f'{days} days, {hours} hours, {minutes} minutes remaining'
        }
    except Exception as e:
        return {'error': str(e)}

def performance_analytics(semesters):
    labels = [s.name for s in semesters]
    gpas   = [s.gpa  for s in semesters]
    cgpas  = [s.cgpa for s in semesters]
    trend = 'stable'
    if len(gpas) >= 2:
        if gpas[-1] > gpas[-2]:   trend = 'improving'
        elif gpas[-1] < gpas[-2]: trend = 'declining'
    return {
        'labels': labels,
        'datasets': {
            'gpa_trend':  {'label': 'GPA per Semester',  'data': gpas,  'borderColor': '#4F46E5', 'backgroundColor': 'rgba(79,70,229,0.2)'},
            'cgpa_trend': {'label': 'Cumulative CGPA',   'data': cgpas, 'borderColor': '#22C55E', 'backgroundColor': 'rgba(34,197,94,0.2)'}
        },
        'trend': trend,
        'latest_gpa':  gpas[-1]  if gpas  else 0,
        'latest_cgpa': cgpas[-1] if cgpas else 0
    }

TRANSLATIONS = {
    'en': {
        'dashboard': 'Dashboard', 'calculator': 'Grade Calculator',
        'predictor': 'Grade Predictor', 'countdown': 'Exam Countdown',
        'timetable': 'Smart Timetable', 'performance': 'Performance',
        'welcome': 'Welcome to GradeAtlas', 'target_gpa': 'Target GPA',
        'current_gpa': 'Current GPA', 'subject': 'Subject', 'marks': 'Marks',
        'calculate': 'Calculate', 'danger_alert': 'Warning: GPA Dropping!',
        'achieved': 'Target Achieved! 🎉'
    },
    'ur': {
        'dashboard': 'ڈیش بورڈ', 'calculator': 'گریڈ کیلکولیٹر',
        'predictor': 'گریڈ پریڈکٹر', 'countdown': 'امتحان کاؤنٹ ڈاؤن',
        'timetable': 'سمارٹ ٹائم ٹیبل', 'performance': 'کارکردگی',
        'welcome': 'گریڈ ایٹلس میں خوش آمدید', 'target_gpa': 'ہدف جی پی اے',
        'current_gpa': 'موجودہ جی پی اے', 'subject': 'مضمون', 'marks': 'نمبر',
        'calculate': 'حساب کریں', 'danger_alert': 'خبردار: جی پی اے گر رہا ہے!',
        'achieved': 'ہدف حاصل! 🎉'
    },
    'ar': {
        'dashboard': 'لوحة التحكم', 'calculator': 'حاسبة الدرجات',
        'predictor': 'متنبئ الدرجات', 'countdown': 'العد التنازلي للامتحان',
        'timetable': 'الجدول الذكي', 'performance': 'الأداء',
        'welcome': 'مرحباً بك في GradeAtlas', 'target_gpa': 'المعدل المستهدف',
        'current_gpa': 'المعدل الحالي', 'subject': 'المادة', 'marks': 'الدرجات',
        'calculate': 'احسب', 'danger_alert': 'تحذير: المعدل ينخفض!',
        'achieved': 'تم تحقيق الهدف! 🎉'
    }
}

@lru_cache(maxsize=16)
def get_translations(language='en'):
    return TRANSLATIONS.get(language, TRANSLATIONS['en'])

def check_achievement(current_gpa, target_gpa):
    current_gpa = float(current_gpa)
    target_gpa  = float(target_gpa)
    if current_gpa >= target_gpa:
        return {'celebration': True,  'message': '🎉 Congratulations! You reached your target GPA!', 'badge': 'Target Achieved', 'color': '#22C55E'}
    else:
        gap = round(target_gpa - current_gpa, 2)
        return {'celebration': False, 'message': f'You need {gap} more GPA points to reach your target.', 'gap': gap, 'color': '#4F46E5'}

def danger_alert(semesters_gpa_list):
    if len(semesters_gpa_list) < 2:
        return {'alert': False, 'message': 'Not enough data yet'}
    latest   = float(semesters_gpa_list[-1])
    previous = float(semesters_gpa_list[-2])
    drop     = round(previous - latest, 2)
    if drop >= 0.5:   return {'alert': True,  'level': 'critical', 'message': f'🚨 Critical! GPA dropped by {drop} points!', 'color': '#EF4444', 'drop': drop}
    elif drop >= 0.2: return {'alert': True,  'level': 'warning',  'message': f'⚠️ Warning! GPA dropped by {drop} points.',  'color': '#F59E0B', 'drop': drop}
    elif drop > 0:    return {'alert': True,  'level': 'mild',     'message': f'📉 Slight drop of {drop} points.',           'color': '#F59E0B', 'drop': drop}
    else:             return {'alert': False, 'level': 'good',     'message': '✅ GPA stable or improving!',                 'color': '#22C55E', 'drop': 0}

def subject_analysis(subjects):
    strong = []
    weak   = []
    chart_labels = []
    chart_data   = []
    chart_colors = []
    for s in subjects:
        pct = s.percentage()
        chart_labels.append(s.name)
        chart_data.append(pct)
        if pct >= 75:
            strong.append({'name': s.name, 'percentage': pct})
            chart_colors.append('#22C55E')
        elif pct >= 50:
            chart_colors.append('#4F46E5')
        else:
            weak.append({'name': s.name, 'percentage': pct})
            chart_colors.append('#EF4444')
    return {
        'strong_subjects': strong,
        'weak_subjects':   weak,
        'chart': {'labels': chart_labels, 'data': chart_data, 'backgroundColor': chart_colors}
    }

def grade_predictor(current_marks, current_weight, final_weight, target_marks, system='pakistan'):
    current_marks  = float(current_marks)
    current_weight = float(current_weight) / 100
    final_weight   = float(final_weight)   / 100
    target_marks   = float(target_marks)
    earned_so_far  = current_marks * current_weight
    needed         = round((target_marks - earned_so_far) / final_weight, 2)
    if needed > 100:
        message  = '❌ Target not achievable even with 100% in final.'
        possible = False
    elif needed < 0:
        message  = '✅ Target already achieved!'
        possible = True
    else:
        message  = f'You need {needed}% in your final exam to achieve {target_marks}%'
        possible = True
    grade_info = calculate_grade(target_marks, system)
    return {'required_marks': needed, 'possible': possible, 'message': message,
            'target_grade': grade_info.get('grade'), 'target_gpa': grade_info.get('gpa')}

def generate_timetable(subjects):
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sorted_subjects = sorted(subjects, key=lambda s: s.percentage())
    timetable = []
    for i, subj in enumerate(sorted_subjects):
        pct = subj.percentage()
        if pct < 50:    hours = 3.0; priority = 'high'
        elif pct < 75:  hours = 2.0; priority = 'medium'
        else:           hours = 1.0; priority = 'low'
        timetable.append({
            'day': DAYS[i % len(DAYS)],
            'subject_name': subj.name,
            'hours': hours,
            'priority': priority,
            'percentage': pct
        })
    return timetable
