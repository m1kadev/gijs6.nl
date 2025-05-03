function statusMessage(message, type, sleep) {
    const container = document.getElementById("status")

    const messageElement = document.createElement("div")
    messageElement.className = "status-item status-" + type;
    messageElement.innerHTML = message;

    container.appendChild(messageElement);

    setTimeout(() => {
        messageElement.style.animation = "500ms fadeout forwards"
        setTimeout(() => {
            container.removeChild(messageElement);
        }, 500);
    }, sleep);
}

async function refreshAllItems() {
    const response = await fetch("/admin/api/libeditor/list_all");
    if (!response.ok) {
        const errorText = await response.text();
        statusMessage(`Error ${response.status}: ${errorText}`, "error", 8000);
        return;
    }
    const data = await response.json();

    const table = document.getElementById("item-table");
    table.innerHTML = ""; // Clear old content

    const headerRow = document.createElement("tr");

    ["Title", "URL", "Icon", "Delete"].forEach(text => {
        const th = document.createElement("th");
        th.textContent = text;
        headerRow.appendChild(th);
    });

    table.appendChild(headerRow)

    
    data.forEach((listItem, index) => {
        const row = document.createElement("tr");
        row.dataset.listitemIndex = index;
    
        const titleTd = document.createElement("td");
        const titleSpan = document.createElement("span");
        titleSpan.className = "list-item-title";
        titleSpan.contentEditable = true;
        titleSpan.spellcheck = false;
        titleSpan.dataset.ltActive = "false";
        titleSpan.textContent = listItem.title;
        titleTd.appendChild(titleSpan);
    
        const urlTd = document.createElement("td");
        const urlSpan = document.createElement("span");
        urlSpan.className = "list-item-url";
        urlSpan.contentEditable = true;
        urlSpan.spellcheck = false;
        urlSpan.dataset.ltActive = "false";
        urlSpan.textContent = listItem.link;
        urlTd.appendChild(urlSpan);
    
        const iconTd = document.createElement("td");
        const iconSpan = document.createElement("span");
        iconSpan.className = "list-item-icon";
        iconSpan.contentEditable = true;
        iconSpan.spellcheck = false;
        iconSpan.dataset.ltActive = "false";
        iconSpan.textContent = listItem.icon;
    
        const iconPreview = document.createElement("span");
        iconPreview.className = "list-item-iconpreview";
        iconPreview.innerHTML = `<i class="${listItem.icon}"></i>`;
    
        iconTd.appendChild(iconSpan);
        iconTd.appendChild(iconPreview);
    
        const deleteTd = document.createElement("td");
        const deleteSpan = document.createElement("span");
        deleteSpan.className = "list-item-delete";
        deleteSpan.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        deleteTd.appendChild(deleteSpan);
    
        row.appendChild(titleTd);
        row.appendChild(urlTd);
        row.appendChild(iconTd);
        row.appendChild(deleteTd);
    
        table.appendChild(row);
    });

    const listItems = document.querySelectorAll("#item-table tr");

    listItems.forEach(lI => {
        let debounceTimeout;
    
        const executeUpdate = () => {
            clearTimeout(debounceTimeout);
    
            const title = lI.querySelector(".list-item-title").textContent;
            const url = lI.querySelector(".list-item-url").textContent;
            const icon = lI.querySelector(".list-item-icon").textContent;

            const listitemIndex = lI.dataset.listitemIndex;
    
            fetch("/admin/api/libeditor/set_info", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    listitemIndex, title, url, icon
                }),
            })
            .then(async (response) => {
                if (!response.ok) {
                    const errorText = await response.text();
                    statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                    return;
                };
                refreshAllItems();
            })
            .catch((err) => {
                statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
            });
        };
    
        lI.addEventListener('input', function () {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(executeUpdate, 3500);
        });
    
        const inputs = lI.querySelectorAll(".list-item-title, .list-item-url, .list-item-icon");
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                executeUpdate();
            });
        });
    });

    
    const addItemElement = document.getElementById("add-list-item");

    addItemElement.addEventListener("click", function () {
        fetch("/admin/api/libeditor/make_new", {
            method: "POST"
        })
            .then(async (response) => {
                if (!response.ok) {
                    const errorText = await response.text();
                    statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                    return;
                }
                refreshAllItems();
            })
            .catch((err) => {
                statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
            });
    });


    const deleteButtons = document.querySelectorAll(".list-item-delete");

    deleteButtons.forEach(dB => {
        dB.addEventListener("click", function () {
            const dBparent = dB.parentElement.parentElement;
            const dBlistitemIndex = dBparent.dataset.listitemIndex;
            
            if (window.confirm(`Do you really want to delete element #${dBlistitemIndex}?`)) {
                fetch("/admin/api/libeditor/delete_item", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        listitemIndex: dBlistitemIndex
                    }),
                })
                    .then(async (response) => {
                        if (!response.ok) {
                            const errorText = await response.text();
                            statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                            return;
                        }
                        refreshAllItems();
                    })
                    .catch((err) => {
                        statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                    });
            }
        });
    });

    statusMessage('Refreshed! <i class="fa-solid fa-repeat"></i>', "success", 2000);
};


document.addEventListener("DOMContentLoaded", () => {
    refreshAllItems();
});
