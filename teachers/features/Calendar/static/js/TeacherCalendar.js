document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');

  // selectors
  const courseSelect = document.getElementById('courseSelect');
  const studentSelect = document.getElementById('studentSelect');

  // make these available everywhere
  let allEvents = [];
  let calendar = null;

  function colorForType(type) {
    return ({
      assignment: getComputedStyle(document.documentElement).getPropertyValue('--assignment').trim(),
      quiz:       getComputedStyle(document.documentElement).getPropertyValue('--quiz').trim(),
      project:    getComputedStyle(document.documentElement).getPropertyValue('--project').trim(),
      meeting:    getComputedStyle(document.documentElement).getPropertyValue('--meeting').trim(),
    })[type] || '#64748b';
  }

  function applyFilters() {
    if (!calendar) return; // calendar not ready yet

    const course = courseSelect.value;
    const student = studentSelect.value;

    const filtered = allEvents.filter(e => {
      const matchCourse = !course || e.extendedProps.course === course;
      const matchStudent = !student || e.extendedProps.student === student;
      return matchCourse && matchStudent;
    });

    calendar.removeAllEvents();
    calendar.addEventSource(filtered);
  }

  //  hook listeners once
  courseSelect.addEventListener('change', applyFilters);
  studentSelect.addEventListener('change', applyFilters);

  // fetch events, then build calendar once
  fetch(EVENTS_URL)
    .then(response => response.json())
    .then(data => {
      allEvents = data;

      calendar = new FullCalendar.Calendar(calendarEl, {
        height: 520,
        initialView: 'dayGridMonth',
        nowIndicator: true,
        selectable: true,
        editable: true,

        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,listWeek'
        },

        eventDidMount: function (info) {
          const type = info.event.extendedProps.type;
          const bg = colorForType(type);
          info.el.style.backgroundColor = bg;
          info.el.style.color = 'white';
        },

        events: allEvents,

        eventClick: function (info) {
          alert(
            info.event.title +
            "\nStart: " + info.event.start +
            (info.event.end ? "\nEnd: " + info.event.end : "")
          );
        },

        select: function (info) {
          // adds event visually (does not save back to JSON)
          calendar.addEvent({
            title: 'Meeting (new)',
            start: info.startStr,
            end: info.endStr,
            extendedProps: { type: 'meeting', course: '', student: '' }
          });
        }
      });

      calendar.render();

      // apply filters immediately (if dropdown has default value)
      applyFilters();
    })
    .catch(error => console.error("Error loading events:", error));
});