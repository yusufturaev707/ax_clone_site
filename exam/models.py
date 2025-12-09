from django.db import models


class Exam(models.Model):
    pupil = models.ForeignKey('pupil.Pupil', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True, null=True)
    question_box = models.ForeignKey('test_maker.QuestionBox', on_delete=models.CASCADE, blank=True, null=True)
    duration = models.DurationField(default="00:30:00")
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    score = models.PositiveSmallIntegerField(default=0)
    count_correct_answer = models.PositiveSmallIntegerField(default=0)
    count_incorrect_answer = models.PositiveSmallIntegerField(default=0)
    is_started = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    spent_time = models.DurationField(default="00:00:00")
    time_left = models.DurationField(default="00:00:00")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pupil.user.full_name)


class ExamQuestion(models.Model):
    exam = models.ForeignKey('exam.Exam', on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey('question.QuestionAdmission', on_delete=models.CASCADE, blank=True, null=True)
    correct_answer = models.PositiveSmallIntegerField(blank=True, null=True)
    pdf = models.FileField(blank=True, null=True)
    is_solved = models.BooleanField(default=False)
    order_q = models.SmallIntegerField(default=0)
    is_last_question = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class PupilResponse(models.Model):
    exam = models.ForeignKey('exam.Exam', on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey('exam.ExamQuestion', on_delete=models.CASCADE, blank=True, null=True)
    selected_answer = models.PositiveSmallIntegerField(null=True, blank=True)
    selected_abcd = models.CharField(max_length=255, null=True, blank=True)
    is_correct_answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Category(models.Model):
    name = models.CharField(max_length=255, blank=True)
    key = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name


class Appeal(models.Model):
    pupil = models.ForeignKey('pupil.Pupil', on_delete=models.CASCADE, blank=True, null=True)
    exam = models.ForeignKey('exam.Exam', on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey('exam.ExamQuestion', on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey('exam.Category', on_delete=models.CASCADE, blank=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
