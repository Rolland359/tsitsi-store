document.addEventListener('DOMContentLoaded', function() {
    const chartContainer = document.getElementById('chartData');
    if (!chartContainer) return;

    // Récupération des données depuis le DOM
    const salesLabels = JSON.parse(chartContainer.dataset.salesLabels);
    const salesData = JSON.parse(chartContainer.dataset.salesData);
    const ordersData = JSON.parse(chartContainer.dataset.ordersData);
    const topLabels = JSON.parse(chartContainer.dataset.topLabels);
    const topQuantities = JSON.parse(chartContainer.dataset.topData);

    // Graphique Tendances
    new Chart(document.getElementById('salesChart'), {
        type: 'line',
        data: {
            labels: salesLabels,
            datasets: [
                { label: 'Ventes (Ar)', data: salesData, borderColor: '#198754', tension: 0.3, yAxisID: 'y' },
                { label: 'Commandes', data: ordersData, borderColor: '#0dcaf0', tension: 0.3, yAxisID: 'y1' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { type: 'linear', position: 'left' },
                y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });

    // Graphique Top Produits
    new Chart(document.getElementById('topProductsChart'), {
        type: 'bar',
        data: {
            labels: topLabels,
            datasets: [{
                data: topQuantities,
                backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
});