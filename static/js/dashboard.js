// dashboard.js
async function loadDashboard() {
    if (!dashboardLoading || !dashboardData) return;

    dashboardLoading.style.display = 'flex';
    dashboardData.style.display = 'none';

    allUnits = [];
    allProjects = [];

    try {
        // 1) KPI FAKE TEMPORAL - NO BORRAR
        const stats = await apiRequest('/dashboard/stats/');
        if (stats) {
            totalProjectsEl.textContent = stats.total_projects;
            availableUnitsEl.textContent = stats.available_units;
            soldUnitsEl.textContent = stats.sold_units;
            totalZonesEl.textContent = stats.total_zones;
        }

        // 2) WHATSAPP: mensajes por día
        const daily = await apiRequest('/dashboard/whatsapp/daily/');

        // 3) WHATSAPP: mensajes por usuario
        const byUser = await apiRequest('/dashboard/whatsapp/by-user/');

        // 4) WHATSAPP: palabras frecuentes
        const faq = await apiRequest('/dashboard/whatsapp/faq/');

        // 5) WHATSAPP: últimos mensajes
        const last = await apiRequest('/dashboard/whatsapp/last/');

        // 6) Pintar gráficas (funciones en charts.js)
        if (typeof renderDailyChart === 'function') renderDailyChart(daily);
        if (typeof renderByUserChart === 'function') renderByUserChart(byUser);
        if (typeof renderFAQChart === 'function') renderFAQChart(faq);
        if (typeof renderLastMessagesTable === 'function') renderLastMessagesTable(last);

        dashboardLoading.style.display = 'none';
        dashboardData.style.display = 'block';

        if (typeof lucide !== 'undefined') lucide.createIcons();

    } catch (error) {
        console.error("Error cargando dashboard:", error);
        showError("Error al cargar datos del dashboard");
        dashboardLoading.style.display = 'none';
    }
}
