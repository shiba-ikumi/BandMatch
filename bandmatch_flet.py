import flet as ft
import csv


# =========================
# スコア計算
# =========================
def calc_part_score(person, part):
    attendance = person["attendance"]

    if part == "1st":
        return person["1st"] + attendance * 0.3

    elif part == "2nd":
        return person["2nd"] + attendance * 0.3

    elif part == "3rd":
        return person["3rd"] + attendance * 0.3

    elif part == "picc":
        return person["picc"] + attendance * 0.2 + person["picc_wish"]

    return 0
PART_LIMIT = {
    "1st": 3,
    "2nd": 3,
    "3rd": 3,
    "picc": 1
}


def assign_parts(assignment_data):

    remaining = assignment_data.copy()

    first_members = []
    second_members = []
    third_members = []
    picc_members = []
    drop_members = []

    # =========================
    # 出席率40%以下は強制降り
    # =========================
    forced_drop = [
        p for p in remaining
        if p["attendance"] <= 40
    ]

    for p in forced_drop:
        drop_members.append(p["name"])
        remaining.remove(p)

    # =========================
    # picc選出
    # =========================
    picc_candidates = [
        p for p in remaining
        if p["picc_wish"] >= 70
        and p["attendance"] >= 80
    ]

    if picc_candidates:

        best_picc = max(
            picc_candidates,
            key=lambda x:
                x["picc"] +
                x["attendance"] * 0.2
        )

        picc_members.append(
            best_picc["name"]
        )

        remaining.remove(best_picc)

    # =========================
    # 現在人数
    # =========================
    part_counts = {
        "1st": 0,
        "2nd": 0,
        "3rd": 0
    }

    # =========================
    # 強い希望順に並べる
    # =========================
    remaining.sort(
        key=lambda x: max(
            x["1st"],
            x["2nd"],
            x["3rd"]
        ),
        reverse=True
    )

    # =========================
    # 割り当て
    # =========================
    for person in remaining:

        scores = [
            ("1st", person["1st"]),
            ("2nd", person["2nd"]),
            ("3rd", person["3rd"])
        ]

        scores.sort(
            key=lambda x: x[1],
            reverse=True
        )

        assigned = False

        for part, score in scores:

            if (
                part == "1st"
                and part_counts["1st"] < PART_LIMIT["1st"]
            ):
                first_members.append(
                    person["name"]
                )
                part_counts["1st"] += 1
                assigned = True
                break

            elif (
                part == "2nd"
                and part_counts["2nd"] < PART_LIMIT["2nd"]
            ):
                second_members.append(
                    person["name"]
                )
                part_counts["2nd"] += 1
                assigned = True
                break

            elif (
                part == "3rd"
                and part_counts["3rd"] < PART_LIMIT["3rd"]
            ):
                third_members.append(
                    person["name"]
                )
                part_counts["3rd"] += 1
                assigned = True
                break

        if not assigned:
            drop_members.append(
                person["name"]
            )

    return (
        first_members,
        second_members,
        third_members,
        picc_members,
        drop_members
    )




