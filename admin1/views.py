import hashlib
import json
import os
import time

import requests
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from admin1.functions import accounted_question
from admin1.models import TypeVoice, AudioLanguage, HistoryConvertedTextToSpeech, TextLanguage, GeneratedText
from config import settings
from expert.models import CheckTestExpert, Expert, CheckedTestCount, JobControlSheetNS, ExpertiseQuestionJob
from moderator.models import ModeratorCheckTest, Moderator
from question.models import QuestionNational, PaymentType, DownloadExcellLog
from test_maker.models import SubmissionTest, TestConfirmationCount, Part, OptionPart
from user_app.decorators import allowed_users
from admin1.constants import base_url, base_url_generate_text, base_url_generate_test
from user_app.models import User
from datetime import datetime, timezone


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def question_dashboard(request):
    return render(request, 'admin1/admin1_dashboard.html')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def question_dashboard(request):
    return render(request, 'admin1/admin1_dashboard.html')


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def text_to_speech(request):
    type_voices = TypeVoice.objects.all().order_by('id')
    languages = AudioLanguage.objects.all().order_by('id')
    status = 1
    if request.method == "POST" and is_ajax(request):
        if status == 0:
            return JsonResponse({"result": False, "message": f"Sun'iy intellektdan foydalanish hozircha mumkin emas!"})
        type_voice = request.POST.get('type_voice')
        language = request.POST.get('language')
        text_string = request.POST.get('text_string')

        if type_voice == '' or language == '' or text_string == '':
            return JsonResponse({"result": False, "message": "Iltimos formani to'ldiring!"})

        current_time = str(time.time()).encode('utf-8')
        hash_object = hashlib.sha256()
        hash_object.update(current_time)
        hashed_time = hash_object.hexdigest()

        domain = request._current_scheme_host

        url = f"{base_url}audio_name={hashed_time}&text_string={text_string}&lang_id={language}&voice_id={type_voice}"
        try:
            response = requests.get(url)
        except Exception as e:
            return JsonResponse({"result": False, "message": f"Sun'iy intellektdan foydalanish hozircha mumkin emas!!"})
        response = response.json()
        status = response['code']
        if status == 'success':
            res_url = response['url']
            file_url = f"{domain}/media/"
            try:
                ob = HistoryConvertedTextToSpeech.objects.create(
                    user=request.user,
                    text=text_string,
                    language=get_object_or_404(AudioLanguage, pk=int(language)),
                    type_voice=get_object_or_404(TypeVoice, pk=int(type_voice)),
                    audio_name=hashed_time,
                    audio_file=res_url
                )
            except Exception as e:
                return JsonResponse({"result": False, "message": f"{e}"})
        else:
            return JsonResponse({"result": False, "message": f"Xatolik yuz berdi."})

        return JsonResponse({"result": True, "message": response['code'], "url": f"{file_url}{ob.audio_file}"})

    context = {
        "type_voices": type_voices,
        "languages": languages,
    }
    return render(request, 'admin1/text_audio_converter_dashboard.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def load_converted_audios(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        limit = start + length

        objects = HistoryConvertedTextToSpeech.objects.filter(user=user).order_by('id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(text__icontains=str(search_value).lower()) |
                Q(audio_name__icontains=str(search_value).lower())
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = '-id'

        objects = objects.order_by(sort_column_name)
        filtered_records_count = objects.count()
        objects = objects[start:limit]

        domain = request._current_scheme_host
        domain_url = f"{domain}/media/"

        data = []
        for item in objects:
            data.append({
                'id': item.id,
                'user_id': item.user.id,
                'voice_name': item.type_voice.name,
                'language': item.language.name,
                'text': item.text,
                'audio_name': item.audio_name,
                'audio_file': item.audio_file,
                'created_at': item.created_at,
                'domain_url': domain_url,
            })

        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": filtered_records_count,
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_questions_admin1(request):
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        items = []
        for i in range(12):
            name = str(request.POST.get(f'columns[{i}][data]'))
            value = str(request.POST.get(f'columns[{i}][search][value]')).lower()
            if value:
                items.append(
                    {
                        "name": name,
                        "value": value
                    }
                )

        limit = start + length

        objects = SubmissionTest.objects.filter(submission__type_test_upload_id=1).order_by('-id')

        if search_value is not None:
            objects = objects.filter(
                Q(submission__subject__name__icontains=str(search_value).lower()) |
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(submission__topic_n__icontains=str(search_value).lower()) |
                Q(submission__part__name__icontains=str(search_value).lower()) |
                Q(submission__part_option__name__icontains=str(search_value).lower()) |
                Q(submission__level_dn__name__icontains=str(search_value).lower()),
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = '-id'

        objects = objects.order_by(sort_column_name)
        for item in items:
            value = item['value']
            print(f"{item['name']}--{value}")
            if item['name'] == 'id':
                objects = objects.filter(id=value)
            if item['name'] == 'last_name':
                objects = objects.filter(user__last_name__icontains=value)
            if item['name'] == 'first_name':
                objects = objects.filter(user__first_name__icontains=value)
            if item['name'] == 'middle_name':
                objects = objects.filter(user__middle_name__icontains=value)
            if item['name'] == 'subject':
                objects = objects.filter(submission__subject__name__icontains=value)
            if item['name'] == 'level_d':
                objects = objects.filter(submission__level_dn__name__icontains=value)
            if item['name'] == 'part':
                objects = objects.filter(submission__part__name__icontains=value)
            if item['name'] == 'part_option_name':
                objects = objects.filter(submission__part_option__name__icontains=value)
            if item['name'] == 'topic_n':
                objects = objects.filter(submission__topic_n__icontains=value)
            if item['name'] == 'status':
                objects = objects.filter(status__name__icontains=value)
            if item['name'] == 'created_at':
                date_time = datetime.strptime(value, '%Y-%m-%d')
                year = date_time.year
                month = date_time.month
                day = date_time.day
                objects = objects.filter(created_at__year=year).filter(created_at__month=month).filter(created_at__day=day)
            if item['name'] == 'is_check_finish':
                if value == 'true':
                    objects = objects.filter(is_check_finish=True)
                if value == 'false':
                    objects = objects.filter(is_check_finish=False)
            
        total = objects.count()
        if length == -1:
            limit = total
        questions = objects[start:limit]
        data = [item.get_data() for item in questions]
        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def view_question(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def question_info(request, pk):
    question = get_object_or_404(SubmissionTest, pk=pk)
    objects = CheckTestExpert.objects.filter(submission_test=question, is_job_given=1).order_by('created_at')
    data = [[[JobControlSheetNS.objects.filter(job=job).order_by('id')], job] for job in objects]
    items = ModeratorCheckTest.objects.filter(submission_test=question)
    moderator_job_controls = [ExpertiseQuestionJob.objects.filter(job=job).order_by('id') for job in items]
    moderator = None
    if items.count() == 1:
        moderator = get_object_or_404(ModeratorCheckTest, pk=items.last().id)

    context = {
        "question": question,
        "objects": objects,
        "moderator": moderator,
        "data": data,
        "moderator_job_controls": moderator_job_controls,
    }
    return render(request, 'admin1/question_info.html', context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def expert_list_admin1(request):
    return render(request, "admin1/experts.html")


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_experts_admin1(request):
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        items = []
        for i in range(10):
            name = str(request.POST.get(f'columns[{i}][data]'))
            value = str(request.POST.get(f'columns[{i}][search][value]')).lower()
            if value:
                items.append(
                    {
                        "name": name,
                        "value": value
                    }
                )

        limit = start + length

        objects = Expert.objects.filter(is_lang_specialist=True).order_by('id')

        if search_value is not None:
            objects = objects.filter(
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(subject__name__icontains=str(search_value).lower()) |
                Q(level__name__icontains=str(search_value).lower()) |
                Q(user__jshshr=str(search_value).lower()),
            )
        if sort_direction is not None:
            if int(sort_column_index) == 1 or int(sort_column_index) == 2 or int(sort_column_index) == 3:
                sort_column_name = f"user__{sort_column_name}"
            elif int(sort_column_index) == 4:
                sort_column_name = f"subject__{sort_column_name}".replace('subject_name', 'name')
            elif int(sort_column_index) == 6:
                sort_column_name = "id"
            elif int(sort_column_index) == 0:
                sort_column_name = "id"

            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = 'id'

        objects = objects.order_by(sort_column_name)
        for item in items:
            value = item['value']
            if item['name'] == 'id':
                objects = objects.filter(id=value)
            if item['name'] == 'last_name':
                objects = objects.filter(user__last_name__icontains=value)
            if item['name'] == 'first_name':
                objects = objects.filter(user__first_name__icontains=value)
            if item['name'] == 'middle_name':
                objects = objects.filter(user__middle_name__icontains=value)
            if item['name'] == 'subject_name':
                objects = objects.filter(subject__name__icontains=value)
            if item['name'] == 'level_name':
                objects = objects.filter(level__name__icontains=value)
            if item['name'] == 'jshshr':
                objects = objects.filter(user__jshshr=value)
            if item['name'] == 'is_sender':
                if value == 'true':
                    objects = objects.filter(is_sender=True)
                if value == 'false':
                    objects = objects.filter(is_sender=False)
            if item['name'] == 'is_checker':
                if value == 'true':
                    objects = objects.filter(is_checker=True)
                if value == 'false':
                    objects = objects.filter(is_checker=False)
            if item['name'] == 'is_blocked':
                if value == 'true':
                    objects = objects.filter(is_blocked=True)
                if value == 'false':
                    objects = objects.filter(is_blocked=False)
        total = objects.count()
        if length == -1:
            limit = total
        experts = objects[start:limit]

        data = []
        for item in experts:
            data.append({
                'id': item.id,
                'user_id': item.user.id,
                'last_name': item.user.last_name,
                'first_name': item.user.first_name,
                'middle_name': item.user.middle_name,
                'subject_name': item.subject.name,
                'level_name': item.level.name,
                'jshshr': str(item.user.jshshr),
                'is_blocked': item.is_blocked,
                'is_sender': item.is_sender,
                'is_checker': item.is_checker,
            })

        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def view_expert(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def expert_info(request, pk):
    expert = get_object_or_404(Expert, pk=pk)
    context = {
        "expert": expert,
    }
    return render(request, 'admin1/expert_info.html', context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def delete_audio(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def delete_audio_object(request, pk):
    url_media = f"{settings.MEDIA_ROOT}"
    url = None
    try:
        ob = get_object_or_404(HistoryConvertedTextToSpeech, pk=pk)
        url = f"{url_media}/{ob.audio_file}"
        os.remove(f"{url}")
        ob.delete()
    except FileNotFoundError:
        print(f"File '{url}' not found.")
    except Exception as e:
        return JsonResponse({"result": False, "message": f"{e}"})
    return JsonResponse({"result": True, "message": f"Audio o'chirildi", "path": url})


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def generate_text(request):
    user = get_object_or_404(User, pk=request.user.id)
    languages = TextLanguage.objects.all().order_by('id')
    status = 1
    if request.method == "POST" and is_ajax(request):
        if status == 0:
            return JsonResponse({"result": False, "message": f"Sun'iy intellektdan foydalanish hozircha mumkin emas!"})
        # if not user.is_moderator:
        #     return JsonResponse({"result": False, "message": "Siz moderator emassiz!"})
        # moderator = get_object_or_404(Moderator, user=user)
        # if not (moderator.is_moderator and moderator.upload_type == 1 and moderator.subject.key == 'en'):
        #     return JsonResponse({"result": False, "message": "Faqat ingliz tili!"})

        language = request.POST.get('language')
        theme = request.POST.get('theme')
        word_count = request.POST.get('word_count')

        if language == '' or word_count == '' or theme == '':
            return JsonResponse({"result": False, "message": "Iltimos formani to'ldiring!"})

        url = f"{base_url_generate_text}theme={theme}&word_count={word_count}&lang_id={language}"
        try:
            response = requests.get(url)
        except Exception as e:
            return JsonResponse({"result": False, "message": f"Sun'iy intellektdan foydalanish hozircha mumkin emas!!"})
        response = response.json()
        text = response['text']
        lang = get_object_or_404(TextLanguage, pk=int(language))
        is_english = False
        if lang.key == 1:
            is_english = True
        try:
            GeneratedText.objects.create(
                user=user,
                theme=theme,
                language=lang,
                word_count=int(word_count),
                text=str(text),
                is_english=is_english
            )
        except Exception as e:
            return JsonResponse({"result": False, "message": f"{e}"})

        return JsonResponse({"result": True, "message": "Ok"})

    context = {
        "languages": languages,
        "user": user,
    }
    return render(request, 'admin1/text_generate_dashboard.html', context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def load_converted_texts(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        limit = start + length

        objects = GeneratedText.objects.filter(user=user).order_by('id')
        total = objects.count()

        if search_value is not None:
            objects = objects.filter(
                Q(theme__icontains=str(search_value).lower()) |
                Q(language__name__icontains=str(search_value).lower())
            )
        if sort_direction is not None:
            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = '-id'

        objects = objects.order_by(sort_column_name)
        filtered_records_count = objects.count()
        objects = objects[start:limit]

        data = []
        for item in objects:
            data.append({
                'id': item.id,
                'theme': item.theme,
                'language__name': item.language.name,
                'language__key': item.language.key,
                'text': item.text,
                'created_at': item.created_at.strftime("%d.%m.%Y %H:%M"),
            })

        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": filtered_records_count,
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def delete_text(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def delete_text_object(request, pk):
    try:
        ob = get_object_or_404(GeneratedText, pk=pk)
        ob.delete()
    except Exception as e:
        return JsonResponse({"result": False, "message": f"{e}"})
    return JsonResponse({"result": True, "message": "Text o'chirildi"})


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def g_test(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def generate_test(request, pk):
    status = 1

    t_object = get_object_or_404(GeneratedText, pk=pk)
    data = t_object.test_data
    is_empty = True
    if data:
        is_empty = False
    if not data:
        if status == 0:
            context = {
                "id": t_object.id,
                "data": "Sun'iy intellektdan foydalanish hozircha mumkin emas!",
                "is_empty": is_empty,
                "is_english": t_object.is_english,
            }
            return render(request, "admin1/tests.html", context=context)
        if t_object.language.key == 1:
            url = f"{base_url_generate_test}text={t_object.text}&test_section=2"
            try:
                response = requests.get(url)
            except Exception as e:
                text_data = f"Sun'iy intellektdan foydalanish hozircha mumkin emas!"
                context = {
                    "id": t_object.id,
                    "data": text_data,
                    "is_empty": is_empty,
                    "is_english": t_object.is_english,
                }
                return render(request, "admin1/tests.html", context=context)
            data = response
            t_object.test_data = data.text
            t_object.save()

    t_object = get_object_or_404(GeneratedText, pk=pk)
    text_data = t_object.test_data

    context = {
        "id": t_object.id,
        "data": text_data,
        "is_empty": is_empty,
        "is_english": t_object.is_english,
    }
    return render(request, "admin1/tests.html", context=context)


@login_required(login_url='login')
@allowed_users(role=['admin', 'moderator'])
def delete_test(request, pk):
    t_object = get_object_or_404(GeneratedText, pk=pk)
    data = t_object.test_data
    if data:
        t_object.test_data = ""
        t_object.save()
        return redirect('generate_text')
    return JsonResponse({"result": True, "message": "Test o'chirildi"})


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def blocking_expert(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def blocked_expert(request, pk):
    try:
        if request.method == "GET" and is_ajax(request):
            expert = get_object_or_404(Expert, pk=pk)
            if expert.is_blocked is False:
                expert.is_blocked = True
                expert.user.is_blocked = True
                expert.is_sender = False
                expert.is_checker = False
                expert.save()
                expert.user.save()

                data = {"error": 1}
                return JsonResponse(data, status=200)
            elif expert.is_blocked is True:
                data = {"error": 0, "message": "Oldin bloklangan"}
                return JsonResponse(data, status=200)
        else:
            data = {"error": 0, "message": "Faqat ajax request bo'lishi kerak!"}
            return JsonResponse(data, status=400)
    except Exception as e:
        data = {"error": 0, "message": str(e)}
        return JsonResponse(data, status=400)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def un_blocking_expert(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def un_blocked_expert(request, pk):
    try:
        if request.method == "GET" and is_ajax(request):
            expert = get_object_or_404(Expert, pk=pk)
            if expert.is_blocked is True:
                expert.is_blocked = False
                expert.user.is_blocked = False
                expert.is_sender = False
                expert.is_checker = False
                expert.save()
                expert.user.save()

                data = {"error": 1}
                return JsonResponse(data, status=200)
            elif expert.is_blocked is False:
                data = {"error": 0, "message": "Bloklanmagan"}
                return JsonResponse(data, status=200)
        else:
            data = {"error": 0, "message": "Faqat ajax request bo'lishi kerak!"}
            return JsonResponse(data, status=400)
    except Exception as e:
        data = {"error": 0, "message": str(e)}
        return JsonResponse(data, status=400)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def edit_expert_permission_url(request):
    return HttpResponse('ok')


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def edit_expert_permission(request, pk):
    if request.method == 'GET' and is_ajax(request):
        expert = get_object_or_404(Expert, pk=pk)
        context = {
            "expert": expert,
        }
        return render(request, "admin1/edit_expert_permission.html", context)
    elif request.method == 'POST' and is_ajax(request):
        try:
            expert = get_object_or_404(Expert, pk=pk)
            ch1 = request.POST.get(f"is_sender{expert.id}", None)
            ch2 = request.POST.get(f"is_checker{expert.id}", None)

            if ch1 == 'on':
                expert.is_sender = True
            elif ch1 is None:
                expert.is_sender = False
            if ch2 == 'on':
                expert.is_checker = True
            elif ch2 is None:
                expert.is_checker = False
            expert.save()

            data = {
                "result": 200,
            }
            return JsonResponse(data)
        except Exception as e:
            data = {
                "result": 500,
                "message": f"Xatolik: {e}",
            }
            return JsonResponse(data)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_question_count_menu(request):
    return render(request, "admin1/sending_question_count.html")


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_sending_question_count_list(request):
    if request.method == 'POST' and is_ajax(request):
        draw = request.POST.get('draw')
        start = int(request.POST.get('start'))
        length = int(request.POST.get('length'))
        search_value = request.POST.get('search[value]')
        sort_column_index = request.POST.get('order[0][column]')
        name = f"columns[{sort_column_index}][data]"
        sort_column_name = request.POST.get(name)
        sort_direction = request.POST.get('order[0][dir]')

        items = []
        for i in range(10):
            name = str(request.POST.get(f'columns[{i}][data]'))
            value = str(request.POST.get(f'columns[{i}][search][value]')).lower()
            if value:
                items.append(
                    {
                        "name": name,
                        "value": value
                    }
                )

        limit = start + length

        objects = TestConfirmationCount.objects.all().order_by('id')
        if search_value is not None:
            objects = objects.filter(
                Q(user__last_name__icontains=str(search_value).lower()) |
                Q(user__first_name__icontains=str(search_value).lower()) |
                Q(user__middle_name__icontains=str(search_value).lower()) |
                Q(subject__name__icontains=str(search_value).lower()) |
                Q(level__name__icontains=str(search_value).lower()) |
                Q(section__name__icontains=str(search_value).lower()) |
                Q(part__name__icontains=str(search_value).lower()) |
                Q(user__jshshr=str(search_value).lower()),
            )
        if sort_direction is not None:
            if int(sort_column_index) in [1, 2, 3, 4]:
                sort_column_name = f"user__{sort_column_name}"
            elif int(sort_column_index) == 6:
                sort_column_name = f"subject__{sort_column_name}".replace('subject_name', 'name')
            elif int(sort_column_index) == 7:
                sort_column_name = f"level__{sort_column_name}".replace('level_name', 'name')
            elif int(sort_column_index) == 8:
                sort_column_name = f"section__{sort_column_name}".replace('section_name', 'name')
            elif int(sort_column_index) == 9:
                sort_column_name = f"part__{sort_column_name}".replace('part_name', 'name')
            elif int(sort_column_index) in [0, 10]:
                sort_column_name = "id"

            if sort_direction == 'desc':
                sort_column_name = f"-{sort_column_name}"
        else:
            sort_column_name = 'id'

        objects = objects.order_by(sort_column_name)
        for item in items:
            value = item['value']
            if item['name'] == 'id':
                objects = objects.filter(id=value)
            if item['name'] == 'last_name':
                objects = objects.filter(user__last_name__icontains=value)
            if item['name'] == 'first_name':
                objects = objects.filter(user__first_name__icontains=value)
            if item['name'] == 'middle_name':
                objects = objects.filter(user__middle_name__icontains=value)
            if item['name'] == 'subject_name':
                objects = objects.filter(subject__name__icontains=value)
            if item['name'] == 'level_name':
                objects = objects.filter(level__name__icontains=value)
            if item['name'] == 'section_name':
                objects = objects.filter(section__name__icontains=value)
            if item['name'] == 'part_name':
                objects = objects.filter(part__name__icontains=value)
            if item['name'] == 'jshshr':
                objects = objects.filter(user__jshshr=value)

        total = objects.count()
        if length == -1:
            limit = total
        experts = objects[start:limit]

        data = []
        for item in experts:
            data.append({
                'id': item.id,
                'user_id': item.user.id,
                'last_name': item.user.last_name,
                'first_name': item.user.first_name,
                'middle_name': item.user.middle_name,
                'subject_name': item.subject.name,
                'level_name': item.level.name,
                'section_name': item.section.name,
                'part_name': item.part.name,
                'jshshr': str(item.user.jshshr),
                'count': item.count,
            })

        response = {
            "data": data,
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": objects.count()
        }
        return JsonResponse(response, safe=False)
    else:
        return JsonResponse({}, safe=False)


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_question_payment_menu(request):
    items = PaymentType.objects.filter(status=True).order_by('id')
    return render(request, "admin1/payment.html", {"items": items})


@login_required(login_url='login')
@allowed_users(role=['admin', 'admin1'])
def load_question_payment_list(request):
    if request.method == 'POST' and is_ajax(request):
        try:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            select_type = request.POST.get('select_payment')

            if start_date == '' or end_date == '' or select_type == '':
                response = {
                    "result": 0,
                    "message": "To'lov turi yoki Sana tanlanmadi!",
                    "data": {},
                }
                return JsonResponse(response)

            pay_type = get_object_or_404(PaymentType, key=int(select_type))
            date1 = datetime.strptime(start_date, '%m/%d/%Y %I:%M %p')
            date2 = datetime.strptime(end_date, '%m/%d/%Y %I:%M %p')

            experts = Expert.objects.filter(is_expert=True, is_lang_specialist=True).order_by('id')

            if pay_type.key == 1:
                q_objects = QuestionNational.objects.filter(created_at__gte=date1, created_at__lte=date2).order_by('created_at')
                data, file_url = accounted_question(questions=q_objects, experts=experts, date1=date1, date2=date2, p_type=pay_type.key)

                if len(data) == 0:
                    response = {
                        "result": 0,
                        "message": f"{date1} - {date2} da ma'lumot topilmadi",
                        "data": {},
                    }
                    return JsonResponse(response)

                excell_ob = DownloadExcellLog.objects.create(
                    user=request.user,
                    payment_type=pay_type,
                    start_date=date1,
                    end_date=date2,
                    excel_file=file_url
                )
                response = {
                    "result": 1,
                    "message": "",
                    "data": data,
                    "link": excell_ob.excel_file.url,
                }
                return JsonResponse(response, safe=False)
            elif pay_type.key == 2:
                jobs = CheckTestExpert.objects.filter(created_at__gte=date1, created_at__lte=date2, is_check=True)
                data, file_url = accounted_question(questions=jobs, experts=experts, date1=date1, date2=date2, p_type=pay_type.key)

                if len(data) == 0:
                    response = {
                        "result": 0,
                        "message": f"{date1} - {date2} da ma'lumot topilmadi",
                        "data": {},
                    }
                    return JsonResponse(response)

                excell_ob = DownloadExcellLog.objects.create(
                    user=request.user,
                    payment_type=pay_type,
                    start_date=date1,
                    end_date=date2,
                    excel_file=file_url
                )
                response = {
                    "result": 1,
                    "message": "",
                    "data": data,
                    "link": excell_ob.excel_file.url,
                }
                return JsonResponse(response, safe=False)
            else:
                response = {
                    "result": 0,
                    "message": "Ishlab chiqilmoqda",
                    "data": {},
                }
                return JsonResponse(response)

        except Exception as e:
            response = {
                "result": 0,
                "message": f"{e}",
                "data": "",
            }
            return JsonResponse(response, safe=False)

    response = {
        "data": [],
    }
    return JsonResponse(response, safe=False)