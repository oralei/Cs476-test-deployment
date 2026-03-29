// --- JAVASCRIPT LOGIC ---

function openFeedback(element) {
    // 1. Get the data from the clicked element's data attributes
    const task = element.getAttribute('data-task');
    const course = element.getAttribute('data-course');
    const grade = element.getAttribute('data-grade');
    const comment = element.getAttribute('data-comment');

    // 2. Populate the Modal
    document.getElementById('modalTitle').innerText = task;
    document.getElementById('modalCourse').innerText = course;
    document.getElementById('modalGrade').innerText = grade + "%";
    document.getElementById('modalComment').innerText = comment;

    // 3. Handle Grade Color in Modal
    const gradeBadge = document.getElementById('modalGrade');
    if (parseInt(grade) < 70) {
        gradeBadge.classList.add('low');
    } else {
        gradeBadge.classList.remove('low');
    }

    // 4. Show the Modal
    document.getElementById('feedbackModal').classList.add('active');
}

function closeFeedbackActual() {
    document.getElementById('feedbackModal').classList.remove('active');
}

// Close if clicking outside the white card (on the background overlay)
function closeFeedback(event) {
    if (event.target.id === 'feedbackModal') {
        closeFeedbackActual();
    }
}