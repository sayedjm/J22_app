 document.addEventListener("DOMContentLoaded", function() {
        var implementedDate = document.getElementById("date").value;
        if (implementedDate !== "") {
            var implementedDateSpan = document.getElementById("date-span");
            implementedDateSpan.textContent = " (" + calculateDaysAgo(implementedDate, "ingevoerd") + ")";
        }

 
        var contactedDate = document.getElementById("emailed").value;
        if (contactedDate !== "") {
            var contactedDateSpan = document.getElementById("contacted_date-span");
            contactedDateSpan.textContent = " (" + calculateDaysAgo(contactedDate, "contact opgenomen") + ")";
        }

        function calculateDaysAgo(date, action) {
            var today = new Date();
            var parts = date.split("-");
            var day = parseInt(parts[0], 10);
            var month = parseInt(parts[1], 10) - 1; // Months are zero-based in JavaScript Date object
            var year = parseInt(parts[2], 10);
            var implementedDate = new Date(year, month, day);

            if (isSameDay(today, implementedDate)) {
                return "vandaag " + action;
            } else {
                var timeDiff = Math.abs(today.getTime() - implementedDate.getTime());
                var daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24) -1);
                return daysDiff + " dagen geleden";
            }
        }

        function isSameDay(date1, date2) {
            return (
                date1.getFullYear() === date2.getFullYear() &&
                date1.getMonth() === date2.getMonth() &&
                date1.getDate() === date2.getDate()
            );
        }
    });