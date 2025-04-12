document.addEventListener("DOMContentLoaded", function () {
  // Get DOM elements
  const searchInput = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");
  const loadingElement = document.getElementById("loading");
  const resultsContainer = document.getElementById("results-container");

  // Your backend API URL (change the port if yours is different)
  const API_URL = "http://localhost:8000";

  // Add event listener to search button
  searchButton.addEventListener("click", function () {
    performSearch();
  });

  // Add event listener for Enter key in search input
  searchInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      performSearch();
    }
  });

  // Function to perform the search
  function performSearch() {
    const query = searchInput.value.trim();

    if (!query) {
      // No search term entered
      resultsContainer.innerHTML =
        '<div class="error-message">Please enter a politician name to search.</div>';
      return;
    }

    // Show loading indicator
    loadingElement.classList.remove("hidden");
    resultsContainer.innerHTML = "";

    // Make API request
    fetch(`${API_URL}/query=${encodeURIComponent(query)}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        // Hide loading indicator
        loadingElement.classList.add("hidden");

        // Display results
        displayResults(data);
      })
      .catch((error) => {
        // Hide loading indicator
        loadingElement.classList.add("hidden");

        // Show error message
        resultsContainer.innerHTML = `
                    <div class="error-message">
                        Error fetching results: ${error.message}
                    </div>
                `;
        console.error("Search error:", error);
      });
  }

  // Function to display search results
  function displayResults(data) {
    // Clear previous results
    resultsContainer.innerHTML = "";

    // Display message
    const messageElement = document.createElement("h2");
    messageElement.textContent = data.message;
    resultsContainer.appendChild(messageElement);

    if (data.count === 0) {
      return; // No results to display
    }

    // Create and append result cards
    data.results.forEach((politician) => {
      const card = document.createElement("div");
      card.className = "politician-card";

      // Get name data
      const firstName = politician.name?.first || "";
      const lastName = politician.name?.last || "";

      // Create card content
      card.innerHTML = `
                <h2>${firstName} ${lastName}</h2>
                <p class="politician-info">Source: ${politician.data_source}</p>
                ${
                  politician.terms
                    ? `<p class="politician-info">Latest position: ${
                        politician.terms[politician.terms.length - 1]?.type ||
                        "N/A"
                      } 
                    (${
                      politician.terms[politician.terms.length - 1]?.state ||
                      "N/A"
                    })</p>`
                    : ""
                }
            `;

      resultsContainer.appendChild(card);
    });
  }
});
