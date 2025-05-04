document.addEventListener("DOMContentLoaded", async function () {
    const tableBody = document.querySelector("table tbody");

    const http_status_colors = {
        1: "blue",
        2: "green",
        3: "blue",
        4: "yellow",
        5: "red",
    };

    try {
        const response = await fetch("/admin/api/dashboard/list_urls");
        const urlitemdata = await response.json();

        const fetchData = async (urlitem) => {
            try {
                const res = await fetch(urlitem.url, { method: urlitem.method });
                const statusCode = res.status;

                const statusCodeFirstDigit = statusCode.toString().charAt(0);
                const status_color = http_status_colors[statusCodeFirstDigit];

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${urlitem.url}</td>
                    <td><span class="marked bg-${status_color}">${statusCode}</span></td>
                `;
                tableBody.appendChild(row);
            } catch (error) {
                statusMessage(`Error fetching ${url}: ${error}`, "error", 4000);
            }
        };

        for (const urlitem of urlitemdata) {
            fetchData(urlitem);
        }
    } catch (error) {
        console.error("Error fetching URL list:", error);
    }
});

function handleAction(button, endpoint) {
    button.classList.add("loading");

    fetch(endpoint, { method: "POST" })
        .then((response) => {
            button.classList.remove("loading");

            if (response.ok) {
                button.classList.add("done");
                setTimeout(() => {
                    button.classList.remove("done");
                }, 750);

                setTimeout(() => {
                    statusMessage('Refreshing in 3 seconds... <i class="fa-solid fa-repeat"></i>', "success", 2000);
                    setTimeout(() => {
                        window.location.reload(true);
                    }, 3000);
                }, 250);
            } else {
                button.classList.add("error");
                setTimeout(() => {
                    button.classList.remove("error");
                }, 2000);
            }
        })
        .catch(() => {
            button.classList.remove("loading");
            button.classList.add("error");
            setTimeout(() => {
                button.classList.remove("error");
            }, 2000);
        });
}

function softreload(button) {
    handleAction(button, "/admin/api/dashboard/softreload");
}

function forcereload(button) {
    handleAction(button, "/admin/api/dashboard/forcereload");
}

function redeploy(button) {
    handleAction(button, "/admin/api/dashboard/redeploy");
}

function disable(button) {
    handleAction(button, "/admin/api/dashboard/disable");
}
