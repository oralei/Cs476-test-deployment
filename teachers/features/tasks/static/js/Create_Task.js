








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

