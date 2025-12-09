from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from expert import models
from moderator.models import Status, ModeratorCheckTest
import time
import hashlib
from PIL import Image
from test_maker.models import TypeTestUpload


def generate_hash():
    current_time = str(time.time()).encode('utf-8')
    hash_object = hashlib.sha256()
    hash_object.update(current_time)
    hashed_time = hash_object.hexdigest()
    return hashed_time


def compress_and_resize_jpeg(input_path, output_path, quality=70, width=None, height=None):
    try:
        with Image.open(input_path) as img:
            if width and height:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(output_path, 'JPEG', quality=quality)
    except Exception as e:
        print(f"An error occurred: {e}")


def submit_to_moderator(submission, upload_type_id):
    upload_type = get_object_or_404(TypeTestUpload, id=upload_type_id)
    status = get_object_or_404(Status, key=2)

    if upload_type.id == 2:
        # ModeratorCheckTest ni boshqa db o'zgartirish kk
        try:
            ModeratorCheckTest.objects.create(
                user=submission.user,
                submission_test=submission,
                status=status,
                upload_type=upload_type
            )
        except Exception:
            return JsonResponse(
                {"result": False, "message": "Tahrirlashga yuborishda xatolik!"})

    if upload_type.id == 1:
        try:
            ob = ModeratorCheckTest.objects.create(
                user=submission.user,
                submission_test=submission,
                status=status,
                upload_type=upload_type,
            )
        except Exception:
            return JsonResponse(
                {"result": False, "message": "Tahrirlashga yuborishda xatolik!"})
        part = ob.submission_test.submission.part
        level = ob.submission_test.submission.level_dn
        subject = ob.submission_test.submission.subject
        part_option = ob.submission_test.submission.part_option
        controls = models.ControlSheetNS.objects.filter(sheet__part=part, sheet__level=level, subject=subject, part_option=part_option, status=True).order_by('id')

        for item in controls:
            models.ExpertiseQuestionJob.objects.create(
                job=ob,
                control_sheet=item,
            )
