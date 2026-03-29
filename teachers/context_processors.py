from courses.models import Notification
# Added By Saim Munshi: this code allows notfication db object to be viewed in all  teacher views
# Updated by Mark: Show only unread notifications to fix "remove" button
def notifications_processor(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {'notifications': user_notifications}
    return {'notifications': []}    