// zones.js

async function loadZones() {
    if (zonesLoading) zonesLoading.style.display = 'flex';
    if (zonesTable) zonesTable.style.display = 'none';
    if (noZones) noZones.style.display = 'none';

    try {
        zones = await apiRequest('/zones');
        console.log('Zones loaded:', zones);
        renderZones();
    } catch (error) {
        console.error('Error loading zones:', error);
        showError('Error al cargar las zonas');
    } finally {
        if (zonesLoading) zonesLoading.style.display = 'none';
    }
}

function renderZones() {
    if (!zones || zones.length === 0) {
        if (zonesTable) zonesTable.style.display = 'none';
        if (noZones) noZones.style.display = 'block';
        return;
    }

    if (zonesTable) zonesTable.style.display = 'block';
    if (noZones) noZones.style.display = 'none';

    zonesTbody.innerHTML = zones.map(zone => `
        <tr class="border-b border-white/10 hover:bg-white/5 transition-colors">
            <td class="px-4 py-4 font-medium text-white">${zone.name}</td>
            <td class="px-4 py-4 text-gray-300">${zone.description || 'Sin descripción'}</td>
            <td class="px-4 py-4 text-center">
                <span class="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-medium">
                    ${zone.project_count || 0}
                </span>
            </td>
            <td class="px-4 py-4 text-gray-400">${new Date(zone.created_at).toLocaleDateString()}</td>
            <td class="px-4 py-4 text-center">
                <div class="flex items-center justify-center space-x-1">
                    <button onclick="editZone('${zone.id}')" class="p-2 text-blue-400 hover:text-blue-300 transition-colors" title="Editar Zona">
                        <i data-lucide="edit"></i>
                    </button>
                    <button onclick="deleteZone('${zone.id}', '${zone.name}')" class="p-2 text-red-500 hover:text-red-400 transition-colors" title="Eliminar Zona">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function openAddZoneModal() {
    editingZoneId = null;
    zoneModalTitle.textContent = 'Nueva Zona';
    zoneForm.reset();
    document.getElementById('zone-name').focus();
    zoneModal.classList.add('active');
}

function editZone(zoneId) {
    const zone = zones.find(z => z.id === zoneId);
    if (!zone) return;

    editingZoneId = zoneId;
    zoneModalTitle.textContent = 'Editar Zona';
    document.getElementById('zone-name').value = zone.name || '';
    document.getElementById('zone-description').value = zone.description || '';
    document.getElementById('zone-name').focus();
    zoneModal.classList.add('active');
}

function closeZoneModalHandler() {
    zoneModal.classList.remove('active');
    editingZoneId = null;
    zoneForm.reset();
}

async function saveZone(formData) {
    try {
        if (editingZoneId) {
            await apiRequest(`/zones/${editingZoneId}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            showSuccess('Zona actualizada correctamente');
        } else {
            await apiRequest('/zones', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            showSuccess('Zona creada correctamente');
        }
        await loadZones();
        closeZoneModalHandler();
    } catch (error) {
        console.error('Error saving zone:', error);
        showError('Error al guardar la zona');
    }
}

async function deleteZone(zoneId, zoneName) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la zona "${zoneName}"?`)) return;
    try {
        await apiRequest(`/zones/${zoneId}`, { method: 'DELETE' });
        await loadZones();
        showSuccess('Zona eliminada correctamente');
    } catch (error) {
        console.error('Error deleting zone:', error);
        showError('Error al eliminar la zona');
    }
}

// Exponer funciones globales
window.editZone = editZone;
window.deleteZone = deleteZone;
window.openAddZoneModal = openAddZoneModal;
