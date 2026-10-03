async function loadStudents() {
    try {
        const response = await fetch("/students");

        if (!response.ok) {
            throw new Error("Failed to load students");
        }

        const students = await response.json();

        const table = document.getElementById("studentTable");

        if (!table) {
            console.error("studentTable not found");
            return;
        }

        table.innerHTML = "";

        students.forEach(student => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${student.id}</td>
                <td>${student.name}</td>
                <td>${student.math}</td>
                <td>${student.science}</td>
                <td>${student.english}</td>
                <td>${student.computer}</td>
                <td>${student.total}</td>
                <td>${student.average}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {
        console.error("Load Students Error:", error);

        const table = document.getElementById("studentTable");

        if (table) {
            table.innerHTML = `
                <tr>
                    <td colspan="8">
                        Unable to load student records.
                    </td>
                </tr>
            `;
        }
    }
}


// ------------------------------------------------------------
// ADD STUDENT
// ------------------------------------------------------------
async function addStudent() {

    const nameInput = document.getElementById("name");
    const mathInput = document.getElementById("math");
    const scienceInput = document.getElementById("science");
    const englishInput = document.getElementById("english");
    const computerInput = document.getElementById("computer");
    const message = document.getElementById("addMessage");

    if (
        !nameInput ||
        !mathInput ||
        !scienceInput ||
        !englishInput ||
        !computerInput
    ) {
        console.error("Input elements not found.");
        return;
    }

    const name = nameInput.value.trim();

    if (name === "") {

        message.innerHTML =
            '<span class="error">Please enter student name.</span>';

        return;
    }

    const math = Number(mathInput.value);
    const science = Number(scienceInput.value);
    const english = Number(englishInput.value);
    const computer = Number(computerInput.value);

    const marks = [
        math,
        science,
        english,
        computer
    ];

    if (
        marks.some(
            mark =>
                !Number.isFinite(mark) ||
                mark < 0 ||
                mark > 100
        )
    ) {

        message.innerHTML =
            '<span class="error">Marks must be between 0 and 100.</span>';

        return;
    }

    try {

        console.log("Sending student data...");

        const response = await fetch("/add_student", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                math: math,
                science: science,
                english: english,
                computer: computer
            })
        });

        const result = await response.json();

        console.log("Flask response:", result);

        if (!response.ok) {

            message.innerHTML =
                `<span class="error">${result.message}</span>`;

            return;
        }

        if (result.success) {

            message.innerHTML =
                `<span class="success">${result.message}</span>`;

            nameInput.value = "";
            mathInput.value = "";
            scienceInput.value = "";
            englishInput.value = "";
            computerInput.value = "";

            await loadStudents();

            if (typeof loadGraph === "function") {
                await loadGraph();
            }

        } else {

            message.innerHTML =
                `<span class="error">${result.message}</span>`;
        }

    } catch (error) {

        console.error("ADD STUDENT ERROR:", error);

        message.innerHTML =
            `<span class="error">
                Unable to connect to Flask server.
                Check the CMD window.
            </span>`;
    }
}


