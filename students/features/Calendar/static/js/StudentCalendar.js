
document.addEventListener('DOMContentLoaded', function ()
{
    const calendarEl = document.getElementById('calendar');
    // For dropdowns
    const courseSelect = document.getElementById('courseSelect');

    //Find the HTML script tag with id "events-data" that stores the calendar events
    const eventsDataElement = document.getElementById('events-data');
    let allEvents = [];

    if (eventsDataElement)
    {
        allEvents = JSON.parse(eventsDataElement.textContent);
    }

    let calendar = null;
    let currentEventSource = null;

    // Helper function to assign colors based on task/event type
    function colorForType(type)
    {
        return ({
            assignment: getComputedStyle(document.documentElement).getPropertyValue('--assignment').trim(),
            quiz:       getComputedStyle(document.documentElement).getPropertyValue('--quiz').trim(),
            project:    getComputedStyle(document.documentElement).getPropertyValue('--project').trim(),
            meeting:    getComputedStyle(document.documentElement).getPropertyValue('--meeting').trim(),
        })[type] || '#64748b';
    }

    // Filter the calendar events based on course dropdown
    function applyFilters() 
    {
        if (!calendar) return; // if calendar not ready yet

        const courseId = courseSelect.value;

        const filtered = allEvents.filter(e => {
            // Check if course matches ie if a course is selected)
            return !courseId || e.extendedProps.course === courseId;
        });

        // Update calendar view
        if (currentEventSource) 
        {
            currentEventSource.remove();
        }
        currentEventSource = calendar.addEventSource(filtered);
    }

    // Hook listener to course dropdown so calendar updates when it changes
    courseSelect.addEventListener('change', applyFilters);

    // Initialize Calendar
    calendar = new FullCalendar.Calendar(calendarEl, {
    height: 520,
    initialView: 'dayGridMonth',
    nowIndicator: true,
    selectable: true,
    editable: false, // Prevents dragging/moving tasks

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

    eventClick: function (info)
    {
        alert(
        info.event.title +
        "\nStart: " + (info.event.startStr ? info.event.startStr : 'N/A') +
        (info.event.endStr ? "\nEnd: " + info.event.endStr : "")
        );
    },
    });

    // Render the calendar to the screen
    calendar.render();
    applyFilters();
});