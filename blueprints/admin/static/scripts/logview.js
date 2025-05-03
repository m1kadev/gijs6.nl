document.addEventListener("DOMContentLoaded", function() {
    const dateInput = document.getElementById("date-filter-input");

    const today = new Date();
    const todayStr = today.toISOString().split("T")[0];

    const pastDate = new Date();
    pastDate.setDate(today.getDate() - 9);
    const pastDateStr = pastDate.toISOString().split('T')[0];

    dateInput.value = todayStr;
    dateInput.setAttribute("value", todayStr)
    dateInput.max = todayStr;
    dateInput.min = pastDateStr;

    dateInput.addEventListener('change', () => {
        const selected = new Date(dateInput.value);
        const diff = Math.floor((today - selected) / (1000 * 60 * 60 * 24));
        dateInput.dataset.daysAgo = diff;
        updateTable();
    });




    function updateTable() {
        var methods = Array.from(document.querySelectorAll("#method-filter input[type='checkbox']:checked")).map(box => box.value)
        var statuses = Array.from(document.querySelectorAll("#status-filter input[type='checkbox']:checked")).map(box => box.value)

        var path = document.querySelector("#path-filter input").value;

        var url = `/admin/api/logview/listall?days_ago=${dateInput.dataset.daysAgo}&path=` + path;
        if (methods.length > 0) {
            url += "&methods=" + methods.join(",");
        }
        if (statuses.length > 0) {
            url += "&statuses=" + statuses.join(",");
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                var tableBody = document.querySelector("table tbody");
                tableBody.innerHTML = "";

                data.forEach(log => {
                    var row = document.createElement("tr");

                    row.innerHTML = `
                        <td><span class="marked bg-${log.method_color}">${log.method}</span></td>
                        <td>${log.path}</td>
                        <td><span class="marked bg-${log.status_color}">${log.status}</span></td>
                        <td>${log.datetime}</td>
                        <td>${log.ip}</td>
                        <td>${log.user_agent}</td>
                        <td>${log.referrer}</td>
                        <td>${log.protocol}</td>
                        <td>${log.size}</td>
                        <td>${log.response_time}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error("Error:", error);
            });
    };

    updateTable();

    document.querySelectorAll("#filters input").forEach((inputElement) => {
        inputElement.addEventListener("input", () => {
            updateTable();
        });
    });
});
