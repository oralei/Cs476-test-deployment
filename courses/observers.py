# courses/observers.py

# Note from Mark: We use abc for the Interface observer and subject classes. It is the Python equivalent.
from abc import ABC, abstractmethod

# <<Interface>> Observer
class Observer(ABC):
    @abstractmethod
    def update(self):
        pass

# <<Interface>> Subject
class Subject(ABC):
    def __init__(self):
        self._observers = [] # This represents the "ObserverList" from the UML

    def register(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer: Observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()

# ConcreteSubject
# Purpose: This detects when a TaskSubmission is made/edited/changed
class SubmissionSubject(Subject):
    def __init__(self, submission):
        super().__init__()
        self.submission = submission # The Django courses/models.py TaskSubmission model instance
        self._subject_state = submission.status # 'pending' or 'reviewed'

    # Matches getState() in UML
    def get_state(self):
        return {
            'status': self._subject_state,
            'task_title': self.submission.task.title,
            'student': self.submission.student,
            'teacher': self.submission.task.course.teacher
        }

    # Matches // Setters in UML
    def set_state(self, new_status):
        self._subject_state = new_status
        self.submission.status = new_status
        self.submission.save()
        
        # When state changes, notify all observers!
        self.notify() 

# ConcreteObserver 1 (Teacher)
class TeacherObserver(Observer):
    def __init__(self, subject: SubmissionSubject):
        self.subject = subject
        self.observer_state = None  # observerState in UML
        self.subject.register(self)

    # update() overrided function (see UML)
    def update(self):
        # update() triggers getState() from the Subject
        state = self.subject.get_state()
        self.observer_state = state['status']

        if self.observer_state == 'pending':
            teacher = state['teacher']
            student = state['student']
            task_title = state['task_title']
            
            # --- NOTIFICATION LOGIC GOES HERE ---
            print(f"NOTIFICATION FOR TEACHER {teacher}: Student {student.full_name} submitted '{task_title}'.")
            # Note from Mark: When the models.py has been updated, create a Notification database object here.
            # Notification.objects.create(user=teacher, message=f"{student.full_name} submitted {task_title}")

# ConcreteObserver 2 (Student)
class StudentObserver(Observer):
    def __init__(self, subject: SubmissionSubject):
        self.subject = subject
        self.observer_state = None # observerState in UML
        self.subject.register(self)

    # update() overrided function (see UML)
    def update(self):
        # update() triggers getState() from the Subject
        state = self.subject.get_state()
        self.observer_state = state['status']

        if self.observer_state == 'reviewed':
            student = state['student']
            task_title = state['task_title']
            
            # Notification logic will go here:
            print(f"Hello, {student}! Your task '{task_title}' has been graded.")
            # Note from Mark: When the models.py has been updated, create a Notification database object here.