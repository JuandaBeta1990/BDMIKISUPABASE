// units.js

let allUnits = [];

async function loadUnits() {
    const unitsLoadingEl = document.getElementById('units-loading');
    const noUnitsEl = document.getElementById('no-units');

    if (unitsLoadingEl) unitsLoadingEl.classList.remove('hidden');
    if (noUnitsEl) noUnitsEl.classList.add('hidden');

    try {
        // Cargar proyectos para los filtros
        const projectsResp = await apiRequest('/projects');
        allProjects = projectsResp;
        populateProjectFilter();

        // Cargar TODAS las unidades directamente
        const unitsResponse = await apiRequest('/units');
        // Note: original hacía unitsResponse.json() tras apiRequest erroneamente.
        const units = unitsResponse || [];

        // Agregar el nombre del proyecto a cada unidad
        allUnits = units.map(unit => {
            const project = allProjects.find(p => String(p.id) === String(unit.project_id));
            return {
                ...unit,
                project_name: project ? project.name : 'Proyecto desconocido'
            };
        });

        console.log(`Cargadas ${allUnits.length} unidades`);

        // Aplicar filtros y renderizar
        displayUnits(allUnits);

        populateFilters();

    } catch (error) {
        console.error('Error loading units:', error);
        if (unitsLoadingEl) unitsLoadingEl.classList.add('hidden');
        if (noUnitsEl) noUnitsEl.classList.remove('hidden');
    } finally {
        if (unitsLoadingEl) unitsLoadingEl.classList.add('hidden');
    }
}

function populateProjectFilter() {
    const select = document.getElementById('filter-project');
    if (!select) return;
    select.innerHTML = '<option value="">Todos los proyectos</option>';

    (allProjects || []).forEach(project => {
        const option = document.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        select.appendChild(option);
    });
}

function populateFilters() {
    const typologies = [...new Set((allUnits || []).map(unit => unit.typology).filter(t => t))];
    const typologySelect = document.getElementById('filter-typology');
    if (!typologySelect) return;
    typologySelect.innerHTML = '<option value="">Todas las tipologías</option>';

    typologies.forEach(typology => {
        const option = document.createElement('option');
        option.value = typology;
        option.textContent = typology;
        typologySelect.appendChild(option);
    });
}

function displayUnits(units) {
    const tbody = document.getElementById('units-table-body');
    const countElement = document.getElementById('units-count');

    if (!tbody || !countElement) return;

    countElement.textContent = units.length;

    if (units.length === 0) {
        document.getElementById('no-units').classList.remove('hidden');
        tbody.innerHTML = '';
        return;
    }

    tbody.innerHTML = units.map(unit => `
        <tr class="border-b border-gray-700/50 hover:bg-white/5">
            <td class="py-3 text-gray-300">${unit.project_name || 'Sin proyecto'}</td>
            <td class="py-3 text-white font-medium">${unit.unit_identifier}</td>
            <td class="py-3 text-gray-300">${unit.typology || 'N/A'}</td>
            <td class="py-3 text-gray-300">${unit.level || 'N/A'}</td>
            <td class="py-3 text-gray-300">${unit.total_area_sqm ? Number(unit.total_area_sqm).toFixed(2) : 'N/A'}</td>
            <td class="py-3">
                <span class="px-2 py-1 rounded text-xs font-medium ${getStatusColor(unit.status)}">
                    ${unit.status || 'Sin estado'}
                </span>
            </td>
            <td class="py-3 text-gray-300">${unit.delivery_date || 'N/A'}</td>
            <td class="py-3">
                <div class="flex items-center space-x-2">
                    <button onclick="viewUnit('${unit.id}')" class="text-blue-400 hover:text-blue-300 p-1">
                        <i data-lucide="eye" class="w-4 h-4"></i>
                    </button>
                    <button onclick="editUnit('${unit.id}')" class="text-yellow-400 hover:text-yellow-300 p-1">
                        <i data-lucide="edit" class="w-4 h-4"></i>
                    </button>
                    <button onclick="deleteUnit('${unit.id}', '${unit.unit_identifier}')" class="text-red-400 hover:text-red-300 p-1">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function getStatusColor(status) {
    switch (String(status || '').toLowerCase()) {
        case 'disponible':
            return 'bg-green-500/20 text-green-400';
        case 'reservada':
            return 'bg-yellow-500/20 text-yellow-400';
        case 'vendida':
            return 'bg-red-500/20 text-red-400';
        case 'en construcción':
            return 'bg-blue-500/20 text-blue-400';
        default:
            return 'bg-gray-500/20 text-gray-400';
    }
}

function applyUnitsFilters() {
    const projectFilter = document.getElementById('filter-project').value;
    const statusFilter = document.getElementById('filter-status').value;
    const typologyFilter = document.getElementById('filter-typology').value;
    const searchFilter = document.getElementById('filter-search').value.toLowerCase().trim();

    const filteredUnits = (allUnits || []).filter(unit => {
        const matchesProject =
            !projectFilter ||
            String(unit.project_id).trim() === String(projectFilter).trim();

        const matchesStatus =
            !statusFilter ||
            String(unit.status).toLowerCase().trim() === String(statusFilter).toLowerCase().trim();

        const matchesTypology =
            !typologyFilter ||
            String(unit.typology).toLowerCase().trim() === String(typologyFilter).toLowerCase().trim();

        const matchesSearch =
            !searchFilter ||
            String(unit.unit_identifier).toLowerCase().includes(searchFilter);

        return matchesProject && matchesStatus && matchesTypology && matchesSearch;
    });

    displayUnits(filteredUnits);
}


function clearUnitsFilters() {
    document.getElementById('filter-project').value = '';
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-typology').value = '';
    document.getElementById('filter-search').value = '';
    displayUnits(allUnits);
}

// Unit management functions (stubs preserved)
function viewUnit(unitId) { alert(`Ver unidad: ${unitId}`); }
function editUnit(unitId) { alert(`Editar unidad: ${unitId}`); }

async function deleteUnit(unitId, unitIdentifier) {
    if (confirm(`¿Estás seguro de que quieres eliminar la unidad "${unitIdentifier}"?`)) {
        try {
            await apiRequest(`/units/${unitId}`, { method: 'DELETE' });

            allUnits = (allUnits || []).filter(unit => unit.id !== unitId);
            applyUnitsFilters();
            alert('Unidad eliminada correctamente');
        } catch (error) {
            console.error('Error deleting unit:', error);
            alert('Error al eliminar la unidad');
        }
    }
}

// Exponer funciones globales usadas en HTML inline
window.viewUnit = viewUnit;
window.editUnit = editUnit;
window.deleteUnit = deleteUnit;
window.applyUnitsFilters = applyUnitsFilters;
window.clearUnitsFilters = clearUnitsFilters;
