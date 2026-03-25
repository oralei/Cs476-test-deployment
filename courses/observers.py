# courses/observers.py
# Update: Follows closer to Refactoring.guru's version

# We use abc for the Interface observer and subject classes. It is the Python equivalent.
from abc import ABC, abstractmethod
from courses.models import Notification

# --------- Added for acceptance testing ----------
import time
from functools import wraps 
def measure_performance(max_ms_allowed):
    """
    Decorator to measure function execution time and print it to the console.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            
            duration_ms = (end - start) * 1000
            status = "PASS" if duration_ms <= max_ms_allowed else "FAIL"
            
            print(f"\n--- PERFORMANCE TEST [{status}] ---")
            print(f"Function: {func.__name__}")
            print(f"Time Taken: {duration_ms:.2f} ms")
            print(f"Threshold:  {max_ms_allowed} ms")
            print("----------------------------------\n")
            
            return result
        return wrapper
    return decorator


"""
<<Interface>> Subject
Purpose: Declares a set of methods for managing subscribers. Structure from Refactoring.Guru
         Take note that this is an abstract class, so no implementation is given for the methods.
"""
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        # Attach an observer to the subject.
        pass

    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        # Detatch an observer to the subject.
        pass

    @abstractmethod
    def notify(self) -> None:
        # Notify all observers about an event.
        pass

# <<Interface>> Observer
class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass

"""
SubmissionSubject (Concrete Subject implementation)
Purpose: This detects when a TaskSubmission is made/edited/changed and informs the attached
         observers that changes have been made.
"""
class SubmissionSubject(Subject):
    def __init__(self, submission):
        self._observers = []
        self.submission = submission
        self._state = submission.status # 'pending' or 'reviewed'

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            # Passing 'self' matches Refactoring.guru exactly
            observer.update(self)

    # Getter method for Pull Strategy
    @measure_performance(max_ms_allowed=200) # For acceptance testing
    def get_state(self):
        return {
            'status': self._state,
            'task_title': self.submission.task.title,
            'student': self.submission.student,
            'teacher': self.submission.task.course.teacher
        }

    # The "Business Logic" that triggers the notification, used in views.py and sets values for subject
    # This is utilized for the Pull Strategy as the subject now has updated values for the observers to pull (use).
    def set_state(self, new_status):
        self._state = new_status
        self.submission.status = new_status
        self.submission.save() # Save to database
        self.notify() # Trigger the observers!

"""
SubmissionObserver (ConcreteObserver Teacher Side)
Purpose: Creates a notification object for the teacher when needing an update.
         We are using the pull strategy, as the observers are "pulling" data passed from the Subject.
"""
class SubmissionObserver(Observer):
    def update(self, subject: Subject) -> None:
        # PULL STRATEGY: Pulling state from the subject
        state = subject.get_state()
        
        if state['status'] == 'pending':
            teacher = state['teacher']
            student = state['student']
            task_title = state['task_title']
            
            # Debug print:
            print(f"NOTIFY TEACHER {teacher}: {student.full_name} submitted a task!")
            
            # Create a Notification database object here.
            Notification.objects.create(
                user=teacher.user, # The teacher receives this
                message=f"{student.full_name} task “{task_title}” Needs feedback!"
            )

"""
FeedbackObserver (ConcreteObserver Student Side)
Purpose: Creates a notification object for the student when needing an update.
"""
class FeedbackObserver(Observer):
    def update(self, subject: Subject) -> None:
        # PULL STRATEGY: Pulling state from the subject
        state = subject.get_state()
        
        if state['status'] == 'reviewed':
            student = state['student']
            task_title = state['task_title']
            
            # Debug print:
            print(f"NOTIFY STUDENT {student}: Your task '{task_title}' has been given feedback!")
            
            # Create a Notification database object here.
            Notification.objects.create(
                user=student.user, # The student receives this
                message=f"Your task “{task_title}” has new feedback!"
            )