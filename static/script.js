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
    const device = document.getElementById("device");
    const warningModal = document.getElementById("warningModal");
    const warningText = document.getElementById("warningText");
    const confirmEditButton = document.getElementById("confirmEdit");
    const cancelEditButton = document.getElementById("cancelEdit");
    const sessionChart = document.querySelector(".chart-wrapper")
    const sessionCharts= document.getElementById("session-charts-container");
    const deviceCharts= document.querySelector(".deviceChart");
    const mechanismChart= document.querySelector(".mechChart");
    
    const mars = document.querySelector(".mars");
    const pluto = document.querySelector(".pluto")
    pluto.addEventListener("click",()=>{
        PatientDetailscontainer.style.display = "none";
        HospitalDetailsContainer.style.display = "none";
        sessionCharts.style.display = "none";
        deviceCharts.style.display = "none";
        mechanismChart.style.display = "none";
        containereditable.style.display = "none"
        console.log("pluto clicked");
        getUserID(pluto.getAttribute("device-name"));
        DeviceName = "PLUTO"
        pluto.style.backgroundColor = "#2f6690"
        mars.style.backgroundColor = "#3a7ca5"
        PatientDetailscontainer.style.backgroundColor = "#2f6690"
        HospitalDetailsContainer.style.backgroundColor = "#2f6690"
        containereditable.style.backgroundColor = "#2f6690"
    })
    
    mars.addEventListener("click",()=>{
        console.log("mars clicked");
        containereditable.style.display = "none"
        PatientDetailscontainer.style.display = "none";
        HospitalDetailsContainer.style.display = "none";
        sessionCharts.style.display = "none";
        deviceCharts.style.display = "none";
        mechanismChart.style.display = "none";
        getUserID(mars.getAttribute("device-name"));
         DeviceName = "MARS"
         pluto.style.backgroundColor = "#3a7ca5"
         mars.style.backgroundColor =  "#193d58"
         PatientDetailscontainer.style.backgroundColor = "#193d58"
         HospitalDetailsContainer.style.backgroundColor =  "#193d58"
         containereditable.style.backgroundColor = "#193d58"
    })
    function getUserID(search_term){
        console.log(search_term);
        let previouslySelectedItem = null;
        const suggestionsDiv = document.getElementById('suggestions');
         $.ajax({
             url: '/get_userId',
             type: 'POST',
             data: { search_term: search_term },
             
             success: function (response) {
                 const hospitalInfo = response.hospital_info;
                 suggestionsDiv.innerHTML = '';
                 hospitalInfo.forEach(hospital => {
                     const suggestionItem = document.createElement('div');
                     suggestionItem.classList.add('suggestion-item');
                     suggestionItem.innerHTML = `
                         ${hospital.HospitalID} - 
                         <span class="${hospital.Status.toLowerCase()}">${hospital.Status}</span>
                     `;
                     suggestionItem.addEventListener('click', function() {
                         // Change the color of the clicked item
                         if (previouslySelectedItem) {
                            previouslySelectedItem.style.backgroundColor = ''; // Reset the previous item's style
                        }
                        suggestionItem.style.backgroundColor = '#193d58'; // Highlight the selected item
                        suggestionItem.style.color = '#fff'; // Optional: Change text color for better visibility
    
                        previouslySelectedItem = suggestionItem; // Update the tracker
    
                        mechanismChart.style.display = "none";
                        sessionCharts.style.display = "none";
                        containereditable.style.display = "none"
                         fetchHospitalDetails(hospital.HospitalID);
                        //  devChart(hospital.HospitalID)
                        //  fetchUserData(hospital.HospitalID,search_term)
                         
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
                    console.log("working")
                    PatientDetailscontainer.style.display = "block";
                    loadingMessage.innerHTML = "";
                    // PatientDetailscontainer.innerHTML = "";
                    //changed
                    time = [

                    ]
                    const headerHTML = header.map((value, index) => {
                        let displayValue = lastRow[index];
                        if (value.toLowerCase() === "usehand") {
                            const numericValue = Number(lastRow[index]);
                            displayValue = numericValue === 1 ? "Right Hand" : numericValue === 2 ? "Left Hand" : displayValue;
                        }
                        const prescribedKeys = ["sabdu", "sfe", "elfe", "wfe", "wurd", "fps", "fme1", "fme2","hoc"];
                        if (prescribedKeys.includes(value.toLowerCase())) {
                            displayValue += `  [Prescribed(min)]`;
                        }
                        console.log(displayValue)
                        return `
                            <div class="form-row-detials">
                                <label class="form-label">${value.toUpperCase()}</label>
                                <label class="form-input">${displayValue}</label>
                            </div>
                        `;
                    }).join("");
                    
                    PatientDetailscontainer.innerHTML = `
                            <div class="form-layout">
                                <h2 class="form-heading">Patient Details</h2>
                                ${headerHTML}
                                <div class="form-actions">
                                     <button id="editconfig" class="btn btn-success">CHANGE DURATION</button>
                                </div>
                            </div>
                        `;
                    
                        function parseCustomDate(dateString) {
                            const [day, month, year] = dateString.split('-').map(Number); 
                            return new Date(year, month - 1, day); 
                        }
                    document.getElementById("editconfig").addEventListener("click", () => {
                        console.log("click")
                        const dateField = lastRow[header.indexOf("Date")]; 
                        const parsedDate = parseCustomDate(dateField);
                        const currentDate = new Date();
                        if (!isNaN(parsedDate)) {
                            console.log(parsedDate)
                            console.log(currentDate)
                            const diffInTime = currentDate - parsedDate; 
                            const diffInDays = diffInTime / (1000 * 60 * 60 * 24); 
                            console.log(diffInDays)
                            if (diffInDays < 28) {
                                warningText.innerText = `Configuration is up to date. Last updated at ${parsedDate}. Do you want to continue?`;
                                warningModal.style.display = "flex";
                            } else {
                                PatientDetailscontainer.style.display="none"
                                createEditableFields(lastRow,header)
                            }
                        } else {
                            console.error("Invalid date format in field:", dateField);
                        }
                        confirmEditButton.addEventListener("click", () => {
                            // Allow editing
                            PatientDetailscontainer.style.display="none"
                            createEditableFields(lastRow,header)
                            warningModal.style.display = "none";
                        });
                        cancelEditButton.addEventListener("click", () => {
                             // Disallow editing
                             PatientDetailscontainer.style.display="block"
                            warningModal.style.display = "none";
                        });
                       
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

}

    // Function to fetch and display hospital details
    function fetchHospitalDetails(hospitalID) {
        HospitalDetailsContainer.style.display = "block"
        device.innerText = DeviceName;
        fetch(`/get_hospital_details/${hospitalID}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
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
                 deviceCharts.style.display = "block"
                // Render pie chart
                destroyChart(); // Destroy any existing chart before rendering
                renderPieChart(data.usage_days, remainingDays);
                fetchUserData(hospitalID,DeviceName)
                devChart(hospitalID)
            })
            .catch(error => {
                console.error('Error fetching hospital details:', error);
            });
    }

    function createEditableFields(rowData, headers) {
        containereditable.style.display = "block";
        containereditable.innerHTML = "";

        const formatDate = (date) => {
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}-${month}-${year}`; 
        };
    
        const currentDate = formatDate(new Date());
        // End Date (28 days from today)
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 28);
        const formattedEndDate = formatDate(endDate);
        rowData[headers.indexOf("Date")] = currentDate;
        rowData[headers.indexOf("startdate")] = currentDate;
        rowData[headers.indexOf("end ")] = formattedEndDate;
        const nonEditableFields = headers.filter(
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
            ${nonEditableFields
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
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, "rgba(0, 0, 128, 0.2)");
            gradient.addColorStop(1, "rgba(0, 0, 128, 0.6)");
  
            // Update chart_data with the gradient
            chartData.datasets[0].backgroundColor = gradient;
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
                                title: { display: false, text: 'Date' },
                                
                            },
                            y: {
                                title: { display: true, text: 'Session Duration' },
                                min: -0.6,
                                max: 180,
                                grid: {
                                    display: false,
                                  },
                            },
                        },
                        plugins: {
                            title: {
                              display: true,
                              text: " Device used or not and its Usage Duration",
                              position: "top", // Add a title for the chart
                              font: {
                                size: 18,
                              },
                            },
                          
                            legend: {
                              display: false,
                            },
                            
                          },
                        onClick: function (event, activeElements) {
                            if (activeElements.length > 0) {
                                const activePoint = activeElements[0];
                                const index = activePoint.index; // Index of the clicked point in the dataset
                                   mechanismChart.style.display = "block";
                                    sessionCharts.style.display="flex"
                                if (index >= 0 && index < chartDataPoints.length) {
                                    const clickedData = chartDataPoints[index]; // Reference the chartDataPoints array
                                    console.log("Clicked Data Point:", clickedData);
    
                                    // Extract the date and session duration
                                    const clickedDate = clickedData.date;
                                    const sessionDuration = clickedData.sessionDuration;
                                    const dateParts = clickedDate.split('-'); // Assuming format is yyyy-mm-dd
                                    const formattedDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`;
                                    scrollToDetails();
                                    console.log("Formatted Clicked Date:", formattedDate); 
    
                                    // Fetch mechanism data or take other actions
                                    fetchMechanismData(hospitalID, formattedDate);
                                  
                                    
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
  
    const fixedColors = [
        "rgba(255, 99, 132, 0.7)",
        "rgba(255, 159, 64, 0.7)",
        "rgba(160, 32, 230, 0.7)",
        "rgba(75, 192, 192, 0.7)",
        "rgba(75, 112, 192, 0.7)",
        "rgba(175, 192, 192, 0.7)",
    ];
  
    // Custom plugin to draw vertical lines
    const verticalLinePlugin = {
        id: 'thresholdLines',
        afterDraw: (chart) => {
            const ctx = chart.ctx;
            const yScale = chart.scales.y;
            const xScale = chart.scales.x;
            const { lines } = data;
  
            // Draw a line for each threshold
            lines.forEach((threshold, index) => {
                const x = xScale.getPixelForValue(index); // Get X position of the bar
                const y = yScale.getPixelForValue(threshold); // Get Y position of the threshold
  
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(x, y); // Start at the threshold position
                ctx.lineTo(x, yScale.bottom); // Extend down to the bottom
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)'; // Black line
                ctx.lineWidth = 1.5;
                ctx.setLineDash([5, 5]); // Dashed line
                ctx.stroke();
                ctx.restore();
            });
        },
    };
  
    window.mechChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.mechanisms,
            datasets: [
                {
                    label: 'Game Duration',
                    data: data.durations,
                    backgroundColor: fixedColors,
                },
            ]
        },
        plugins: [ChartDataLabels, verticalLinePlugin],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 31,
                    title: {
                        display: true,
                        text: 'Duration (mins)'
                    },
                    grid: {
                        display: false,
                    }
                },
                x: {
                    grid: {
                        display: false,
                    }
                },
            },
            plugins: {
                title: {
                    display: true,
                    text: "Total Days Usage Duration",
                    position: "top",
                    font: {
                        size: 18,
                    },
                },
                datalabels: {
                    color: "black",
                    font: {
                        weight: "bold",
                        size: 10,
                    },
                    anchor: "middle",
                    align: "start",
                    borderRadius: 4,
                    borderWidth: 1,
                    borderColor: "rgb(75, 192, 192)",
                    backgroundColor: "rgb(91, 236, 241)",
                },
                legend: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            var label = context.dataset.label || "";
                            if (context.parsed.y !== null) {
                                label += ": " + context.parsed.y;
                            }
                            return label;
                        },
                    },
                },
            }
        }
    });
  }
  
  
  
  
    
    
    // Call the function to fetch hospital suggestions when the page loads
    window.onload = getUserID(DEVICE_NAME);
  });
  