// ------------------------------------------------------------
// SORT STUDENTS
// ------------------------------------------------------------
async function sortStudents(algorithm) {

    try {

        const response = await fetch(
            "/sort?algorithm=" +
            encodeURIComponent(algorithm)
        );

        if (!response.ok) {
            throw new Error("Sorting failed");
        }

        const data = await response.json();

        const sortInfo =
            document.getElementById("sortInfo");

        const table =
            document.getElementById("rankingTable");

        if (!sortInfo || !table) {
            console.error("Sorting elements not found");
            return;
        }

        sortInfo.innerHTML = `
            <strong>Algorithm:</strong>
            ${data.algorithm.toUpperCase()}
            <br>

            <strong>Comparisons:</strong>
            ${data.comparisons}
            <br>

            <strong>Execution Time:</strong>
            ${data.time} ms
        `;

        table.innerHTML = "";

        data.students.forEach(student => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${student.rank}</td>
                <td>${student.name}</td>
                <td>${student.total}</td>
                <td>${student.average}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {

        console.error("Sorting Error:", error);

        const sortInfo =
            document.getElementById("sortInfo");

        if (sortInfo) {
            sortInfo.innerText =
                "Unable to perform sorting.";
        }
    }
}


// ------------------------------------------------------------
// BINARY SEARCH
// ------------------------------------------------------------
async function binarySearch() {

    const searchInput =
        document.getElementById("searchMark");

    const resultBox =
        document.getElementById("searchResult");

    const stepsBox =
        document.getElementById("searchSteps");

    if (!searchInput || !resultBox || !stepsBox) {
        console.error(
            "Binary Search elements not found"
        );
        return;
    }

    const target = Number(searchInput.value);

    if (!Number.isFinite(target)) {

        resultBox.innerText =
            "Please enter valid total marks.";

        stepsBox.innerHTML = "";

        return;
    }

    try {

        const response = await fetch(
            "/binary_search?target=" + target
        );

        if (!response.ok) {
            throw new Error("Binary search failed");
        }

        const data = await response.json();

        if (data.success) {

            resultBox.innerHTML = `
                <strong>Student Found!</strong>
                <br><br>

                <strong>Name:</strong>
                ${data.student.name}
                <br>

                <strong>Total Marks:</strong>
                ${data.student.total}
                <br>

                <strong>Average:</strong>
                ${data.student.average}
                <br>

                <strong>Comparisons:</strong>
                ${data.comparisons}
            `;

        } else {

            resultBox.innerHTML = `
                <strong>Student Not Found</strong>
                <br><br>

                Comparisons:
                ${data.comparisons}
            `;
        }

        stepsBox.innerHTML =
            "<h3>Binary Search Steps</h3>";

        if (data.steps && data.steps.length > 0) {

            data.steps.forEach((step, index) => {

                stepsBox.innerHTML += `
                    <div class="step">

                        <strong>
                            Step ${index + 1}
                        </strong>

                        <br>

                        Low:
                        ${step.low}

                        <br>

                        High:
                        ${step.high}

                        <br>

                        Mid:
                        ${step.mid}

                        <br>

                        Mid Value:
                        ${step.mid_value}

                    </div>
                `;
            });
        }

    } catch (error) {

        console.error(
            "Binary Search Error:",
            error
        );

        resultBox.innerText =
            "Unable to perform binary search.";

        stepsBox.innerHTML = "";
    }
}


// ------------------------------------------------------------
// RANGE QUERY
// ------------------------------------------------------------
async function rangeQuery() {

    const minInput =
        document.getElementById("minMark");

    const maxInput =
        document.getElementById("maxMark");

    const resultBox =
        document.getElementById("rangeResult");

    if (!minInput || !maxInput || !resultBox) {
        console.error(
            "Range Query elements not found"
        );
        return;
    }

    const minimum = Number(minInput.value);
    const maximum = Number(maxInput.value);

    if (
        !Number.isFinite(minimum) ||
        !Number.isFinite(maximum)
    ) {

        resultBox.innerText =
            "Please enter valid marks.";

        return;
    }

    if (minimum > maximum) {

        resultBox.innerText =
            "Minimum cannot be greater than maximum.";

        return;
    }

    try {

        const response = await fetch(
            `/range_query?min=${minimum}&max=${maximum}`
        );

        if (!response.ok) {
            throw new Error("Range query failed");
        }

        const data = await response.json();

        if (
            !data.students ||
            data.students.length === 0
        ) {

            resultBox.innerText =
                "No students found in this range.";

            return;
        }

        let html = `
            <strong>
                ${data.count} student(s) found
            </strong>

            <br><br>
        `;

        data.students.forEach(student => {

            html += `
                <strong>${student.name}</strong>

                - Total:
                ${student.total}

                - Average:
                ${student.average}

                <br>
            `;
        });

        resultBox.innerHTML = html;

    } catch (error) {

        console.error(
            "Range Query Error:",
            error
        );

        resultBox.innerText =
            "Unable to perform range query.";
    }
}


// ------------------------------------------------------------
// SUBJECT GRAPH
// ------------------------------------------------------------

let subjectChart = null;

async function loadGraph() {

    try {

        const response =
            await fetch("/graph");

        if (!response.ok) {
            throw new Error("Graph loading failed");
        }

        const data =
            await response.json();

        const subjects = [
            "Math",
            "Science",
            "English",
            "Computer"
        ];

        const datasets = [];

        subjects.forEach(subject => {

            datasets.push({

                label: subject,

                data: subjects.map(
                    other => data[subject][other]
                ),

                borderWidth: 2,

                fill: false,

                tension: 0.3
            });
        });

        const canvas =
            document.getElementById(
                "subjectChart"
            );

        if (!canvas) {

            console.error(
                "subjectChart not found"
            );

            return;
        }

        // Chart.js must be loaded
        if (typeof Chart === "undefined") {

            console.error(
                "Chart.js is not loaded."
            );

            return;
        }

        const ctx =
            canvas.getContext("2d");

        if (subjectChart) {
            subjectChart.destroy();
        }

        subjectChart = new Chart(ctx, {

            type: "line",

            data: {

                labels: subjects,

                datasets: datasets
            },

            options: {

                responsive: true,

                plugins: {

                    legend: {
                        position: "bottom"
                    }
                },

                scales: {

                    y: {

                        beginAtZero: true,

                        title: {
                            display: true,

                            text:
                                "Average Mark Difference"
                        }
                    },

                    x: {

                        title: {
                            display: true,

                            text: "Subjects"
                        }
                    }
                }
            }
        });

    } catch (error) {

        console.error(
            "Graph Error:",
            error
        );
    }
}


// ------------------------------------------------------------
// BFS
// ------------------------------------------------------------
async function runBFS() {

    const startElement =
        document.getElementById(
            "startSubject"
        );

    const resultBox =
        document.getElementById(
            "bfsResult"
        );

    if (!startElement || !resultBox) {

        console.error(
            "BFS elements not found"
        );

        return;
    }

    const start =
        startElement.value;

    try {

        const response =
            await fetch(
                `/bfs?start=${encodeURIComponent(start)}`
            );

        if (!response.ok) {
            throw new Error("BFS failed");
        }

        const data =
            await response.json();

        if (!data.success) {

            resultBox.innerText =
                data.message;

            return;
        }

        resultBox.innerHTML = `
            <strong>
                Starting Subject:
            </strong>

            ${data.start}

            <br><br>

            <strong>
                BFS Visit Order:
            </strong>

            <br><br>

            ${data.visit_order.join(" → ")}
        `;

    } catch (error) {

        console.error(
            "BFS Error:",
            error
        );

        resultBox.innerText =
            "Unable to perform BFS.";
    }
}


// ------------------------------------------------------------
// PAGE LOAD
// ------------------------------------------------------------
document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log(
            "Student Result Analyzer loaded."
        );

        loadStudents();

        loadGraph();
    }
);
