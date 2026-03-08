# courses/observers.py
# Update: Follows closer to Refactoring.guru's version

# We use abc for the Interface observer and subject classes. It is the Python equivalent.
from abc import ABC, abstractmethod
from courses.models import Notification

# <<Interface>> Subject
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        pass

    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass

# <<Interface>> Observer
class Observer(ABC):
    @abstractmethod
    def update(self, subject: Subject) -> None:
        pass

# ConcreteSubject
# Purpose: This detects when a TaskSubmission is made/edited/changed
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
    def get_state(self):
        return {
            'status': self._state,
            'task_title': self.submission.task.title,
            'student': self.submission.student,
            'teacher': self.submission.task.course.teacher
        }

    # The "Business Logic" that triggers the notification
    def set_state(self, new_status):
        self._state = new_status
        self.submission.status = new_status
        self.submission.save() # Save to database
        self.notify() # Trigger the observers!

# ConcreteObserver 1 (Teacher)
class TeacherObserver(Observer):
    def update(self, subject: Subject) -> None:
        # PULL STRATEGY: Pulling state from the subject
        state = subject.get_state()
        
        if state['status'] == 'pending':
            teacher = state['teacher']
            student = state['student']
            task_title = state['task_title']
            print(f"NOTIFY TEACHER {teacher}: {student.full_name} submitted a task!")
            # Note from Mark: Create a Notification database object here.
            Notification.objects.create(
                user=teacher.user, # The teacher receives this
                message=f"{student.full_name} task “{task_title}” Needs feedback!"
            )

# ConcreteObserver 2 (Student)
class StudentObserver(Observer):
    def update(self, subject: Subject) -> None:
        # PULL STRATEGY: Pulling state from the subject
        state = subject.get_state()
        
        if state['status'] == 'reviewed':
            student = state['student']
            task_title = state['task_title']
            print(f"NOTIFY STUDENT {student}: Your task '{task_title}' is graded!")
            # Note from Mark: Create a Notification database object here.
            Notification.objects.create(
                user=student.user, # The student receives this
                message=f"Your task “{task_title}” has new feedback!"
            )