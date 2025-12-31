document.addEventListener('DOMContentLoaded', function() {
    // Récupération de l'objet global défini dans le template
    const data = window.dashboardData;

    // Sécurité : on vérifie que les données et les éléments existent
    if (!data) {
        console.error("Données de dashboard manquantes dans window.dashboardData");
        return;
    }

    const salesCtx = document.getElementById('salesChart');
    const topCtx = document.getElementById('topProductsChart');

    // 1. Graphique Ventes & Commandes (Line Chart)
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: data.salesLabels,
                datasets: [
                    {
                        label: 'Ventes (Ar)',
                        data: data.salesData,
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        fill: true,
                        yAxisID: 'y',
                        tension: 0.3 // Pour des courbes plus fluides
                    },
                    {
                        label: 'Commandes',
                        data: data.ordersData,
                        borderColor: '#0dcaf9',
                        backgroundColor: 'transparent',
                        yAxisID: 'y1',
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Montant (Ar)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false, // Évite de superposer les grilles
                        },
                        title: {
                            display: true,
                            text: 'Volume (Commandes)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }

    // 2. Graphique Top 5 Produits (Bar Chart)
    if (topCtx) {
        new Chart(topCtx, {
            type: 'bar',
            data: {
                labels: data.topLabels,
                datasets: [{
                    label: 'Unités vendues',
                    data: data.topData,
                    backgroundColor: '#0d6efd',
                    borderRadius: 5
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            // C'est ici qu'on gère la coupure des titres trop longs
                            callback: function(value) {
                                const label = this.getLabelForValue(value);
                                if (label.length > 20) {
                                    return label.substring(0, 20) + '...'; // Coupe à 20 car après c'est trop large
                                }
                                return label;
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false,
                        // Pour que l'utilisateur puisse quand même lire le titre complet au survol
                        callbacks: {
                            title: function(tooltipItems) {
                                return tooltipItems[0].label;
                            }
                        }
                    }
                }
            }
        });
    }
});