# =========================
# メイン
# =========================
def main(page: ft.Page):

    page.title = "BandMatch"
    page.scroll = ft.ScrollMode.AUTO

    # ---------------- UI ----------------
    title = ft.Text("🎷 BandMatch", size=30, weight=ft.FontWeight.BOLD)

    name = ft.TextField(label="名前")

    grade = ft.Dropdown(
        label="学年",
        options=[
            ft.dropdown.Option("08"),
            ft.dropdown.Option("07"),
            ft.dropdown.Option("06"),
            ft.dropdown.Option("05")
        ]
    )

    first_score = ft.TextField(label="1st希望度(0~100)")
    second_score = ft.TextField(label="2nd希望度(0~100)")
    third_score = ft.TextField(label="3rd希望度(0~100)")
    picc_score = ft.TextField(label="picc希望度(0~100)")
    drop_score = ft.TextField(label="降り希望度80~100")
    attendance = ft.TextField(label="出席率（％）")

    result = ft.Text(size=18)
    member_list = ft.Text(size=16)
    member_count = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    part_summary = ft.Text(size=16)
    ranking_text = ft.Text(size=16)
    score_text = ft.Text(size=16)
    assignment_Text = ft.Text(size=16)
    assignment_table = ft.DataTable(
        columns=
        [ft.DataColumn(ft.Text("名前")),
        ft.DataColumn(ft.Text("担当パート"))
        ],
        rows=[]
        
    )

    # =========================
    # submit
    # =========================
    def submit(e):

        # --- 保存 ---
        with open("bandmatch.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                name.value,
                grade.value,
                first_score.value,
                second_score.value,
                third_score.value,
                picc_score.value,
                drop_score.value,
                attendance.value
            ])

        # --- 表示 ---
        result.value = f"""
名前：{name.value}
学年：{grade.value}

第1希望度：{first_score.value}
第2希望度：{second_score.value}
第3希望度：{third_score.value}
picc希望度：{picc_score.value}

出席率：{attendance.value}%
"""

        # =========================
        # データ読み込み
        # =========================
        count = 0
        first_count = 0
        second_count = 0
        third_count = 0
        picc_count = 0

       

        ranking_data = []
        score_data = []
        assignment_data = []

        text = "現在の登録者\n\n"

        with open("bandmatch.csv", "r", encoding="utf-8") as file:
            for line in file:
                if line.strip() == "":
                    continue

                count += 1
                data = line.strip().split(",")

                attendance_score = int(data[7])

                grade_bonus = {
                    "06": 40,
                    "05": 30,
                    "07": 20
                }.get(data[1], 10)

                first_total = attendance_score + grade_bonus + int(data[2])
                second_total = attendance_score + grade_bonus + int(data[3])
                third_total = attendance_score + grade_bonus + int(data[4])
                picc_total = attendance_score + grade_bonus + int(data[5])

                assignment_data.append({
                    "name": data[0],
                    "1st": first_total,
                    "2nd": second_total,
                    "3rd": third_total,
                    "picc": picc_total,
                    "picc_wish": int(data[5]),
                    "drop_wish":int(data[6]),
                    "attendance": attendance_score
                })

                score_data.append(
                    (data[0], first_total, second_total, third_total, picc_total,int(data[6]))
                )

                ranking_data.append((data[0], attendance_score))

                text += f"{data[0]}({data[1]})\n"

        # =========================
        # スコア表示
        # =========================
        score_result = "🥁BandMatchスコア\n\n"

        for person in score_data:
            score_result += (
                f"{person[0]}\n"
                f"1st:{person[1]}\n"
                f"2nd:{person[2]}\n"
                f"3rd:{person[3]}\n"
                f"picc:{person[4]}\n"
                f"降り:{person[5]}\n\n"
            )

        score_text.value = score_result

        # =========================
        # パート割り当て
        # =========================
        first_members, second_members, third_members, picc_members, drop_members = assign_parts(assignment_data)

        with open("result_log.csv","a",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)

            for member in first_members:
                writer.writerow([member,"1st"])
            for member in second_members:
                writer.writerow([member,"2nd"])
            for member in third_members:
                writer.writerow([member,"3rd"])
            for member in picc_members:
                writer.writerow([member,"picc"])
            for member in drop_members:
                writer.writerow([member,"drop"])
        
        assignment_table.rows.clear()

        for member in picc_members:
            assignment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member)),
                        ft.DataCell(ft.Text("picc"))
                    ]
                )
            )
        for member in first_members:
            assignment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member)),
                        ft.DataCell(ft.Text("1st"))
                    ]
                )
            )

        for member in second_members:
            assignment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member)),
                        ft.DataCell(ft.Text("2nd"))
                    ]
                )
            )

        for member in third_members:
            assignment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member)),
                        ft.DataCell(ft.Text("3rd"))
                    ]
                )
            )

        for member in drop_members:
            assignment_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(member)),
                        ft.DataCell(ft.Text("降り"))
                    ]
                )
            )
                

        assignment_Text.value = (
            "🎵パート割り結果\n\n"
            f"picc : {', '.join(picc_members)}\n"
            f"1st : {', '.join(first_members)}\n"
            f"2nd : {', '.join(second_members)}\n"
            f"3rd : {', '.join(third_members)}\n"
            f"降り : {', '.join(drop_members)}\n"
        )

        # =========================
        # ランキング
        # =========================
        ranking_data.sort(key=lambda x: x[1], reverse=True)

        ranking_result = "🏆出席率ランキング🏅\n\n"

        for i, person in enumerate(ranking_data):
            ranking_result += f"{i+1}位 {person[0]} {person[1]}%\n"

        ranking_text.value = ranking_result

        # =========================
        # 希望数
        # =========================
        part_summary.value = f"""
1st希望:{first_count}人
2nd希望:{second_count}人
3rd希望:{third_count}人
picc希望:{picc_count}人
降り希望:{drop_members}人
"""

        member_list.value = text
        member_count.value = f"現在の登録者数:{count}人"

        page.update()

    # =========================
    # UI配置
    # =========================
    page.add(
        title,
        name,
        grade,
        first_score,
        second_score,
        third_score,
        picc_score,
        drop_score,
        attendance,
        ft.ElevatedButton("登録", on_click=submit),
        result,
        member_count,
        part_summary,
        member_list,
        ranking_text,
        score_text,
        assignment_Text,
        assignment_table
    )


ft.app(target=main)