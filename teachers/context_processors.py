from courses.models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return {'notifications': user_notifications}
    return {'notifications': []}    