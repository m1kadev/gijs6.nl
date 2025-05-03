document.addEventListener("DOMContentLoaded", function() {
    function updateTable() {
        let methods = Array.from(document.querySelectorAll("#method-filter input[type='checkbox']:checked")).map(box => box.value)
        let statuses = Array.from(document.querySelectorAll("#status-filter input[type='checkbox']:checked")).map(box => box.value)

        let path = document.querySelector("#path-filter input").value;

        const lognumInput = document.getElementById("lognum-input");

        let url = `/admin/api/logview/listall?log_num=${lognumInput.value}&path=` + path;
        if (methods.length > 0) {
            url += "&methods=" + methods.join(",");
        }
        if (statuses.length > 0) {
            url += "&statuses=" + statuses.join(",");
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                let tableBody = document.querySelector("table tbody");
                tableBody.innerHTML = "";

                data.forEach(log => {
                    let row = document.createElement("tr");

                    row.innerHTML = `
                        <td><span class="marked bg-${log.method_color}">${log.method}</span></td>
                        <td>${log.path}</td>
                        <td><span class="marked bg-${log.status_color}">${log.status}</span></td>
                        <td>${log.datetime}</td>
                        <td>${log.ip}</td>
                        <td>${log.user_agent_formatted}</td>
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

    document.querySelectorAll("#filters input, #lognum-input").forEach((inputElement) => {
        inputElement.addEventListener("input", () => {
            updateTable();
        });
    });
});
