document.addEventListener("DOMContentLoaded", () => {

    // Added by Matthew/Spooky: Function to retrieve the hidden CSRF token from the DOM
    function getCSRFToken() {
        const tokenElem = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElem ? tokenElem.value : '';
    }

    // Added by Matthew/Spooky: Helper to update the unread count in the UI dynamically
    function decrementUnreadCount() {
        const countElem = document.getElementById('unreadCount');
        if (countElem) {
            let count = parseInt(countElem.textContent, 10);
            if (!isNaN(count) && count > 0) {
                count -= 1;
                countElem.textContent = count;
                
                // Handle grammar (plural vs singular)
                const pluralElem = document.getElementById('unreadPlural');
                if (pluralElem) {
                    pluralElem.textContent = count === 1 ? '' : 's';
                }

                // Hide the alert banner entirely if count reaches 0
                if (count === 0) {
                    const alertElem = document.getElementById('unreadAlert');
                    if (alertElem) alertElem.style.display = 'none';
                }
            }
        }
    }

    // Added by Matthew/Spooky: Event Listeners for "Mark as Read" buttons
    const markReadButtons = document.querySelectorAll('.mark-read-btn');
    markReadButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Prevent double-clicking
            this.disabled = true;

            const url = this.getAttribute('data-url');
            const feedbackId = this.getAttribute('data-id');

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Find the status badge and update it
                    const badge = document.getElementById(`status-${feedbackId}`);
                    if (badge && badge.textContent.trim() === 'Unread') {
                        badge.className = 'badge bg-success';
                        badge.textContent = 'Read';
                        
                        // Lower the unread counter alert
                        decrementUnreadCount();
                    }
                    // Remove the button from the UI so it can't be clicked again
                    this.remove();
                }
            })
            .catch(err => {
                console.error("Mark read error:", err);
                this.disabled = false; // re-enable if there was an error
            });
        });
    });

    // Added by Matthew/Spooky: Event Listeners for "Archive" buttons
    const archiveButtons = document.querySelectorAll('.archive-btn');
    archiveButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            this.disabled = true;

            const url = this.getAttribute('data-url');
            const feedbackId = this.getAttribute('data-id');

            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const feedbackItem = document.getElementById(`feedback-${feedbackId}`);
                    if (feedbackItem) {
                        // 1. If it was unread, handle the transition to Read (backend does this automatically)
                        const badge = document.getElementById(`status-${feedbackId}`);
                        if (badge && badge.textContent.trim() === 'Unread') {
                            badge.className = 'badge bg-success';
                            badge.textContent = 'Read';
                            decrementUnreadCount();
                        }

                        // 2. Adjust styling to match archived items
                        feedbackItem.classList.add('border-secondary', 'opacity-75');
                        
                        // 3. Remove action buttons
                        const markReadBtn = feedbackItem.querySelector('.mark-read-btn');
                        if (markReadBtn) markReadBtn.remove();
                        this.remove(); // Remove the archive button itself

                        // 4. Move element to Archive list visually
                        const archiveContainer = document.getElementById('archiveFeedbackList');
                        if (archiveContainer) {
                            // Clear "No archived feedback." message if it exists
                            const emptyArchiveMsg = archiveContainer.querySelector('p');
                            if (emptyArchiveMsg && emptyArchiveMsg.textContent.includes('No archived feedback')) {
                                emptyArchiveMsg.remove();
                            }
                            // Move the card to the top of the archive list
                            archiveContainer.prepend(feedbackItem);
                        }

                        // 5. If the Active list is now empty, show an empty state message
                        const activeContainer = document.getElementById('activeFeedbackList');
                        if (activeContainer && activeContainer.querySelectorAll('.feedback-item').length === 0) {
                            activeContainer.innerHTML = '<p class="text-muted text-center mt-3">No active feedback.</p>';
                        }
                    }
                }
            })
            .catch(err => {
                console.error("Archive error:", err);
                this.disabled = false;
            });
        });
    });

});