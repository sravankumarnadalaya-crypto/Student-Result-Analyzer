from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import time

# ============================================================
# FLASK CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

DATABASE = os.path.join(BASE_DIR, "result_analyzer.db")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            math INTEGER NOT NULL,
            science INTEGER NOT NULL,
            english INTEGER NOT NULL,
            computer INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# GET STUDENTS
# ============================================================

@app.route("/students", methods=["GET"])
def get_students():

    conn = None

    try:

        conn = get_db()

        rows = conn.execute("""
            SELECT *
            FROM students
            ORDER BY id
        """).fetchall()

        students = []

        for row in rows:

            total = (
                row["math"]
                + row["science"]
                + row["english"]
                + row["computer"]
            )

            average = total / 4

            students.append({
                "id": row["id"],
                "name": row["name"],
                "math": row["math"],
                "science": row["science"],
                "english": row["english"],
                "computer": row["computer"],
                "total": total,
                "average": round(average, 2)
            })

        return jsonify(students)

    except Exception as e:

        print("GET STUDENTS ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        if conn:
            conn.close()


# ============================================================
# ADD STUDENT
# ============================================================

@app.route("/add_student", methods=["POST"])
def add_student():

    conn = None

    try:

        print("\n========== ADD STUDENT REQUEST ==========")

        # Get JSON
        data = request.get_json(silent=True)

        print("Received JSON:", data)

        if data is None:

            return jsonify({
                "success": False,
                "message": "No JSON data received."
            }), 400

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        name = str(
            data.get("name", "")
        ).strip()

        if not name:

            return jsonify({
                "success": False,
                "message": "Student name is required."
            }), 400

        # ----------------------------------------------------
        # MARKS
        # ----------------------------------------------------

        math_value = data.get("math")
        science_value = data.get("science")
        english_value = data.get("english")
        computer_value = data.get("computer")

        print("Math:", math_value)
        print("Science:", science_value)
        print("English:", english_value)
        print("Computer:", computer_value)

        # Check missing values

        if math_value is None:
            return jsonify({
                "success": False,
                "message": "Math mark is required."
            }), 400

        if science_value is None:
            return jsonify({
                "success": False,
                "message": "Science mark is required."
            }), 400

        if english_value is None:
            return jsonify({
                "success": False,
                "message": "English mark is required."
            }), 400

        if computer_value is None:
            return jsonify({
                "success": False,
                "message": "Computer mark is required."
            }), 400

        # ----------------------------------------------------
        # CONVERT TO INTEGER
        # ----------------------------------------------------

        try:

            math = int(float(math_value))
            science = int(float(science_value))
            english = int(float(english_value))
            computer = int(float(computer_value))

        except (ValueError, TypeError):

            return jsonify({
                "success": False,
                "message": "Marks must be valid numbers."
            }), 400

        # ----------------------------------------------------
        # MARK VALIDATION
        # ----------------------------------------------------

        marks = [
            math,
            science,
            english,
            computer
        ]

        for mark in marks:

            if mark < 0 or mark > 100:

                return jsonify({
                    "success": False,
                    "message": "Marks must be between 0 and 100."
                }), 400

        # ----------------------------------------------------
        # INSERT INTO DATABASE
        # ----------------------------------------------------

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (
                name,
                math,
                science,
                english,
                computer
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            math,
            science,
            english,
            computer
        ))

        conn.commit()

        student_id = cursor.lastrowid

        print("Student inserted successfully.")
        print("Student ID:", student_id)
        print("=========================================\n")

        return jsonify({
            "success": True,
            "message": "Student added successfully!",
            "id": student_id
        }), 200

    except sqlite3.Error as e:

        print("SQLITE ERROR:", e)

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": "Database error: " + str(e)
        }), 500

    except Exception as e:

        print("ADD STUDENT ERROR:", e)

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": "Server error: " + str(e)
        }), 500

    finally:

        if conn:
            conn.close()


# ============================================================
# GET STUDENT DATA
# ============================================================

