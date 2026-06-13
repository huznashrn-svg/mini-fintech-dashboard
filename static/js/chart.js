const ctx = document.getElementById('expenseChart');

if (ctx && chartLabels.length > 0) {

    const chartColors = [
        '#DC2626', // Red
        '#3B82F6', // Blue
        '#10B981', // Green
        '#F59E0B', // Amber
        '#8B5CF6', // Purple
        '#EC4899', // Pink
        '#14B8A6', // Teal
        '#F97316', // Orange
        '#6366F1', // Indigo
        '#84CC16', // Lime
        '#06B6D4', // Cyan
        '#A855F7'  // Violet
    ];

    new Chart(ctx, {
        type: 'pie',

        data: {
            labels: chartLabels,

            datasets: [{
                data: chartValues,

                backgroundColor: chartLabels.map(
                    (_, index) =>
                        chartColors[index % chartColors.length]
                ),

                borderColor: '#FFFFFF',
                borderWidth: 3,

                hoverOffset: 15
            }]
        },

        options: {
            responsive: true,

            plugins: {

                legend: {
                    position: 'bottom',

                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 13
                        }
                    }
                },

                tooltip: {
                    callbacks: {

                        label: function(context) {

                            const total =
                                context.dataset.data.reduce(
                                    (a, b) => a + b,
                                    0
                                );

                            const value = context.raw;

                            const percentage =
                                ((value / total) * 100).toFixed(1);

                            return `${context.label}: ₹${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}