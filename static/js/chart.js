// charts.js
function renderDailyChart(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById("chart-daily");
    if (!ctx) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.map(x => x.fecha),
            datasets: [{
                label: "Mensajes por día",
                data: data.map(x => x.total),
                borderWidth: 2,
                fill: false
            }]
        }
    });
}

function renderByUserChart(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById("chart-by-user");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.map(x => x.usuario),
            datasets: [{
                label: "Mensajes",
                data: data.map(x => x.total),
                borderWidth: 1
            }]
        }
    });
}

function renderFAQChart(data) {
    if (!data || data.length === 0) return;

    const ctx = document.getElementById("chart-faq");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.map(x => x.palabra),
            datasets: [{
                label: "Frecuencia",
                data: data.map(x => x.total),
                borderWidth: 1
            }]
        }
    });
}

function renderLastMessagesTable(rows) {
    const tbody = document.getElementById("table-last-messages");
    if (!tbody) return;

    tbody.innerHTML = rows.map(msg => `
        <tr class="border-b border-gray-700">
            <td class="px-4 py-2">${msg.nombreusuario || msg.idusuario}</td>
            <td class="px-4 py-2">${msg.historial_conversacion}</td>
            <td class="px-4 py-2">${msg.fecha}</td>
        </tr>
    `).join("");
}
