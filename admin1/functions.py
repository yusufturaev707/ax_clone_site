import os
import time

from django.shortcuts import get_object_or_404
import xlsxwriter
from config import settings
from question.models import PaymentType
from test_maker.models import Part, OptionPart


def accounted_question(questions=None, experts=None, date1=None, date2=None, p_type=None):
    try:
        data = []
        if p_type is None:
            return data, ""

        s_part = get_object_or_404(Part, key='s')
        w_part = get_object_or_404(Part, key='w')

        if p_type == 1:
            for expert in experts:
                is_exist = questions.filter(user=expert.user).exists()
                subject = expert.subject
                fio = f"{expert.user.last_name} {expert.user.first_name} {expert.user.middle_name}"
                jshshr = f"{expert.user.jshshr}"
                if is_exist:
                    items = questions.filter(user=expert.user, subject=subject).order_by('created_at')
                    s_part_list = items.filter(part=s_part)
                    w_part_list = items.filter(part=w_part)
                    p1 = p2 = p3 = t1 = t2 = 0

                    if s_part_list.count() > 0:
                        p1_object = get_object_or_404(OptionPart, key='p1')
                        part1_count = s_part_list.filter(part_option=p1_object).count()
                        p1 = p1_object.number_question * part1_count

                        p2_object = get_object_or_404(OptionPart, key='p2')
                        part2_count = s_part_list.filter(part_option=p2_object).count()
                        p2 = p2_object.number_question * part2_count

                        p3_object = get_object_or_404(OptionPart, key='p3')
                        part3_count = s_part_list.filter(part_option=p3_object).count()
                        p3 = p3_object.number_question * part3_count

                    if w_part_list.count() > 0:
                        t1_object = get_object_or_404(OptionPart, key='t1')
                        task1_count = w_part_list.filter(part_option=t1_object).count()
                        t1 = t1_object.number_question * task1_count

                        t2_object = get_object_or_404(OptionPart, key='t2')
                        task2_count = w_part_list.filter(part_option=t2_object).count()
                        t2 = t2_object.number_question * task2_count

                    data.append({
                        'id': expert.id, 'fio': fio, 'pnfl': jshshr, 'subject': subject.name,
                        'p1': p1, 'p2': p2, 'p3': p3, 't1': t1, 't2': t2,
                    })
            if len(data) > 0:
                p_type_ob = get_object_or_404(PaymentType, key=int(p_type))
                file_url = create_excell_report_file(data, date1, date2, p_type_ob.name)
                return data, file_url
            if len(data) == 0:
                return data, ""

        if p_type == 2:
            for expert in experts:
                is_exist = questions.filter(expert=expert).exists()
                subject = expert.subject
                fio = f"{expert.user.last_name} {expert.user.first_name} {expert.user.middle_name}"
                jshshr = f"{expert.user.jshshr}"

                if is_exist:
                    items = questions.filter(expert=expert).order_by('created_at')
                    s_part_list = items.filter(submission_test__submission__part=s_part)
                    w_part_list = items.filter(submission_test__submission__part=w_part)
                    p1 = p2 = p3 = t1 = t2 = 0

                    if s_part_list.count() > 0:
                        p1_object = get_object_or_404(OptionPart, key='p1')
                        part1_count = s_part_list.filter(submission_test__submission__part_option=p1_object).count()
                        p1 = p1_object.number_question * part1_count

                        p2_object = get_object_or_404(OptionPart, key='p2')
                        part2_count = s_part_list.filter(submission_test__submission__part_option=p2_object).count()
                        p2 = p2_object.number_question * part2_count

                        p3_object = get_object_or_404(OptionPart, key='p3')
                        part3_count = s_part_list.filter(submission_test__submission__part_option=p3_object).count()
                        p3 = p3_object.number_question * part3_count

                    if w_part_list.count() > 0:
                        t1_object = get_object_or_404(OptionPart, key='t1')
                        task1_count = w_part_list.filter(submission_test__submission__part_option=t1_object).count()
                        t1 = t1_object.number_question * task1_count

                        t2_object = get_object_or_404(OptionPart, key='t2')
                        task2_count = w_part_list.filter(submission_test__submission__part_option=t2_object).count()
                        t2 = t2_object.number_question * task2_count

                    data.append({
                        'id': expert.id, 'fio': fio, 'pnfl': jshshr, 'subject': subject.name,
                        'p1': p1, 'p2': p2, 'p3': p3, 't1': t1, 't2': t2,
                    })
            if len(data) > 0:
                p_type_ob = get_object_or_404(PaymentType, key=int(p_type))
                file_url = create_excell_report_file(data, date1, date2, p_type_ob.name)
                return data, file_url
            if len(data) == 0:
                return data, ""
    except Exception as e:
        print(e)


