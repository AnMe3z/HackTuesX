from datetime import datetime
import calendar

def generate_calendar_data(tasks):
    calendar_data = []
    today = datetime.today()
    year = today.year
    month = today.month
    cal = calendar.Calendar(firstweekday=0)  # 0: Monday, 6: Sunday
    month_days = cal.monthdayscalendar(year, month)
    for week in month_days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append((None, []))
            else:
                date = datetime(year, month, day)
                day_tasks = [task for task in tasks if task.get('deadline') == date.strftime('%Y-%m-%d')]
                week_data.append((day, day_tasks))
        calendar_data.append(week_data)
    return calendar_data