def get_student_data():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM students
        ORDER BY id
    """).fetchall()

    conn.close()

    students = []

    for row in rows:

        total = (
            row["math"]
            + row["science"]
            + row["english"]
            + row["computer"]
        )

        students.append({

            "id": row["id"],

            "name": row["name"],

            "math": row["math"],

            "science": row["science"],

            "english": row["english"],

            "computer": row["computer"],

            "total": total,

            "average": round(total / 4, 2)

        })

    return students


# ============================================================
# BUBBLE SORT
# ============================================================

def bubble_sort(students):

    students = students.copy()

    comparisons = 0

    n = len(students)

    for i in range(n):

        for j in range(0, n - i - 1):

            comparisons += 1

            if students[j]["total"] < students[j + 1]["total"]:

                students[j], students[j + 1] = (
                    students[j + 1],
                    students[j]
                )

    return students, comparisons


# ============================================================
# MERGE SORT
# ============================================================

def merge_sort(students):

    if len(students) <= 1:

        return students, 0

    mid = len(students) // 2

    left, left_count = merge_sort(
        students[:mid]
    )

    right, right_count = merge_sort(
        students[mid:]
    )

    comparisons = left_count + right_count

    result = []

    i = 0
    j = 0

    while i < len(left) and j < len(right):

        comparisons += 1

        if left[i]["total"] >= right[j]["total"]:

            result.append(left[i])
            i += 1

        else:

            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])

    return result, comparisons


# ============================================================
# SORT
# ============================================================

@app.route("/sort", methods=["GET"])
def sort_students():

    try:

        algorithm = request.args.get(
            "algorithm",
            "merge"
        ).lower()

        students = get_student_data()

        start = time.perf_counter()

        if algorithm == "bubble":

            sorted_students, comparisons = bubble_sort(
                students
            )

        else:

            sorted_students, comparisons = merge_sort(
                students
            )

            algorithm = "merge"

        end = time.perf_counter()

        for index, student in enumerate(sorted_students):

            student["rank"] = index + 1

        return jsonify({

            "students": sorted_students,

            "algorithm": algorithm,

            "comparisons": comparisons,

            "time": round(
                (end - start) * 1000,
                4
            )

        })

    except Exception as e:

        print("SORT ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# BINARY SEARCH
# ============================================================

@app.route("/binary_search", methods=["GET"])
def binary_search():

    try:

        target = request.args.get(
            "target",
            type=int
        )

        if target is None:

            return jsonify({
                "success": False,
                "message": "Enter total marks."
            }), 400

        students = get_student_data()

        students.sort(
            key=lambda student: student["total"]
        )

        low = 0
        high = len(students) - 1

        comparisons = 0

        steps = []

        found = None

        while low <= high:

            mid = (low + high) // 2

            comparisons += 1

            steps.append({

                "low": low,

                "high": high,

                "mid": mid,

                "mid_value":
                    students[mid]["total"]

            })

            if students[mid]["total"] == target:

                found = students[mid]

                break

            elif students[mid]["total"] < target:

                low = mid + 1

            else:

                high = mid - 1

        return jsonify({

            "success": found is not None,

            "student": found,

            "comparisons": comparisons,

            "steps": steps

        })

    except Exception as e:

        print("BINARY SEARCH ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# RANGE QUERY
# ============================================================

@app.route("/range_query", methods=["GET"])
def range_query():

    try:

        minimum = request.args.get(
            "min",
            type=int
        )

        maximum = request.args.get(
            "max",
            type=int
        )

        if minimum is None or maximum is None:

            return jsonify({
                "success": False,
                "message": "Enter minimum and maximum."
            }), 400

        if minimum > maximum:

            return jsonify({
                "success": False,
                "message":
                    "Minimum cannot be greater than maximum."
            }), 400

        students = get_student_data()

        result = [

            {
                "id": student["id"],
                "name": student["name"],
                "total": student["total"],
                "average": student["average"]
            }

            for student in students

            if minimum <= student["total"] <= maximum

        ]

        return jsonify({

            "success": True,

            "count": len(result),

            "students": result

        })

    except Exception as e:

        print("RANGE QUERY ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# GRAPH
# ============================================================

@app.route("/graph", methods=["GET"])
def graph():

    try:

        conn = get_db()

        rows = conn.execute("""
            SELECT
                math,
                science,
                english,
                computer
            FROM students
        """).fetchall()

        conn.close()

        subjects = [
            "Math",
            "Science",
            "English",
            "Computer"
        ]

        graph_data = {}

        for subject1 in subjects:

            graph_data[subject1] = {}

            for subject2 in subjects:

                if subject1 == subject2:

                    graph_data[subject1][subject2] = 0

                    continue

                total_difference = 0

                for row in rows:

                    value1 = row[
                        subject1.lower()
                    ]

                    value2 = row[
                        subject2.lower()
                    ]

                    total_difference += abs(
                        value1 - value2
                    )

                if len(rows) > 0:

                    average_difference = (
                        total_difference /
                        len(rows)
                    )

                else:

                    average_difference = 0

                graph_data[
                    subject1
                ][subject2] = round(
                    average_difference,
                    2
                )

        return jsonify(graph_data)

    except Exception as e:

        print("GRAPH ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# BFS
# ============================================================

@app.route("/bfs", methods=["GET"])
def bfs():

    try:

        start_subject = request.args.get(
            "start",
            "Math"
        )

        subject_graph = {

            "Math": [
                "Science",
                "English"
            ],

            "Science": [
                "Math",
                "Computer"
            ],

            "English": [
                "Math",
                "Computer"
            ],

            "Computer": [
                "Science",
                "English"
            ]

        }

        if start_subject not in subject_graph:

            return jsonify({
                "success": False,
                "message": "Invalid subject."
            }), 400

        queue = [start_subject]

        visited = set()

        visit_order = []

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            visit_order.append(current)

            for neighbor in subject_graph[current]:

                if neighbor not in visited:

                    queue.append(neighbor)

        return jsonify({

            "success": True,

            "start": start_subject,

            "visit_order": visit_order

        })

    except Exception as e:

        print("BFS ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    create_database()

    print("\n==============================================")
    print("STUDENT RESULT ANALYZER")
    print("==============================================")
    print("Database:", DATABASE)
    print("URL: http://127.0.0.1:5000")
    print("==============================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )