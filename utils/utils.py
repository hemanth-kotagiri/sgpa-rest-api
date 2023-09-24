from .constants import grades


def get_student_info(sel_soup) -> dict:
    """Returns the student information"""

    """ tables[0] consists the information regarding the student """

    tables = sel_soup.find_all("table")
    # print(len(tables))
    # print(tables[0].find_all("tr"))

    # Gathering the student information

    data = []
    for element in list(tables[0].find_all("tr")):
        for bTag in element.find_all("b"):
            data.append(bTag.text)

    student = dict(
        zip(
            [data[i].replace(":", "") for i in range(len(data)) if i % 2 == 0],
            [data[j] for j in range(1, len(data)) if j % 2 != 0],
        )
    )

    return student


def get_results_info(sel_soup):
    """A method to obtain the results object
    tables[1] consists the subject code, subject name, grade and credits
    """

    tables = sel_soup.find_all("table")
    results = []

    for row in tables[1].find_all("tr"):
        bTags = row.find_all("b")
        if not bTags[0].text.isalnum():
            continue
        current_subject = []
        count = 1
        # table_row has 4 elements: subject code, name, grade, credits else
        # table_row has 7 elements: subject code, name, internal, external, total grade, credits
        for b in bTags:
            if count <= 7:
                current_subject.append(b.text)
                count += 1

        if not current_subject:
            continue

        subject_object = {}
        if current_subject and len(current_subject) == 4:
            subject_object["subject_code"] = current_subject[0]
            subject_object["subject_name"] = current_subject[1]
            subject_object["grade_earned"] = current_subject[2]
            subject_object["subject_credits"] = current_subject[3]
        else:
            subject_object["subject_code"] = current_subject[0]
            subject_object["subject_name"] = current_subject[1]
            subject_object["grade_earned"] = current_subject[5]
            subject_object["subject_credits"] = current_subject[6]
            subject_object["internal_marks"] = current_subject[2]
            subject_object["external_marks"] = current_subject[3]
            subject_object["total_marks"] = current_subject[4]

        results.append(subject_object)

    return results


def get_hallticket_helper(roll_number, i):
    if i < 10:
        hallticket = roll_number + "0" + str(i)
    elif i < 100:
        hallticket = roll_number + str(i)
    elif i > 99 and i < 110:
        hallticket = roll_number + "A" + str(i - 100)
    elif i > 109 and i < 120:
        hallticket = roll_number + "B" + str(i - 110)
    elif i > 119 and i < 130:
        hallticket = roll_number + "C" + str(i - 120)
    elif i > 129 and i < 140:
        hallticket = roll_number + "D" + str(i - 130)
    elif i > 139 and i < 150:
        hallticket = roll_number + "E" + str(i - 140)
    elif i > 149 and i < 160:
        hallticket = roll_number + "F" + str(i - 150)
    elif i > 159 and i < 170:
        hallticket = roll_number + "G" + str(i - 160)
    elif i > 169 and i < 180:
        hallticket = roll_number + "H" + str(i - 170)
    elif i > 179 and i < 190:
        hallticket = roll_number + "J" + str(i - 180)
    elif i > 189 and i < 200:
        hallticket = roll_number + "K" + str(i - 190)
    elif i > 199 and i < 210:
        hallticket = roll_number + "L" + str(i - 200)
    elif i > 209 and i < 220:
        hallticket = roll_number + "M" + str(i - 210)
    elif i > 219 and i < 230:
        hallticket = roll_number + "N" + str(i - 220)
    elif i > 229 and i < 240:
        hallticket = roll_number + "P" + str(i - 230)

    return hallticket


def calculate_sgpa(results_object):
    sgpa = 0
    total_credits = 0
    for subject in results_object[1]:
        total_credits += float(subject["subject_credits"])
        grade_earned = subject["grade_earned"]
        if grade_earned == "F" or grade_earned == "-" or grade_earned == "Ab":
            sgpa = 0
            break
        if not subject["grade_earned"] in grades.keys():
            sgpa = 0
            break
        sgpa += grades[subject["grade_earned"]] * float(subject["subject_credits"])

    if total_credits == 0:
        sgpa = 0
    else:
        sgpa = round(sgpa / total_credits, 2)
    results_object.insert(0, {"SGPA": sgpa if sgpa else "FAIL"})

    return results_object


# TODO: Add Docstrings
def exam_codes(code: str):
    arr11 = ["1323", "1358", "1404", "1430", "1467", "1504", "1572", "1615", "1658"]
    arr12 = [
        "1356",
        "1363",
        "1381",
        "1435",
        "1448",
        "1481",
        "1503",
        "1570",
        "1620",
        "1622",
        "1656",
    ]
    arr21 = ["1391", "1425", "1449", "1496", "1560", "1610", "1628", "1667", "1671"]
    arr22 = ["1437", "1447", "1476", "1501", "1565", "1605", "1627", "1663"]
    arr31 = ['1454', '1491', '1550', '1590', '1626', '1639', '1645', '1655','1686']
    arr32 = ['1502', '1555', '1595', '1625', '1638', '1649', '1654','1682','1690']
    arr41 = ["1545", "1585", "1624", "1640", "1644", "1653", '1678']
    arr42 = ['1580', '1600', '1623','1672', '1673','1677','1691']

    if code == "1-1":
        return arr11
    elif code == "1-2":
        return arr12
    elif code == "2-1":
        return arr21
    elif code == "2-2":
        return arr22
    elif code == "3-1":
        return arr31
    elif code == "3-2":
        return arr32
    elif code == "4-1":
        return arr41
    elif code == "4-2":
        return arr42
    elif code == "all":
        return [*arr11, *arr12, *arr21, *arr22, *arr31, *arr32, *arr41, *arr42]
    else:
        return []


def invalid_hallticket(sel_soup):
    if sel_soup.find_all(
        lambda tag: tag.name == "div" and "invalid hallticket number" in tag.text
    ):
        return True
    return False
