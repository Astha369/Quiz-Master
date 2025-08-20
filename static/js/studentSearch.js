let debounceTimer;

function debounceSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(handleSearch, 300);
}

function handleSearch() {
    let query = document.getElementById("searchInput").value.trim().toLowerCase();
    let tableRows = document.querySelectorAll("tbody tr");
    let noDataMessage = document.getElementById("noDataMessage");

    let found = false;

    tableRows.forEach(row => {
        let chapterName = row.children[1].innerText.toLowerCase();
        if (chapterName.includes(query)) {
            row.style.display = "";
            found = true;
        } else {
            row.style.display = "none";
        }
    });

    if (!found) {
        if (!noDataMessage) {
            noDataMessage = document.createElement("tr");
            noDataMessage.id = "noDataMessage";
            noDataMessage.innerHTML = `<td colspan="6" style="text-align: center;">No Results Found</td>`;
            document.querySelector("tbody").appendChild(noDataMessage);
        }
    } else {
        if (noDataMessage) {
            noDataMessage.remove();
        }
    }
}

function displayResults(data) {
    let resultDiv = document.getElementById("searchResults");
    let searchResultsContainer = document.getElementById("searchResultsContainer");

    if (!resultDiv || !searchResultsContainer) {
        console.error("Error: searchResults element not found.");
        return;
    }

    resultDiv.innerHTML = "";

    if ((!data.subjects || data.subjects.length === 0) && (!data.quizzes || data.quizzes.length === 0)) {
        resultDiv.innerHTML = "<p>No results found</p>";
    } else {
        if (data.subjects && data.subjects.length) {
            resultDiv.innerHTML += "<h3>Subjects</h3>" + data.subjects.map(s => `<p>${s.name}</p>`).join('');
        }
        if (data.quizzes && data.quizzes.length) {
            resultDiv.innerHTML += "<h3>Quizzes</h3>" + data.quizzes.map(q => `<p>Quiz ID: ${q.id}, Date: ${q.date}</p>`).join('');
        }
    }

    searchResultsContainer.style.display = "block";
    searchResultsContainer.classList.remove("hidden");
}


function clearSearch() {
    document.getElementById("searchResultsContainer").classList.add("hidden");
    document.getElementById("searchResults").innerHTML = "";
    document.getElementById("searchInput").value = "";
    document.querySelector(".content-box").style.display = "block";
}