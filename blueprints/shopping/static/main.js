function statusMessage(message, type, sleep) {
    const container = document.getElementById("status");

    const messageElement = document.createElement("div");
    messageElement.className = "status-item status-" + type;
    messageElement.innerHTML = message;

    container.appendChild(messageElement);

    setTimeout(() => {
        messageElement.style.animation = "500ms fadeout forwards";
        setTimeout(() => {
            container.removeChild(messageElement);
        }, 500);
    }, sleep);
}

async function refreshAllItems() {
    const response = await fetch("/boodschappen/api/list_all");
    if (!response.ok) {
        const errorText = await response.text();
        statusMessage(`Error ${response.status}: ${errorText}`, "error", 8000);
        return;
    }
    const data = await response.json();

    const container = document.getElementById("item-container");
    container.innerHTML = "";

    if (data.length === 0) {
        const addItemDiv = document.createElement("div");
        addItemDiv.id = "no-items";
        addItemDiv.innerHTML = 'Geen items gevonden... <i class="fa-solid fa-face-frown"></i>';

        container.appendChild(addItemDiv);
    } else {
        data.forEach((listItem, index) => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "list-item";
            itemDiv.dataset.listitemIndex = index;

            const checkSpan = document.createElement("span");
            checkSpan.className = "list-item-check" + (listItem.checked ? " checked" : "");
            checkSpan.innerHTML = '<i class="fa-solid fa-check"></i>';

            const titleSpan = document.createElement("span");
            titleSpan.className = "list-item-title";
            titleSpan.contentEditable = true;
            titleSpan.spellcheck = false;
            titleSpan.dataset.ltActive = "false"; // LanguageTool
            titleSpan.textContent = listItem.title;

            const infoSpan = document.createElement("span");
            infoSpan.className = "list-item-info";
            infoSpan.textContent = listItem.info;

            if (listItem.title == "Title") {
                itemDiv.classList.add("new-list-item");
                setTimeout(() => {
                    itemDiv.classList.remove("new-list-item");
                }, 500);
            }

            const deleteSpan = document.createElement("span");
            deleteSpan.className = "list-item-delete";
            deleteSpan.innerHTML = '<i class="fa-solid fa-trash-can"></i>';

            itemDiv.appendChild(checkSpan);
            itemDiv.appendChild(titleSpan);
            itemDiv.appendChild(infoSpan);
            itemDiv.appendChild(deleteSpan);

            container.appendChild(itemDiv);
        });

        const addItemDiv = document.createElement("button");
        addItemDiv.id = "add-list-item";
        addItemDiv.innerHTML = '<i class="fa-solid fa-plus"></i> Item toevoegen';

        container.appendChild(addItemDiv);
    }

    const checkBoxes = document.querySelectorAll(".list-item-check");

    checkBoxes.forEach((cB) => {
        cB.addEventListener("click", function () {
            const parent = cB.parentElement;

            const listitemIndex = parent.dataset.listitemIndex;

            const isNowChecked = !cB.classList.contains("checked");

            fetch("/boodschappen/api/set_checked", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    checked: isNowChecked,
                    listitemIndex: listitemIndex,
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

            cB.classList.toggle("checked");
        });
    });

    const listItems = document.querySelectorAll(".list-item");

    listItems.forEach((lI) => {
        let debounceTimeout;

        const executeUpdate = () => {
            clearTimeout(debounceTimeout);

            const title = lI.querySelector(".list-item-title").textContent;

            const listitemIndex = lI.dataset.listitemIndex;

            fetch("/boodschappen/api/set_info", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    listitemIndex: listitemIndex,
                    title: title,
                }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                        return;
                    }

                    statusMessage('Updated! <i class="fa-solid fa-repeat"></i>', "success", 2000);
                })
                .catch((err) => {
                    statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                });
        };

        lI.addEventListener("input", function () {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(executeUpdate, 3500);
        });

        const inputs = lI.querySelectorAll(".list-item-title");
        inputs.forEach((input) => {
            input.addEventListener("blur", () => {
                executeUpdate();
            });
        });
    });

    const addItemElement = document.getElementById("add-list-item");

    addItemElement.addEventListener("click", function () {
        fetch("/boodschappen/api/make_new", {
            method: "POST",
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

    const deleteAll = document.getElementById("delete-all");

    deleteAll.addEventListener("click", function () {
        fetch("/boodschappen/api/delete_all", {
            method: "DELETE",
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

    const deleteChecked = document.getElementById("delete-checked");

    deleteChecked.addEventListener("click", function () {
        fetch("/boodschappen/api/delete_checked", {
            method: "DELETE",
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

    deleteButtons.forEach((dB) => {
        dB.addEventListener("click", function () {
            const dBparent = dB.parentElement;

            const title = dBparent.querySelector(".list-item-title").textContent;

            const dBlistitemIndex = dBparent.dataset.listitemIndex;

            if (window.confirm(`Wil je echt item #${dBlistitemIndex} '${title}' verwijderen?`)) {
                fetch("/boodschappen/api/delete_item", {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        listitemIndex: dBlistitemIndex,
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
}

document.addEventListener("DOMContentLoaded", () => {
    refreshAllItems();
});
