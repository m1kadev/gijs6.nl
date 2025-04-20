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

async function refreshAllCollections() {
    const response = await fetch("/proli/api/list_all");
    if (!response.ok) {
        const errorText = await response.text();
        statusMessage(`Error ${response.status}: ${errorText}`, "error", 8000);
        return;
    }
    const data = await response.json();

    const container = document.getElementById("collection-container");
    container.innerHTML = ""; // Clear old content

    for (const [colTitle, colList] of Object.entries(data)) {
        // Create collection wrapper
        const collectionDiv = document.createElement("div");
        collectionDiv.className = "collection";
        collectionDiv.dataset.collection = colTitle;

        // Collection header
        const collectionHeader = document.createElement("div");
        collectionHeader.className = "collection-header";

        // Collection title
        const titleSpan = document.createElement("span");
        titleSpan.className = "collection-title";
        titleSpan.textContent = colTitle;
        titleSpan.contentEditable = true;
        collectionDiv.spellcheck = false;
        collectionDiv.dataset.ltActive = "false"; // LanguageTool
        collectionHeader.appendChild(titleSpan);

        // Collection delete
        const colDelete = document.createElement("span");
        colDelete.className = "collection-delete";
        colDelete.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
        collectionHeader.appendChild(colDelete);

        collectionDiv.appendChild(collectionHeader);

        // List container
        const listContainer = document.createElement("div");
        listContainer.className = "list-container";
        listContainer.dataset.collection = colTitle;

        colList.forEach((listItem, index) => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "list-item";
            itemDiv.dataset.collection = colTitle;
            itemDiv.dataset.listitemIndex = index;

            const checkSpan = document.createElement("span");
            checkSpan.className = "list-item-check" + (listItem.check ? " checked" : "");
            checkSpan.innerHTML = '<i class="fa-solid fa-check"></i>';

            const titleSpan = document.createElement("span");
            titleSpan.className = "list-item-title";
            titleSpan.contentEditable = true;
            titleSpan.spellcheck = false;
            titleSpan.dataset.ltActive = "false"; // LanguageTool
            titleSpan.textContent = listItem.title;

            const datetimeSpan = document.createElement("span");
            datetimeSpan.className = "list-item-datetime";
            datetimeSpan.textContent = listItem.datetime;

            const contentSpan = document.createElement("span");
            contentSpan.className = "list-item-content";
            contentSpan.contentEditable = true;
            contentSpan.spellcheck = false;
            contentSpan.dataset.ltActive = "false"; // LanguageTool
            contentSpan.textContent = listItem.content;

            const deleteSpan = document.createElement("span");
            deleteSpan.className = "list-item-delete";
            deleteSpan.innerHTML = '<i class="fa-solid fa-trash-can"></i>';

            itemDiv.appendChild(checkSpan);
            itemDiv.appendChild(titleSpan);
            itemDiv.appendChild(datetimeSpan);
            itemDiv.appendChild(contentSpan);
            itemDiv.appendChild(deleteSpan);

            listContainer.appendChild(itemDiv);
        });

        const addItemDiv = document.createElement("div");
        addItemDiv.className = "list-item add-list-item";
        addItemDiv.innerHTML = '<i class="fa-solid fa-plus"></i> Add list item';

        listContainer.appendChild(addItemDiv);
        collectionDiv.appendChild(listContainer);
        container.appendChild(collectionDiv);
    };

    const addCollectionDiv = document.createElement("div");
    addCollectionDiv.id = "add-collection";
    addCollectionDiv.className = "collection";
    addCollectionDiv.innerHTML = '<i class="fa-solid fa-plus"></i> Add collection';

    container.appendChild(addCollectionDiv);
    


        
    const checkBoxes = document.querySelectorAll(".list-item-check");

    checkBoxes.forEach(cB => {
        cB.addEventListener("click", function () {
            const parent = cB.parentElement;

            const collection = parent.dataset.collection;
            const listitemIndex = parent.dataset.listitemIndex;

            const isNowChecked = !cB.classList.contains("checked"); // so this will be the state after the toggle

            fetch("/proli/api/set_checked", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    checked: isNowChecked,
                    collection: collection,
                    listitemIndex: listitemIndex
                }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                        return;
                    }
                    refreshAllCollections();
                })
                .catch((err) => {
                    statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                });
            

            cB.classList.toggle("checked")
        });
    });


    const listItems = document.querySelectorAll(".list-item");

    listItems.forEach(lI => {
        let debounceTimeout;

        lI.addEventListener('input', function () {
            clearTimeout(debounceTimeout);

            debounceTimeout = setTimeout(() => {
                const title = lI.querySelector(".list-item-title").textContent;
                const content = lI.querySelector(".list-item-content").textContent;

                
                const datetimeElement = lI.querySelector(".list-item-datetime");
                const newDate = new Date().toISOString();
                datetimeElement.textContent = newDate

                const collection = lI.dataset.collection;
                const listitemIndex = lI.dataset.listitemIndex;

                fetch("/proli/api/set_info", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        listitemIndex: listitemIndex,
                        collection: collection,
                        title: title,
                        datetime: newDate,
                        content: content,
                    }),
                })
                    .then(async (response) => {
                        if (!response.ok) {
                            const errorText = await response.text();
                            statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                            return;
                        }
                        refreshAllCollections();
                    })
                    .catch((err) => {
                        statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                    });
            }, 2000); // wait 2 seconds after last input
        });
    });


    const addItemElements = document.querySelectorAll(".add-list-item");

    addItemElements.forEach(aIE => {
        aIE.addEventListener("click", function () {
            const aIEParent = aIE.parentElement;
            const aIECollection = aIEParent.dataset.collection;

            fetch("/proli/api/make_new", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    collection: aIECollection
                }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                        return;
                    }
                    refreshAllCollections();
                })
                .catch((err) => {
                    statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                });
        });
    });


    const deleteButtons = document.querySelectorAll(".list-item-delete");

    deleteButtons.forEach(dB => {
        dB.addEventListener("click", function () {
            const dBparent = dB.parentElement;

            const dBcollection = dBparent.dataset.collection;
            const dBlistitemIndex = dBparent.dataset.listitemIndex;

            fetch("/proli/api/delete_item", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    collection: dBcollection,
                    listitemIndex: dBlistitemIndex
                }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                        return;
                    }
                    refreshAllCollections();
                })
                .catch((err) => {
                    statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                });
        });
    });


    const addCollection = document.getElementById("add-collection");

    addCollection.addEventListener("click", function () {
        fetch("/proli/api/new_collection", {
            method: "POST"
        })
            .then(async (response) => {
                if (!response.ok) {
                    const errorText = await response.text();
                    statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                    return;
                }
                refreshAllCollections();
            })
            .catch((err) => {
                statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
            });
    });


    const collectionTitles = document.querySelectorAll(".collection-title");

    collectionTitles.forEach(cT => {
        let debounceTimeout;

        cT.addEventListener('input', function () {
            clearTimeout(debounceTimeout);

            debounceTimeout = setTimeout(() => {
                const cTParent = cT.parentElement.parentElement;
                const collection = cTParent.dataset.collection;

                const newName = cT.textContent;

                fetch("/proli/api/rename_collection", {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        oldName: collection,
                        newName: newName
                    }),
                })
                    .then(async (response) => {
                        if (!response.ok) {
                            const errorText = await response.text();
                            statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                            return;
                        }
                        refreshAllCollections();
                    })
                    .catch((err) => {
                        statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                    });
            }, 2000); // wait 2 seconds after last input
        });
    });


    const deleteCollectionButtons = document.querySelectorAll(".collection-delete");

    deleteCollectionButtons.forEach(dCB => {
        dCB.addEventListener("click", function () {
            const dCBparent = dCB.parentElement.parentElement;

            const dCBcollection = dCBparent.dataset.collection;

            fetch("/proli/api/delete_collection", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    collection: dCBcollection
                }),
            })
                .then(async (response) => {
                    if (!response.ok) {
                        const errorText = await response.text();
                        statusMessage(`Error ${response.status}: ${errorText}`, "error", 4000);
                        return;
                    }
                    refreshAllCollections();
                })
                .catch((err) => {
                    statusMessage(`Fetch failed: ${err.message}`, "error", 4000);
                });
        });
    });

    statusMessage('Refreshed! <i class="fa-solid fa-repeat"></i>', "success", 2000);
};


document.addEventListener("DOMContentLoaded", () => {
    refreshAllCollections();
});
