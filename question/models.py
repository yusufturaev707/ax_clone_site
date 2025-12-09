from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=255, blank=True)
    key = models.PositiveSmallIntegerField(blank=True)

    def __str__(self):
        return self.name


class QuestionAdmission(models.Model):
    number = models.CharField(max_length=8, blank=True, null=True)
    submission_test = models.ForeignKey('test_maker.SubmissionTest', on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True)
    language = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True)
    theme = models.ForeignKey('test_maker.Theme', on_delete=models.CASCADE, blank=True)
    level = models.ForeignKey('test_maker.LevelDifficulty', on_delete=models.CASCADE, blank=True)
    tex_code = models.TextField(blank=True)
    a = models.TextField(blank=True)
    b = models.TextField(blank=True)
    c = models.TextField(blank=True)
    d = models.TextField(blank=True)
    tex_file = models.FileField(blank=True, null=True)
    question_pdf = models.FileField(blank=True, null=True)
    option_pdf = models.FileField(blank=True, null=True)
    status = models.ForeignKey('question.Status', on_delete=models.CASCADE, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.number)


class QuestionNational(models.Model):
    number = models.CharField(max_length=8, blank=True, null=True)
    submission_test = models.ForeignKey('test_maker.SubmissionTest', on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True)
    language = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True)
    part = models.ForeignKey('test_maker.Part', on_delete=models.CASCADE, blank=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True)
    part_option = models.ForeignKey('test_maker.OptionPart', on_delete=models.CASCADE, blank=True)
    file_word = models.FileField(blank=True, null=True)
    file_audio = models.FileField(blank=True, null=True)
    status = models.ForeignKey('question.Status', on_delete=models.CASCADE, blank=True)
    is_have_audio = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edit = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)

    def get_data(self):
        number = None
        submission_test_id = None
        user = None
        subject = None
        language = None
        part = None
        level = None
        part_option = None
        file_word = None
        file_audio = None
        status = None
        created_at = None
        updated_at = None

        if self.number:
            number = self.number
        if self.submission_test_id:
            submission_test_id = self.submission_test.id
        if self.user:
            user = self.user.full_name
        if self.subject:
            subject = self.subject.name
        if self.language:
            language = self.language.name
        if self.part:
            part = self.part.name
        if self.level:
            level = self.level.name
        if self.part_option:
            part_option = self.part_option.name
        if self.file_word:
            file_word = self.file_word.url
        if self.file_audio:
            file_audio = self.file_audio.url
        if self.status:
            status = self.status.name
        if self.created_at:
            created_at = self.created_at.strftime("%d.%m.%Y")
        if self.updated_at:
            updated_at = self.updated_at

        return {
            'id': self.id,
            'number': number,
            'submission_test_id': submission_test_id,
            'user': user,
            'subject': subject,
            'language': language,
            'part': part,
            'level': level,
            'part_option': part_option,
            'file_word': file_word,
            'file_audio': file_audio,
            'status': status,
            'created_at': created_at,
            'updated_at': updated_at,
        }

    def __str__(self):
        return str(self.number)


class MockQuestion(models.Model):
    number = models.CharField(max_length=8, blank=True, null=True)
    submission_test = models.ForeignKey('test_maker.SubmissionTest', on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey('user_app.User', on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey('test_maker.Subject', on_delete=models.CASCADE, blank=True)
    language = models.ForeignKey('test_maker.LanguageTest', on_delete=models.CASCADE, blank=True)
    part = models.ForeignKey('test_maker.Part', on_delete=models.CASCADE, blank=True)
    level = models.ForeignKey('test_maker.LevelDifficultyNational', on_delete=models.CASCADE, blank=True)
    part_option = models.ForeignKey('test_maker.OptionPart', on_delete=models.CASCADE, blank=True)
    file_word = models.FileField(blank=True, null=True)
    file_audio = models.FileField(blank=True, null=True)
    is_have_audio = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edit = models.BooleanField(default=False)
    payed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.number)


class PaymentType(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    key = models.PositiveSmallIntegerField(default=0)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)


class DownloadExcellLog(models.Model):
    user = models.ForeignKey('user_app.User', on_delete=models.SET_NULL, blank=True, null=True)
    payment_type = models.ForeignKey('question.PaymentType', on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    excel_file = models.FileField(upload_to="payments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"
