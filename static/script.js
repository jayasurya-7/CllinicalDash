let usageChart;

$(document).ready(function () {
    function getSuggestions() {
        const suggestionsDiv = document.getElementById('suggestions');

        fetch('/get_hosID')
            .then(response => response.json())
            .then(data => {
                const hospitalInfo = data.hospital_info;
                console.log("Hospital Info:", hospitalInfo);

                suggestionsDiv.innerHTML = '';

                hospitalInfo.forEach(hospital => {
                    const suggestionItem = document.createElement('div');
                    suggestionItem.classList.add('suggestion-item');

                    suggestionItem.innerHTML = `
                        ${hospital.HospitalID} - 
                        <span class="${hospital.Status.toLowerCase()}">${hospital.Status}</span>
                    `;

                    suggestionItem.addEventListener('click', function() {
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
            usageChart.destroy(); //
            usageChart = null;    // Reset the chart variable
        }
    }

    function fetchHospitalDetails(hospitalID) {
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

                document.getElementById('detailsForm').style.display = 'block';

                const remainingDays = data.total_days - data.usage_days;

                destroyChart();
                renderPieChart(data.usage_days, remainingDays);
            })
            .catch(error => {
                console.error('Error fetching hospital details:', error);
            });
    }

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
                    position: "bottom",
                    size:0.2,
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

        usageChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: options
        });
    }

    window.onload = getSuggestions;
});
