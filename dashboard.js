document.getElementById('forecast-btn').addEventListener('click', () => {
    const fileInput = document.getElementById('file-input');
    if (!fileInput.files.length) {
        alert("Please choose a CSV file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const uploadMessage = document.getElementById('uploadMessage');
    uploadMessage.textContent = "Forecasting in progress...";

    fetch('/', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            uploadMessage.textContent = "Error: " + data.error;
            return;
        }
        uploadMessage.textContent = "Forecast completed!";
        displayForecastTable(data.forecast);
        renderCharts(data.forecast);
    })
    .catch(err => {
        uploadMessage.textContent = "Error running forecast!";
        console.error(err);
    });
});

function displayForecastTable(forecast) {
    const table = document.getElementById('forecast-table');
    table.innerHTML = "<tr><th>Column</th><th>Forecast Values</th></tr>";
    for (let col in forecast) {
        const row = `<tr><td>${col}</td><td>${forecast[col].join(', ')}</td></tr>`;
        table.innerHTML += row;
    }
}

function renderCharts(forecast) {
    const chartsGrid = document.getElementById('charts-grid');
    chartsGrid.innerHTML = '';

    for (let col in forecast) {
        const canvas = document.createElement('canvas');
        canvas.style.background = "#fff";  // white background
        chartsGrid.appendChild(canvas);

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: forecast[col].map((_, i) => `T+${i+1}`),
                datasets: [{
                    label: col,
                    data: forecast[col],
                    borderColor: 'rgba(46,139,87,1)',
                    backgroundColor: 'rgba(46,139,87,0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    title: { display: true, text: 'Forecast: ' + col }
                },
                scales: { y: { beginAtZero: false } }
            }
        });
    }
}
