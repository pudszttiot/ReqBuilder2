// JavaScript for Search Bar Functionality

// Array of searchable content (for demonstration)
const contentItems = [
    { title: "Introduction", url: "index.html" },
    { title: "Installation", url: "installation.html" },
    { title: "Usage", url: "usage.html" },
    { title: "Screenshots", url: "screenshots.html" },
    { title: "GitHub Repo", url: "https://github.com/pudszttiot" },
];

// Function to handle search input changes
function handleSearchInput() {
    const searchQuery = document.getElementById("search-input").value.toLowerCase();
    if (searchQuery) {
        showSpinner();
        updateProgressBar(50); // Simulate progress

        setTimeout(() => { // Simulate search delay
            const results = contentItems.filter(item =>
                item.title.toLowerCase().includes(searchQuery)
            );
            displaySearchResults(results);
            hideSpinner();
            updateProgressBar(100); // Complete progress
        }, 500); // Adjust delay as needed
    } else {
        clearSearchResults();
        updateProgressBar(0);
    }
}

// Function to display search results dynamically
function displaySearchResults(results) {
    let resultsContainer = document.getElementById("search-results");
    if (!resultsContainer) {
        resultsContainer = document.createElement("div");
        resultsContainer.id = "search-results";
        document.querySelector(".search-bar").appendChild(resultsContainer);
    }
    resultsContainer.innerHTML = results.length > 0
        ? results.map(result => `
            <div class="search-result">
                <a href="${result.url}" target="_blank">${result.title}</a>
            </div>
          `).join("")
        : "<div class='search-result'>No results found.</div>";
}

// Function to clear search results
function clearSearchResults() {
    const resultsContainer = document.getElementById("search-results");
    if (resultsContainer) resultsContainer.innerHTML = "";
}

// Function to perform search on button click
function performSearch() {
    handleSearchInput();
}

// Spinner control functions
function showSpinner() {
    document.querySelector(".spinner").style.display = "block";
}

function hideSpinner() {
    document.querySelector(".spinner").style.display = "none";
}

// Progress bar control function
function updateProgressBar(value) {
    const progressBar = document.querySelector(".progress-bar div");
    progressBar.style.width = `${value}%`;
    document.querySelector(".progress-bar").setAttribute("aria-valuenow", value);
}
