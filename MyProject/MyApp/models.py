from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

# -----------------------------
# Custom User Manager
# -----------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, role='Student', **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, role='Admin', **extra_fields)


# -----------------------------
# User Model
# -----------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Instructor', 'Instructor'),
        ('Admin', 'Admin'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email



# -----------------------------
# Role-specific Details
# -----------------------------
class StudentDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_detail')
    department = models.CharField(max_length=50, blank=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    course_interests = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.full_name} - Student"


class InstructorDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_detail')
    qualification = models.CharField(max_length=100, blank=True)
    expertise = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.full_name} - Instructor"


class AdminDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_detail')
    admin_code = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.full_name} - Admin"


# -----------------------------
# Courses
# -----------------------------
class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image_url = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# -----------------------------
# Enrollment
# -----------------------------
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    progress = models.IntegerField(default=0)  # 0-100
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.full_name} - {self.course.title}"


# -----------------------------
# Security Questions
# -----------------------------
class SecurityQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_questions')
    question = models.CharField(max_length=255)
    answer_hash = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.full_name} - {self.question}"


# -----------------------------
# Course Content
# -----------------------------
class CourseContent(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('Video', 'Video'),
        ('PDF', 'PDF'),
        ('Text', 'Text'),
        ('Test', 'Test'),
        ('Link', 'Link'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=100)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='course_pdfs/', blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    test_link = models.URLField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    position = models.IntegerField(default=1)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# -----------------------------
# Quiz / Test Questions
# -----------------------------
class QuizQuestion(models.Model):
    course = models.ForeignKey(Course, related_name='quiz_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200)
    option_4 = models.CharField(max_length=200)
    correct_option = models.PositiveSmallIntegerField(choices=[
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.question_text[:50]}"


# -----------------------------
# Track Student Progress per Content
# -----------------------------
class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    content = models.ForeignKey(CourseContent, on_delete=models.CASCADE, related_name='progress')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'content')

    def __str__(self):
        return f"{self.user.full_name} - {self.content.title} - {'Completed' if self.completed else 'Pending'}"


# -----------------------------
# Quiz Attempts / Student Scores
# -----------------------------
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_attempts')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='attempts')
    selected_option = models.PositiveSmallIntegerField(choices=[
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4')
    ])
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.full_name} - {self.question.question_text[:30]} - {'Correct' if self.is_correct else 'Wrong'}"


# -----------------------------------
# Table Structure in Comments
# -----------------------------------
"""
Tables:

User
- id (PK)
- email
- full_name
- username
- phone
- dob
- gender
- role
- is_active
- is_staff
- created_at
- updated_at

StudentDetail / InstructorDetail / AdminDetail
- id (PK)
- user_id (FK -> User.id)
- specific fields (department, qualification, expertise, admin_code)

Course
- id (PK)
- title
- description
- image_url
- created_by (FK -> User.id)
- created_at
- updated_at

Enrollment
- id (PK)
- user_id (FK -> User.id)
- course_id (FK -> Course.id)
- progress
- enrolled_at
- completed_at

SecurityQuestion
- id (PK)
- user_id (FK -> User.id)
- question
- answer_hash

CourseContent
- id (PK)
- course_id (FK -> Course.id)
- title
- content_type
- video_file
- pdf_file
- text_content
- test_link
- external_link
- position

QuizQuestion
- id (PK)
- course_id (FK -> Course.id)
- question_text
- option_1
- option_2
- option_3
- option_4
- correct_option
- created_at

CourseProgress
- id (PK)
- user_id (FK -> User.id)
- content_id (FK -> CourseContent.id)
- completed
- completed_at

QuizAttempt
- id (PK)
- user_id (FK -> User.id)
- course_id (FK -> Course.id)
- question_id (FK -> QuizQuestion.id)
- selected_option
- is_correct
- attempted_at
"""
