let lastChartData = null;

document.addEventListener("DOMContentLoaded", () => {
    const chartSelect = document.getElementById("chart-timeframe");
    const recentSelect = document.getElementById("recent-timeframe");
    const mostSelect = document.getElementById("most-timeframe");
    const levelSelect = document.getElementById("level-timeframe");
    const eventSelect = document.getElementById("event-timeframe");

    function updateAll() {
        if (document.visibilityState === "visible") {
            fetchChart(chartSelect.value);
            fetchLogs(recentSelect.value);
            fetchActiveLogs(mostSelect.value);
            fetchLevelLogs(levelSelect.value);
            fetchEventLogs(eventSelect.value);
        }
    }

    updateAll();

    chartSelect.addEventListener("change", () => fetchChart(chartSelect.value));
    recentSelect.addEventListener("change", () => fetchLogs(recentSelect.value));
    mostSelect.addEventListener("change", () => fetchActiveLogs(mostSelect.value));
    levelSelect.addEventListener("change", () => fetchLevelLogs(levelSelect.value));
    eventSelect.addEventListener("change", () => fetchEventLogs(eventSelect.value));

    setInterval(updateAll, 5000);
});

function fetchChart(timeframe) {
    fetchPost("/logs/chart", { last_hour: parseFloat(timeframe) })
    .then(data => {
        const newLogs = data.logs;
        if (JSON.stringify(newLogs) === JSON.stringify(lastChartData)) return;
        lastChartData = newLogs;

        const parent = document.getElementById("activity-overview-chart");
        parent.innerHTML = "";

        if (!newLogs?.length) {
            parent.innerHTML = "<p style='color: #bbb;'>No data to view</p>";
            return;
        }

        const canvas = document.createElement("canvas");
        canvas.id = "activityChart";
        parent.appendChild(canvas);

        const labels = newLogs.map(item =>
            luxon.DateTime.fromISO(item.time).toFormat("LLLL dd, HH:mm")
        );
        const counts = newLogs.map(item => item.count);

        const ctx = canvas.getContext("2d");
        new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "",
                    data: counts,
                    backgroundColor: "rgba(0, 230, 153, 0.2)",
                    borderColor: "rgba(0, 230, 153, 1)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: "category",
                        ticks: { autoSkip: false }
                    },
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    })
    .catch(() => {
        document.getElementById("activity-overview-chart").innerHTML =
            "<p style='color: #bbb;'>Failed to load chart</p>";
    });
}

function fetchLogs(timeframe) {
    fetchPost("/logs/recent", { last_hour: parseFloat(timeframe) })
    .then(data => {
        const table = document.getElementById("recent-activity-logs");
        table.innerHTML = "";

        if (!data.logs?.length) {
            table.innerHTML = `<tr><td colspan="2">No logs to view</td></tr>`;
            return;
        }

        data.logs.forEach(log => {
            const icon = getIconForEvent(log.event);
            const row = `
                <tr>
                    <td>${icon}</td>
                    <td>${escapeHtml(log.src_path)}</td>
                </tr>
            `;
            table.insertAdjacentHTML("beforeend", row);
        });
    })
    .catch(error => {
        document.getElementById("recent-activity-logs").innerHTML =
            `<tr><td colspan="2">Error: ${error}</td></tr>`;
    });
}

function fetchActiveLogs(timeframe) {
    fetchPost("/logs/most", { last_hour: parseFloat(timeframe) })
    .then(data => {
        const table = document.getElementById("most-active-logs");
        table.innerHTML = "";

        if (!data.logs?.length) {
            table.innerHTML = `<tr><td colspan="2">No logs to view</td></tr>`;
            return;
        }

        data.logs.forEach(log => {
            const row = `
                <tr>
                    <td style="padding-right: 10px;">(+${log.count})</td>
                    <td>${escapeHtml(log.src_path)}</td>
                </tr>
            `;
            table.insertAdjacentHTML("beforeend", row);
        });
    })
    .catch(error => {
        document.getElementById("most-active-logs").innerHTML =
            `<tr><td colspan="2">Error: ${error}</td></tr>`;
    });
}

function fetchLevelLogs(timeframe) {
    fetchPost("/logs/level_activity", { last_hour: parseFloat(timeframe) })
    .then(data => {
        const total = data.logs["total"];
        Object.entries(data.logs).forEach(([key, value]) => {
            const indicator = document.querySelector(`circle-progress.${key}`);
            if (indicator) {
                indicator.setAttribute("value", value);
                indicator.setAttribute("max", total);
            }
        });
    })
}

function fetchEventLogs(timeframe) {
    fetchPost("/logs/event_activity", { last_hour: parseFloat(timeframe) })
    .then(data => {
        const total = data.logs["total"];
        Object.entries(data.logs).forEach(([key, value]) => {
            const indicator = document.querySelector(`circle-progress.${key}`);
            if (indicator) {
                indicator.setAttribute("value", value);
                indicator.setAttribute("max", total);
            }
        });
    })
}

function fetchPost(url, payload) {
    return fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    }).then(res => res.json());
}

function getIconForEvent(event) {
    switch (event) {
        case "MODIFIED": return `<i class="fa-solid fa-pen"></i>`;
        case "CREATED":  return `<i class="fa-solid fa-folder-plus"></i>`;
        case "DELETED":  return `<i class="fa-solid fa-trash"></i>`;
        case "RENAMED":  return `<i class="fa-solid fa-file-signature"></i>`;
        default:         return "";
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/"/g, "&#039;");
}