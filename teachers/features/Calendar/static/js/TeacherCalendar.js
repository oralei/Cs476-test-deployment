document.addEventListener('DOMContentLoaded', function () 
{
    const calendarEl = document.getElementById('calendar');

    // Selectors for dropdowns
    const courseSelect = document.getElementById('courseSelect');
    const studentSelect = document.getElementById('studentSelect');

    // Load events directly from the embedded JSON script tag
    const eventsDataElement = document.getElementById('events-data');
    let allEvents = [];

    if (eventsDataElement)
    {
        allEvents = JSON.parse(eventsDataElement.textContent);
    }

  let calendar = null;

    // Helper function to assign colors based on task/event type
    function colorForType(type)
    {
    return ({
        assignment: getComputedStyle(document.documentElement).getPropertyValue('--assignment').trim(),
        quiz:       getComputedStyle(document.documentElement).getPropertyValue('--quiz').trim(),
        project:    getComputedStyle(document.documentElement).getPropertyValue('--project').trim(),
        meeting:    getComputedStyle(document.documentElement).getPropertyValue('--meeting').trim(),
    })[type] || '#64748b'; // default slate color
    }

    // Filter the calendar events based on dropdown selections
    function applyFilters() 
    {
        if (!calendar) return; // if calendar not ready yet

        const courseId = courseSelect.value;
        const studentId = studentSelect.value;

        const filtered = allEvents.filter(e => 
        {
            // Check if course matches, if a course is selected
            const matchCourse = !courseId || e.extendedProps.course === courseId;
            
            // Check if student ID is in the task's assigned students array, if a student is selected
            const matchStudent = !studentId || (e.extendedProps.students && e.extendedProps.students.includes(studentId));
            
            return matchCourse && matchStudent;
        });

        // Update calendar view
        calendar.removeAllEvents();
        calendar.addEventSource(filtered);
    }

    // Join  listeners to dropdowns so calendar updates when they change
    courseSelect.addEventListener('change', applyFilters);
    studentSelect.addEventListener('change', applyFilters);

    // Initialize Calendar
    calendar = new FullCalendar.Calendar(calendarEl, 
    {
        height: 520,
        initialView: 'dayGridMonth',
        nowIndicator: true,
        selectable: true,
        editable: false,

        headerToolbar: 
        {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,listWeek'
        },

        eventDidMount: function (info)
        {
            const type = info.event.extendedProps.type || 'assignment';
            const bg = colorForType(type);
            info.el.style.backgroundColor = bg;
            info.el.style.borderColor = bg;
            info.el.style.color = 'white';
        },

        // Load in our fetched events
        events: allEvents,

        eventClick: function (info)
        {
            alert(
            info.event.title +
            "\nStart: " + (info.event.startStr ? info.event.startStr : 'N/A') +
            (info.event.endStr ? "\nEnd: " + info.event.endStr : "")
            );
        },

        select: function (info)
        {
            // adds event visually (Note: this does not save back to the database yet)
            calendar.addEvent({
            title: 'Meeting (new)',
            start: info.startStr,
            end: info.endStr,
            extendedProps: { 
                type: 'meeting', 
                course: courseSelect.value || '', 
                // If a student is selected, attach them to the new event
                students: studentSelect.value ? [studentSelect.value] : []
            }
            });
            calendar.unselect();
        }
    });

    // Render the calendar to the screen
    calendar.render();

    // Apply filters just in case the dropdowns have default values loaded
    applyFilters();
});