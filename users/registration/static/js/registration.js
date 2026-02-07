/**
 * AUTHOR:        Saim Munshi
 * Arguments:   
 * * LAST MODIFIED: [2026-02-04]
 * MODIFIED BY:  
 * * CHANGE LOG:
 *  * PURPOSE:     Handles user authentication logic]
 */
function toggleFields() {
        const isTeacher = document.getElementById('roleTeacher').checked;
        const teacherSection = document.getElementById('teacherFields');
        const studentSection = document.getElementById('studentFields');
        
        if (isTeacher) {
            teacherSection.classList.remove('hidden');
            studentSection.classList.add('hidden');
        } else {
            teacherSection.classList.add('hidden');
            studentSection.classList.remove('hidden');
        }
    }