

// Added by Mark: JavaScript grabs that safely rendered JSON data
document.addEventListener("DOMContentLoaded", function () {
    const courseSelect = document.getElementById("courseSelect");
    const studentSelect = document.getElementById("studentSelect");
    const courseData = JSON.parse(document.getElementById("course-data").textContent);

    courseSelect.addEventListener("change", function () {
        const courseId = this.value;
        studentSelect.innerHTML = ""; // clear previous options

        if (courseData[courseId]) {
            courseData[courseId].forEach(student => {
                const option = document.createElement("option");
                option.value = student.id;
                option.textContent = student.name;
                option.selected = true; // select by default
                studentSelect.appendChild(option);
            });
        }
    });
});

// Added by Saim Munshi: JavaScript grabs that safely rendered JSON data for student built on exisiting logic from marks code.
document.addEventListener("DOMContentLoaded", function () {
    const assignedStudentIds = JSON.parse(document.getElementById("assigned-students-data").textContent);
    const courseData = JSON.parse(document.getElementById("course-data").textContent);

    const courseSelect = document.getElementById("courseSelect");
    const studentSelect = document.getElementById("studentSelect");

    courseSelect.addEventListener("change", function () {
        const courseId = this.value;
        studentSelect.innerHTML = ""; 

        if (courseData[courseId]) {
            courseData[courseId].forEach(student => {
                const option = document.createElement("option");
                option.value = student.id;
                option.textContent = student.full_name;

    
                if (assignedStudentIds.includes(student.id)) {
                    option.selected = true;
                }

                studentSelect.appendChild(option);
            });
        }
    });

    if (courseSelect.value) {
        courseSelect.dispatchEvent(new Event("change"));
    }
});