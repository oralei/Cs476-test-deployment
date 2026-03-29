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
                option.textContent = student.name;

                // Bug fix: Default to all selected if no specific assignments exist yet
                if (assignedStudentIds.length === 0 || assignedStudentIds.includes(student.id)) {
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


// Added by Saim Munshi: JavaScript logic for handling unaccaptable start and due date .
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const startInput = document.getElementById('start_date');
    const dueInput = document.getElementById('due_date');
    const errorDiv = document.getElementById('js-error');

    form.addEventListener('submit', function (event) {
        let errors = [];
        const now = new Date();
        const startDate = new Date(startInput.value);
        const dueDate = new Date(dueInput.value);

        // Added by Saim Munshi: clear previous errors
        errorDiv.style.display = 'none';
        errorDiv.innerHTML = '';

        // Added by Saim Munshi: check if start date is in the past
        if (startDate < now) {
            errors.push("Start date cannot be in the past.");
        }

        // Added by Saim Munshi: check if start date is in the past
        if (dueDate < now) {
            errors.push("Due date cannot be in the past.");
        }

        // Added by Saim Munshi: Due Date is before Start Date
        if (dueDate <= startDate) {
            errors.push("Due date must be after the start date.");
        }

        if (errors.length > 0) {

            event.preventDefault();

            errorDiv.style.display = 'block';
            for (let i = 0; i < errors.length; i++) {
                let err = errors[i];
                errorDiv.innerHTML += '<div>' + err + '</div>';
            }
           
        }
    });
});