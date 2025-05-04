/**
 * Opt-AI - Dashboard JavaScript
 * Handle dashboard functionality and visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize dashboard components
  initializeAnalysisHistory();
  initializeScoreChart();
  
  // Set up refresh button
  const refreshButton = document.getElementById('refresh-data');
  if (refreshButton) {
    refreshButton.addEventListener('click', () => {
      refreshAnalysisData();
    });
  }
});

/**
 * Initialize the analysis history table
 */
function initializeAnalysisHistory() {
  const tableBody = document.querySelector('#analysis-history tbody');
  if (!tableBody) return;
  
  // Show loading indicator
  tableBody.innerHTML = `
    <tr>
      <td colspan="5" class="text-center">
        <div class="spinner-border spinner-border-sm text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <span class="ms-2">Loading analysis history...</span>
      </td>
    </tr>
  `;
  
  // Fetch analysis history
  fetch('/api/analyses')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load analysis history');
      }
      return response.json();
    })
    .then(data => {
      if (data.length === 0) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="5" class="text-center">
              <p class="my-3">No analyses found. Start by analyzing a URL!</p>
              <a href="/analyze" class="btn btn-primary">Analyze New URL</a>
            </td>
          </tr>
        `;
        return;
      }
      
      // Populate table
      tableBody.innerHTML = '';
      data.forEach(analysis => {
        const row = document.createElement('tr');
        
        // Determine status class based on score
        let statusClass = 'bg-danger';
        let statusText = 'Poor';
        if (analysis.overall_score >= 80) {
          statusClass = 'bg-success';
          statusText = 'Good';
        } else if (analysis.overall_score >= 60) {
          statusClass = 'bg-warning';
          statusText = 'Fair';
        }
        
        // Create row content
        row.innerHTML = `
          <td>
            <a href="/report/${analysis.id}" class="text-truncate d-inline-block" style="max-width: 200px;" title="${analysis.url}">
              ${analysis.url}
            </a>
          </td>
          <td>${analysis.type}</td>
          <td>${analysis.date}</td>
          <td>
            <div class="progress" style="height: 20px;">
              <div class="progress-bar ${statusClass}" role="progressbar" style="width: ${analysis.overall_score}%;" 
                   aria-valuenow="${analysis.overall_score}" aria-valuemin="0" aria-valuemax="100">
                ${analysis.overall_score}%
              </div>
            </div>
          </td>
          <td>
            <a href="/report/${analysis.id}" class="btn btn-sm btn-primary">View</a>
          </td>
        `;
        
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="text-center text-danger">
            <p>Error loading analysis history: ${error.message}</p>
            <button class="btn btn-outline-primary btn-sm" onclick="initializeAnalysisHistory()">
              Try Again
            </button>
          </td>
        </tr>
      `;
    });
}

/**
 * Initialize the score chart
 */
function initializeScoreChart() {
  const chartCanvas = document.getElementById('score-chart');
  if (!chartCanvas) return;
  
  // Fetch data for chart
  fetch('/api/analyses')
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load analysis data');
      }
      return response.json();
    })
    .then(data => {
      if (data.length === 0) {
        // No data to display
        const ctx = chartCanvas.getContext('2d');
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No analysis data to display', chartCanvas.width / 2, chartCanvas.height / 2);
        return;
      }
      
      // Process data for chart (last 10 analyses in reverse order)
      const recentAnalyses = data.slice(0, 10).reverse();
      
      const labels = recentAnalyses.map(a => a.url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]);
      const scores = recentAnalyses.map(a => a.overall_score);
      
      // Create chart
      new Chart(chartCanvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'SEO Score',
            data: scores,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Score'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Domain'
              },
              ticks: {
                maxRotation: 45,
                minRotation: 45
              }
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              callbacks: {
                title: function(tooltipItems) {
                  const idx = tooltipItems[0].dataIndex;
                  return recentAnalyses[idx].url;
                },
                label: function(context) {
                  return `Score: ${context.parsed.y}%`;
                }
              }
            }
          }
        }
      });
    })
    .catch(error => {
      const ctx = chartCanvas.getContext('2d');
      ctx.font = '16px Arial';
      ctx.textAlign = 'center';
      ctx.fillStyle = '#dc3545';
      ctx.fillText(`Error loading chart data: ${error.message}`, chartCanvas.width / 2, chartCanvas.height / 2);
    });
}

/**
 * Refresh analysis data
 */
function refreshAnalysisData() {
  // Show refresh indicator
  const refreshButton = document.getElementById('refresh-data');
  if (refreshButton) {
    const originalContent = refreshButton.innerHTML;
    refreshButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...`;
    refreshButton.disabled = true;
    
    // Re-initialize components
    initializeAnalysisHistory();
    
    // Destroy and re-create chart
    const chartCanvas = document.getElementById('score-chart');
    if (chartCanvas) {
      const chartInstance = Chart.getChart(chartCanvas);
      if (chartInstance) {
        chartInstance.destroy();
      }
      initializeScoreChart();
    }
    
    // Reset button after refresh
    setTimeout(() => {
      refreshButton.innerHTML = originalContent;
      refreshButton.disabled = false;
    }, 1000);
  }
}

/**
 * Format date string
 * @param {String} dateString - ISO date string
 * @returns {String} Formatted date
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}
