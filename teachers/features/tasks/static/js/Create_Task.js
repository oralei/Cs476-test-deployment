
    /*Added by Saim Munshi: This is code block deal with the button and content for the side panel for task map and conetent summary */
    const taskMapButton = document.getElementById("taskmap-btn");
    const summaryButton = document.getElementById("summary-btn");
    let summaryContent = document.getElementById("summary-content-div");
    let taskMapContent = document.getElementById("task-map-content-div");
    const courseTitleContainer = document.getElementById("course-title-container");
    /*Added by Saim Munshi: This is code block deal with the button and content for the side panel for task map and conetent summary */
    const overviewButton = document.getElementById("overview-button");
    const existingCourseButton = document.getElementById("existing-course-button");

    /*___________________________________________________________________________________________________________________________________*/
    const courseTitle = document.getElementById("courseSelect");
    const courseTitleNode = document.getElementById("course-node-title");
    const updateButton = document.getElementById("Update-Course");
    const addButton = document.getElementById("Add-Task");
    const deleteButton = document.getElementById("Delete-Task");

    const courseTask = document.getElementById("Course-Task");
    const courseDescription = document.getElementById("Course-Description");
    
    const descriptionDisplay = document.getElementById("course-description-display");
    const descriptionNodeDisplay = document.getElementById("roadmap-body-div");
    const taskDateInput = document.getElementById("Task-Date");
    const taskTypeSelect = document.getElementById("Task-Type");
    
   
    const overviewFormContent = document.getElementById("course-creation-form");
    const existingCourseContent = document.getElementById("existing-courses-overview");
    /*___________________________________________________________________________________________________________________________________*/

    /* Task Creation Panel And Task Map And Summary Panel Overview */

    /** Added by Saim Munshi:  This is code block deal with the button and content for the side panel for task map and conetent summary and nav buttons **/

    taskMapButton.addEventListener('click', (e) => {
        e.preventDefault();
        taskMapButton.style.backgroundColor = "#007bff"
        taskMapButton.style.color = "white"
        summaryButton.style.backgroundColor = "white"
        summaryButton.style.color = "black"
        taskMapContent.classList.remove("hidden-content1");
        summaryContent.classList.add("hidden-content1");
    });


    summaryButton.addEventListener('click', (e) => {
        e.preventDefault();
        summaryButton.style.backgroundColor = "#007bff"
        summaryButton.style.color = "white"
        taskMapButton.style.backgroundColor = "white"
        taskMapButton.style.color = "black"
        summaryContent.classList.remove("hidden-content1");
        taskMapContent.classList.add("hidden-content1");
    });

    /** Added by Saim Munshi:  This is code block deal with the button and content for the side panel for task map and conetent summary and nav buttons **/
    existingCourseButton.addEventListener('click', (e) => {
        e.preventDefault();
        existingCourseButton.style.backgroundColor = "#007bff"
        existingCourseButton.style.color = "white"
        overviewButton.style.backgroundColor = "white"
        overviewButton.style.color = "black"

        overviewFormContent.classList.add("hidden-content1");
        existingCourseContent.classList.remove("hidden-content1");
    });

    /*Added by Saim Munshi: This is code block deal with the button and content for the side panel for task map and conetent summary and nav buttons */

    overviewButton.addEventListener('click', (e) => {
        e.preventDefault();
        overviewButton.style.backgroundColor = "#007bff"
        overviewButton.style.color = "white"
        existingCourseButton.style.backgroundColor = "white"
        existingCourseButton.style.color = "black"
        existingCourseContent.classList.add("hidden-content1");
        overviewFormContent.classList.remove("hidden-content1");
    });
    /** Added by Saim Munshi:  button for side navigation panel **/

    