media_url = settings.MEDIA_URL
media_root = settings.MEDIA_ROOT
main_folder = "payments/"


def create_excell_report_file(data=None, date1=None, date2=None, p_type_name=None):
    try:
        t = time.time()
        url = f"{main_folder}"
        full_url = f"{media_root}{url}"

        if not os.path.exists(full_url):
            os.makedirs(full_url)

        file_url = f"{url}{t}.xlsx"
        workbook = xlsxwriter.Workbook(f"{media_root}{file_url}")
        worksheet = workbook.add_worksheet()

        worksheet.set_column("A:B", 10)
        worksheet.set_column("B:C", 60)
        worksheet.set_column("C:D", 20)
        worksheet.set_column("D:E", 15)
        worksheet.set_column("E:F", 15)
        worksheet.set_column("F:G", 20)
        worksheet.set_column("G:H", 20)
        worksheet.set_column("H:I", 20)
        worksheet.set_column("I:J", 20)

        worksheet.set_row(0, 20)
        worksheet.set_row(1, 30)

        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "#C6E0B4",
                "font_size": "12",
                'text_wrap': True,
                'font_name': 'Times New Roman'
            }
        )
        format_0 = workbook.add_format(
            {
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": "12",
                'text_wrap': True,
                'font_name': 'Times New Roman'
            }
        )
        data_format = workbook.add_format(
            {
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "font_size": "12",
                'font_name': 'Times New Roman'
            }
        )

        worksheet.merge_range("A1:J1", f"{p_type_name}     {date1} - {date2}", format_0)
        worksheet.write("A2", "TR", merge_format)
        worksheet.write("B2", "FIO", merge_format)
        worksheet.write("C2", "PNFL", merge_format)
        worksheet.write("D2", "Fan", merge_format)
        worksheet.write("E2", "Speaking Part1", merge_format)
        worksheet.write("F2", "Speaking Part2", merge_format)
        worksheet.write("G2", "Speaking Part3", merge_format)
        worksheet.write("H2", "Writing Task1", merge_format)
        worksheet.write("I2", "Writing Task2", merge_format)

        n = len(data)

        for i in range(0, n):
            fio = data[i]['fio']
            pnfl = data[i]['pnfl']
            subject = data[i]['subject']
            p1 = data[i]['p1']
            p2 = data[i]['p2']
            p3 = data[i]['p3']
            t1 = data[i]['t1']
            t2 = data[i]['t2']

            worksheet.write(f"A{3 + i}", i + 1, data_format)
            worksheet.write(f"B{3 + i}", fio, data_format)
            worksheet.write(f"C{3 + i}", pnfl, data_format)
            worksheet.write(f"D{3 + i}", subject, data_format)
            worksheet.write(f"E{3 + i}", p1, data_format)
            worksheet.write(f"F{3 + i}", p2, data_format)
            worksheet.write(f"G{3 + i}", p3, data_format)
            worksheet.write(f"H{3 + i}", t1, data_format)
            worksheet.write(f"I{3 + i}", t2, data_format)
        workbook.close()
        return file_url
    except Exception as e:
        print(f"{e}")
