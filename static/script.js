// $(document).ready(function () {
//   // Function to fetch all hospital IDs and their statuses
//   function getSuggestions() {
//       const suggestionsDiv = document.getElementById('suggestions');

//       // Fetch hospital IDs and statuses from the backend
//       fetch('/get_hosID')
//           .then(response => response.json())
//           .then(data => {
//               const hospitalInfo = data.hospital_info;
//               console.log("Hospital Info:", hospitalInfo);
              
//               // Clear previous suggestions
//               suggestionsDiv.innerHTML = '';

//               // Show all hospital IDs and their statuses
//               hospitalInfo.forEach(hospital => {
//                   const suggestionItem = document.createElement('div');
//                   suggestionItem.classList.add('suggestion-item');

//                   // Add hospital ID and status
//                   suggestionItem.innerHTML = `
//                       ${hospital.HospitalID} - 
//                       <span class="${hospital.Status.toLowerCase()}">${hospital.Status}</span>
//                   `;

//                   suggestionsDiv.appendChild(suggestionItem);
//               });
//           })
//           .catch(error => {
//               console.error('Error fetching hospital IDs:', error);
//           });
//   }

//   // Call the function when the page has fully loaded
//   window.onload = getSuggestions;
// });



// $(document).ready(function () {
//     // Function to fetch all hospital IDs and their statuses
//     function getSuggestions() {
//       const suggestionsDiv = document.getElementById('suggestions');
  
//       // Fetch hospital IDs and statuses from the backend
//       fetch('/get_hosID')
//         .then(response => response.json())
//         .then(data => {
//           const hospitalInfo = data.hospital_info;
//           console.log("Hospital Info:", hospitalInfo);
  
//           // Clear previous suggestions
//           suggestionsDiv.innerHTML = '';
  
//           // Show all hospital IDs and their statuses
//           hospitalInfo.forEach(hospital => {
//             const suggestionItem = document.createElement('div');
//             suggestionItem.classList.add('suggestion-item');
  
//             // Add hospital ID and status
//             suggestionItem.innerHTML = `
//               ${hospital.HospitalID} - 
//               <span class="${hospital.Status.toLowerCase()}">${hospital.Status}</span>
//             `;
  
//             // Add click event to fetch and display hospital details
//             suggestionItem.addEventListener('click', () => fetchHospitalDetails(hospital.HospitalID));
  
//             suggestionsDiv.appendChild(suggestionItem);
//           });
//         })
//         .catch(error => {
//           console.error('Error fetching hospital IDs:', error);
//         });
//     }
  
//     // Function to fetch and display hospital details
//     function fetchHospitalDetails(hospitalID) {
//       fetch(`/get_hospital_details/${hospitalID}`)
//         .then(response => response.json())
//         .then(data => {
//           if (data.error) {
//             alert(data.error);
//             return;
//           }
  
//           // Populate form fields with data
//           document.getElementById('hospitalID').value = hospitalID;
//           document.getElementById('startDate').value = data.start_date;
//           document.getElementById('endDate').value = data.end_date;
//           document.getElementById('totalDays').value = data.total_days;
//           document.getElementById('usageDays').value = data.usage_days;
//           document.getElementById('totalusageDays').value = data.total_usage_days;

  
//           // Show the details form
//           document.getElementById('detailsForm').style.display = 'block';
//            // Calculate remaining days
//            const remainingDays = data.total_days - data.usage_days;

//           renderPieChart(data.usage_days, remainingDays);
//         })
//         .catch(error => {
//           console.error('Error fetching hospital details:', error);
//         });
//     }
  

//     // Function to render pie chart
//     function renderPieChart(usedDays, remainingDays) {
//         const ctx = document.getElementById('usageChart').getContext('2d');

//         const data = {
//             labels: ['Used Days', 'Remaining Days'],
//             datasets: [{
//                 data: [usedDays, remainingDays],
//                 backgroundColor: ['#4caf50', '#f44336'],
//                 hoverBackgroundColor: ['#388e3c', '#d32f2f'],
//             }]
//         };

//         const options = {
//             responsive: true,
//             plugins: {
//                 legend: {
//                     position: 'top',
//                 },
//                 tooltip: {
//                     callbacks: {
//                         label: function (tooltipItem) {
//                             return tooltipItem.raw + ' days';
//                         }
//                     }
//                 }
//             }
//         };

//         new Chart(ctx, {
//             type: 'pie',
//             data: data,
//             options: options
//         });
//     }

//     // Example to trigger form and pie chart when a hospital ID is clicked
//     document.getElementById('suggestions').addEventListener('click', function (event) {
//         const hospitalId = event.target.textContent.split(' - ')[0]; // Get the hospital ID from the clicked item
//         if (hospitalId) {
//             fetchHospitalDetails(hospitalId);
//         }
//     });


//     // Call the function when the page has fully loaded
//     window.onload = getSuggestions;
//   });
  
let usageChart;
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

                    // Add click event to fetch and display hospital details
                    suggestionItem.addEventListener('click', function() {
                        // $('#detailsForm').empty();
                        fetchHospitalDetails(hospital.HospitalID);
                       
                    });

                    suggestionsDiv.appendChild(suggestionItem);
                });
            })
            .catch(error => {
                console.error('Error fetching hospital IDs:', error);
            });
    }
    function destroyChart() {
    if (usageChart) {
        usageChart.destroy(); // Destroy the existing chart
        usageChart = null;    // Reset the chart variable
    }
}
    // Function to fetch and display hospital details
    function fetchHospitalDetails(hospitalID) {
        
        fetch(`/get_hospital_details/${hospitalID}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Populate form fields with data
                document.getElementById('hospitalID').value = hospitalID;
                document.getElementById('startDate').value = data.start_date;
                document.getElementById('endDate').value = data.end_date;
                document.getElementById('totalDays').value = data.total_days;
                document.getElementById('usageDays').value = data.usage_days;
                document.getElementById('totalusageDays').value = data.total_usage_days;

                // Show the details form
                document.getElementById('detailsForm').style.display = 'block';
                destroyChart(); 
                // Calculate remaining days
                const remainingDays = data.total_days - data.usage_days;
                // Render pie chart
                renderPieChart(data.usage_days, remainingDays);
            })
            .catch(error => {
                console.error('Error fetching hospital details:', error);
            });
    }

    // Function to render pie chart
    function renderPieChart(usedDays, remainingDays) {
        const ctx = document.getElementById('usageChart').getContext('2d');

        const data = {
            labels: ['Used Days', 'Remaining Days'],
            datasets: [{
                data: [usedDays, remainingDays],
                backgroundColor: ['#4caf50', '#f44336'],
                hoverBackgroundColor: ['#388e3c', '#d32f2f'],
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio:false,
            plugins: {
                legend: {
                    display:false,
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            return tooltipItem.raw + ' days';
                        }
                    }
                }
            }
        };

        new Chart(ctx, {
            type: 'pie',
            data: data,
            options: options
        });
    }

    // Call the function to fetch hospital suggestions when the page loads
    window.onload = getSuggestions;
});
