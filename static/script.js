$(document).ready(function () {
  // Function to fetch all hospital IDs and their statuses
  function getSuggestions() {
      const suggestionsDiv = document.getElementById('suggestions');

      // Fetch hospital IDs and statuses from the backend
      fetch('/get_hosID')
          .then(response => response.json())
          .then(data => {
              const hospitalInfo = data.hospital_info;
              console.log("Hospital Info:", hospitalInfo);
              
              // Clear previous suggestions
              suggestionsDiv.innerHTML = '';

              // Show all hospital IDs and their statuses
              hospitalInfo.forEach(hospital => {
                  const suggestionItem = document.createElement('div');
                  suggestionItem.classList.add('suggestion-item');

                  // Add hospital ID and status
                  suggestionItem.innerHTML = `
                      ${hospital.HospitalID} - 
                      <span class="${hospital.Status.toLowerCase()}">${hospital.Status}</span>
                  `;

                  suggestionsDiv.appendChild(suggestionItem);
              });
          })
          .catch(error => {
              console.error('Error fetching hospital IDs:', error);
          });
  }

  // Call the function when the page has fully loaded
  window.onload = getSuggestions;
});
