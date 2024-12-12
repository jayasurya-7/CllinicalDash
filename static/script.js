let usageChart; // Declare the chart globally
let devChart;
DEVICE_NAME = "PLUTO"
$(document).ready(function () {
    
    var UserName;
    var DeviceName = "PLUTO";
    const PatientDetailscontainer = document.getElementById("homerUserDetails");// userdetials
    const containereditable = document.getElementById("editableFieldsContainer");
    const loadingMessage = document.getElementById("loadingMessage");
    const HospitalDetailsContainer = document.getElementById("detailsForm");
    const pluto = document.querySelector(".pluto")
    pluto.addEventListener("click",()=>{
        PatientDetailscontainer.style.display = "none";
        HospitalDetailsContainer.style.display = "none"
        console.log("pluto clicked");
        getUserID(pluto.getAttribute("device-name"));
        
    })
    const mars = document.querySelector(".mars");
    mars.addEventListener("click",()=>{
        console.log("mars clicked");
        PatientDetailscontainer.style.display = "none";
        HospitalDetailsContainer.style.display = "none"
        getUserID(mars.getAttribute("device-name"));
        
    })
    function getUserID(search_term){
        console.log(search_term);
        const suggestionsDiv = document.getElementById('suggestions');
         $.ajax({
             url: '/get_userId',
             type: 'POST',
             data: { search_term: search_term },
             
             success: function (response) {
                 const hospitalInfo = response.hospital_info;
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
                         fetchHospitalDetails(hospital.HospitalID);
                         devChart(hospital.HospitalID);
                         fetchUserData(hospital.HospitalID,search_term)
                     });
 
                     suggestionsDiv.appendChild(suggestionItem);
                 })
             },
             error: function (error) {
                 console.error('Error:', error);
             }
         });
     }
    
    function fetchUserData(name, d_name) {
        UserName = name;
        DeviceName = d_name;
        $.ajax({
            url: '/get_user_data',
            type: 'POST',
            data: {
                Name: name,
                devicename: d_name
            },
            success: function (response) {
                if (response.status === "success") {
                    const header = response.data.header;
                    const lastRow = response.data.last_row;
                    PatientDetailscontainer.style.display = "block";
                    loadingMessage.innerHTML = "";
                    // PatientDetailscontainer.innerHTML = "";

                    const headerHTML = header.map((value, index) => `
                            <div class="form-row-detials">
                                <label class="form-label">${value.toUpperCase()}</label>
                                <label class="form-input">${lastRow[index]}</label>
                            </div>
                        `).join("");

                    PatientDetailscontainer.innerHTML = `
                            <div class="form-layout">
                                <h2 class="form-heading">Patient Details</h2>
                                ${headerHTML}
                                <div class="form-actions">
                                     <button id="editconfig" class="btn btn-success">Edit Configuation</button>
                                </div>
                            </div>
                        `;
                    document.getElementById("editconfig").addEventListener("click", () => {
                        createEditableFields(lastRow, header)
                        PatientDetailscontainer.style.display = "none";
                    });

                } else {
                    alert("Error: " + response.message);
                }

            },
            error: function (xhr, status, error) {
                console.error("Error fetching user data:", error);
                alert("Failed to fetch user data. Please try again later.");
            }
        });
    }
    // Function to destroy the chart if it exists
    function destroyChart() {
        if (usageChart) {
            usageChart.destroy(); // Destroy the existing chart
            window.devChart.destroy();
            usageChart = null; 
            window.devChart=null;
               // Reset the chart variable
        }
        // if(devChart){
        //     devChart.destroy();
        //     devChart=null;
        // }
    }

    // Function to fetch and display hospital details
    function fetchHospitalDetails(hospitalID) {
        HospitalDetailsContainer.style.display = "block"
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

                // Calculate remaining days
                const remainingDays = data.total_days - data.usage_days;

                // Render pie chart
                destroyChart(); // Destroy any existing chart before rendering
                renderPieChart(data.usage_days, remainingDays);
                fetchUserData(hospitalID,DeviceName)
            })
            .catch(error => {
                console.error('Error fetching hospital details:', error);
            });
    }
    function createEditableFields(rowData, headers) {
        containereditable.style.display = "block";
        containereditable.innerHTML = "";

        const formatDate = (date) => {
            const day = String(date.getDate()).padStart(2, '0'); // Ensure two digits
            const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
            const year = date.getFullYear();
            return `${day}-${month}-${year}`; // Return in DD-MM-YYYY format
        };
        
        // Current Date
        const currentDate = formatDate(new Date());
        
        // End Date (28 days from today)
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 28);
        const formattedEndDate = formatDate(endDate);
        
        console.log(currentDate);       // Example Output: 10-12-2024
        console.log(formattedEndDate);  // Example Output: 07-01-2025
        
        rowData[headers.indexOf("Date")] = currentDate;
        rowData[headers.indexOf("startdate")] = currentDate;
        rowData[headers.indexOf("end ")] = formattedEndDate;
        const editableFields = headers.filter(
            (header) =>
                ![
                    "name",
                    "date",
                    "startdate",
                    "end ",
                    "age",
                    "hospno",
                    "usehand",
                    "upperarmlength",
                    "forearmlength",
                ].includes(header.toLowerCase())
        );
        containereditable.innerHTML = `
          <div class="form-layout">
            <h3 class="form-heading">Therapy Duration(min)</h3>
            ${editableFields
                .map((header, index) => {
                    const value = rowData[headers.indexOf(header)] || ""; // Get value based on original index
                    return `
                  <div class="form-row-detials">
                    <label class="editable-label">${header}</label>
                    <input type="text" class="editable-input" value="${value}" />
                  </div>
                `;
                })
                .join("")}
            <div class="form-actions">
              <button id="saveChangesButton" class="btn btn-success">Save Changes</button>
              <button id="cancelButton" class="btn btn-danger">Cancel</button>
            </div>
          </div>
        `;
        document.getElementById("cancelButton").addEventListener("click", () => {
            containereditable.style.display = "none";
            PatientDetailscontainer.style.display = "block";
        });
        document.getElementById("saveChangesButton").addEventListener("click", () => {
            const formInputs = document.querySelectorAll(".editable-input");
            const editableheaders = document.querySelectorAll(".editable-label")
            const headerTexts = Array.from(editableheaders).map(label => label.textContent);
            let isValid = true;
            const updatedData = { ...rowData };
            formInputs.forEach((input, index) => {
                if (input.value.trim() === "") {
                    isValid = false;
                    input.style.border = "2px solid red";
                    let errorMessage = input.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains("error-message")) {
                        errorMessage = document.createElement("span");
                        errorMessage.classList.add("error-message");
                        errorMessage.textContent = "This field is required";
                        input.parentElement.appendChild(errorMessage);
                    }
                } else {
                    input.style.border = "";
                    const header = headerTexts[index];
                    console.log(index);
                    console.log(headerTexts);

                    updatedData[headers.indexOf(header)] = input.value; // Update only editable fields
                    let errorMessage = input.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains("error-message")) {
                        errorMessage.remove();
                    }
                }
            });

            if (isValid) {
                console.log("Updated Data:", updatedData); // Updated data including non-editable fields
                updateDataInAWS(updatedData); // Pass updated data to AWS function
                containereditable.style.display = "none";
                PatientDetailscontainer.style.display = "block";
            } else {
                alert("Please fill in all required fields.");
            }
        });
    }

    function updateDataInAWS(updatedRowData) {
        showUploadStatus("uploading...", "warning");
        $.ajax({
            url: '/update_data_in_aws',
            type: 'POST',
            data: {
                updatedData: Object.values(updatedRowData), // Send the updated row data
                userName: UserName,
                deviceName: DeviceName
            },
            success: function (response) {
                if (response.status === "success") {
                    showUploadStatus("Changes saved successfully!", "success");

                    fetchUserData(UserName, DeviceName);
                } else {

                    showUploadStatus("Failed to upload data to AWS.", "error");

                }
            },
            error: function (xhr, status, error) {
                console.error("Error updating data in AWS:", error);
                showUploadStatus("Error during the upload. Please try again later.", "error");
            }
        });
    }

    function showUploadStatus(message, type) {
        loadingMessage.innerHTML = "<div id='statusmessage'></div>";
        const statusContainer = document.getElementById("statusmessage");

        if (statusContainer) {
            statusContainer.textContent = message;
            statusContainer.style.color = "white"
            statusContainer.style.backgroundColor = type === "success" ? "green" : "red";
            if (type === "success" || type === "error") {
                setTimeout(() => {
                    loadingMessage.innerHTML = '';
                }, 3000);
            }

        }
    }
    // Function to render the pie chart
    function renderPieChart(usedDays, remainingDays) {
        const ctx = document.getElementById('usageChart').getContext('2d');

        const data = {
            labels: ['Used Days', 'Remaining Days'],
            datasets: [{
                data: [usedDays, remainingDays],
                backgroundColor: ['#81c3d7', '#3a7ca5'],
                hoverBackgroundColor: ['#118ab2', '#16425b'],
            }]
        };

        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position:"bottom",
                    labels:{
                        color:"white"
                    }
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

        // Create a new chart instance and assign it to the global variable
        usageChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: options
        });
    }
    // function devChart(hospitalID){
    //     fetch(`/chart-data/${hospitalID}`)
    //         .then(response => response.json())
    //         .then(chartData => {
    //             const ctx = document.getElementById('devChart').getContext('2d');
    //             console.log(chartData)
    //             window.devChart = new Chart(ctx, {
    //                 type: 'scatter', // Base type, combines bubble and line
    //                 data: chartData,
    //                 options: {
    //                     responsive: true,
    //                     maintainAspectRatio:false,
    //                     scales: {
    //                         x: {
    //                             type: 'time',
    //                             time: {
    //                                 unit: 'day', // Set X-axis to display days
    //                                 displayFormats: {
    //                                     day: 'dd-MM-yyyy', // Format the date as dd-mm-yyyy on X-axis
    //                                 }
    //                             },
    //                             title: {
    //                                 display: true,
    //                                 text: 'Date',
    //                             },
    //                         },
    //                         y: {
    //                             title: {
    //                                 display: true,
    //                                 text: 'Session Duration',
    //                             },
    //                             min: -0.6,
    //                             max:180,
    //                             display: false,
    //                             grid: {
    //                               display: false,
    //                             },
    //                         },
    //                     },
    //                     tooltips: {
    //                         callbacks: {
    //                             // Custom tooltip label to format date and session duration
    //                             label: function(tooltipItem) {
    //                                 // Format the X value (date) in dd-MM-yyyy format
    //                                 const date = new Date(tooltipItem.xLabel);
    //                                 const formattedDate = `${('0' + date.getDate()).slice(-2)}-${('0' + (date.getMonth() + 1)).slice(-2)}-${date.getFullYear()}`;
                                    
    //                                 // Get the session duration (y value)
    //                                 const sessionDuration = tooltipItem.yLabel;
    
    //                                 // Return the custom tooltip content
    //                                 return `Date: ${formattedDate}, Duration: ${sessionDuration} min`;
    //                             }
    //                         }
    //                     }
    //                 },
    //             });
    //         })
    //         .catch(error => console.error('Error fetching chart data:', error));
    // }
 
    // function devChart(hospitalID) {
    //     fetch(`/chart-data/${hospitalID}`)
    //         .then(response => response.json())
    //         .then(chartData => {
    //             console.log("Fetched Chart Data:", chartData); // Debug fetched data
    
    //             // Populate chartDataPoints array
    //             chartDataPoints = chartData.datasets[1].data.map(point => ({
    //                 date: point.x,
    //                 sessionDuration: point.y,
    //             }));
    //             console.log("Chart Data Points Array:", chartDataPoints); // Debug array content
    
    //             const ctx = document.getElementById('devChart').getContext('2d');
    //             window.devChart = new Chart(ctx, {
    //                 type: 'scatter',
    //                 data: {
    //                     labels: chartData.labels,
    //                     datasets: chartData.datasets,
    //                 },
    //                 options: {
    //                     responsive: true,
    //                     maintainAspectRatio: false,
    //                     scales: {
    //                         x: {
    //                             type: 'category',
    //                             title: { display: true, text: 'Date' },
    //                         },
    //                         y: {
    //                             title: { display: true, text: 'Session Duration' },
    //                             min: -0.6,
    //                             max: 180,
    //                         },
    //                     },
    //                     onClick: function (event, activeElements) {
    //                         if (activeElements.length > 0) {
    //                             const activePoint = activeElements[0];
    //                             const index = activePoint.index; // Index of the clicked point in the dataset
                        
    //                             if (index >= 0 && index < chartDataPoints.length) {
    //                                 const clickedData = chartDataPoints[index]; // Reference the chartDataPoints array
    //                                 console.log("Clicked Data Point:", clickedData);
                        
    //                                 // Extract the date and session duration
    //                                 const clickedDate = clickedData.date;
    //                                 const sessionDuration = clickedData.sessionDuration;
                        
    //                                 // Fetch mechanism data or take other actions
    //                                 fetchMechanismData(hospitalID, clickedDate);
                        
    //                                 // Optional: Smooth scroll to details section
    //                                 scrollToDetails();
    //                             } else {
    //                                 console.error("Index out of bounds or invalid:", index);
    //                             }
    //                         } else {
    //                             console.error("No active element clicked.");
    //                         }
    //                     }
                        
    //                 },
    //             });
    //         })
    //         .catch(error => console.error('Error fetching chart data:', error));
    // }
    
    // Helper function to fetch mechanism data for a specific date
    


    let chartDataPoints = []; // Array to store date and session duration points

    function devChart(hospitalID) {
        fetch(`/chart-data/${hospitalID}`)
            .then(response => response.json())
            .then(chartData => {
                console.log("Fetched Chart Data:", chartData); // Debug fetched data
    
                // Populate chartDataPoints array
                chartDataPoints = chartData.datasets[1].data.map(point => ({
                    date: point.x,
                    sessionDuration: point.y,
                }));
                console.log("Chart Data Points Array:", chartDataPoints); // Debug array content
    
                // Modify the dataset to include all points, but set pointRadius to 0 for sessionDuration 0
                const updatedDatasets = chartData.datasets.map(dataset => {
                    if (dataset.label === "Session Bubble") {
                        return {
                            ...dataset,
                            data: dataset.data.map(point => ({
                                ...point,
                                // Set point radius to 0 if sessionDuration is 0
                                r: point.y > 0 ? 10 : 0,
                            })),
                        };
                    }
                    return dataset;
                });
    
                const ctx = document.getElementById('devChart').getContext('2d');
                window.devChart = new Chart(ctx, {
                    type: 'scatter',
                    data: {
                        labels: chartData.labels,
                        datasets: updatedDatasets, // Use the modified dataset
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                type: 'category',
                                title: { display: true, text: 'Date' },
                            },
                            y: {
                                title: { display: true, text: 'Session Duration' },
                                min: -0.6,
                                max: 180,
                            },
                        },
                        onClick: function (event, activeElements) {
                            if (activeElements.length > 0) {
                                const activePoint = activeElements[0];
                                const index = activePoint.index; // Index of the clicked point in the dataset
    
                                if (index >= 0 && index < chartDataPoints.length) {
                                    const clickedData = chartDataPoints[index]; // Reference the chartDataPoints array
                                    console.log("Clicked Data Point:", clickedData);
    
                                    // Extract the date and session duration
                                    const clickedDate = clickedData.date;
                                    const sessionDuration = clickedData.sessionDuration;
                                    const dateParts = clickedDate.split('-'); // Assuming format is yyyy-mm-dd
                                    const formattedDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`;
    
                                    console.log("Formatted Clicked Date:", formattedDate); // Output the formatted date
    
                                    // Fetch mechanism data or take other actions
                                    fetchMechanismData(hospitalID, formattedDate);
                                    fetchSessionData(hospitalID, formattedDate);
                                    // Optional: Smooth scroll to details section
                                    scrollToDetails();
                                } else {
                                    console.error("Index out of bounds or invalid:", index);
                                }
                            } else {
                                console.error("No active element clicked.");
                            }
                        }
                    },
                });
            })
            .catch(error => console.error('Error fetching chart data:', error));
    }
    
    

    
    // Optional: Helper function to scroll to the details section
    function scrollToDetails() {
        const target = document.getElementById('detailsSection');
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    
 
    


    
    
    function fetchMechanismData(hospitalID, selectedDate) {
        fetch(`/fetch-mechanism-data/${hospitalID}/${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    console.log(data);
                    displayBarChart(data);
                }
            })
            .catch(error => console.error('Error fetching mechanism data:', error));
    }
    
    function displayBarChart(data) {
        const ctx = document.getElementById('mechChartID').getContext('2d');
        if (window.mechChart) {
            window.mechChart.destroy();
        }
        window.mechChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.mechanisms,
                datasets: [{
                    label: 'Game Duration',
                    data: data.durations,
                    backgroundColor: 'rgba(0, 123, 255, 0.6)',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Duration (mins)'
                        }
                    }
                }
            }
        });
    }
    
    function fetchSessionData(hospitalID, selectedDate) {
        fetch(`/fetch-session-data/${hospitalID}/${selectedDate}`)
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
    
                console.log("Fetched Session Data:", data);
    
                // Ensure we have sessions data
                if (!data.sessions || data.sessions.length === 0) {
                    console.error("No sessions found for the selected date.");
                    return;
                }
    
                // Clear previous charts
                const sessionChartsContainer = document.getElementById("session-charts-container");
                sessionChartsContainer.innerHTML = "";
    
                // Iterate through sessions and generate charts
                data.sessions.forEach((session) => {
                    if (!session.Mechanisms || !session.GameDurations) {
                        console.error("Invalid session data:", session);
                        return;
                    }
    
                    createPieChart(session.SessionNumber, session.Mechanisms, session.GameDurations);
                });
            })
            .catch((error) => {
                console.error('Error fetching session data:', error);
            });
    }
    
    function createPieChart(sessionNumber, mechanisms, durations) {
        const sessionChartsContainer = document.getElementById("session-charts-container");
    
        // Create a wrapper for each chart
        const chartWrapper = document.createElement('div');
        chartWrapper.classList.add('chart-wrapper'); // Optional: Add CSS for layout
        chartWrapper.style.margin = "20px"; // Adjusted spacing between charts
    
        // Add a title for the session chart
        const chartTitle = document.createElement('h3');
        chartTitle.textContent = `Session ${sessionNumber} - Mechanism Durations`;
        chartWrapper.appendChild(chartTitle);
    
        // Create canvas for the chart
        const canvas = document.createElement('canvas');
        chartWrapper.appendChild(canvas);
    
        // Append wrapper to the main container
        sessionChartsContainer.appendChild(chartWrapper);
    
        // Generate the chart
        new Chart(canvas, {
            type: 'pie',
            data: {
                labels: mechanisms,
                datasets: [{
                    data: durations,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 205, 86, 0.7)'
                    ],
                    borderWidth: 1,
                }],
            },
            options: {
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (tooltipItem) {
                                return `${tooltipItem.label}: ${tooltipItem.raw} mins`;
                            },
                        },
                    },
                    title: {
                        display: true,
                        text: `Mechanisms for Session ${sessionNumber}`,
                    },
                },
                responsive: true,
                maintainAspectRatio: true,
            },
        });
    }
    
    
    

   

    // Call the function to fetch hospital suggestions when the page loads
    window.onload = getUserID(DEVICE_NAME);
});