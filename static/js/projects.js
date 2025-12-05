// projects.js
function renderProjects(filteredProjects = null) {
    const projectsToRender = filteredProjects || projects;

    if (!projectsToRender || projectsToRender.length === 0) {
        if (projectsTable) projectsTable.style.display = 'none';
        if (noProjects) noProjects.style.display = 'block';
        return;
    }

    if (projectsTable) projectsTable.style.display = 'block';
    if (noProjects) noProjects.style.display = 'none';

    projectsTbody.innerHTML = projectsToRender.map(project => {
        const features = [];
        if (project.accepts_crypto) features.push('Crypto');
        if (project.turn_key) features.push('Llave en Mano');
        if (project.has_ocean_view) features.push('Vista al Mar');
        if (project.condo_regime) features.push('Condo');

        return `
        <tr class="border-b border-white/10 hover:bg-white/5 transition-colors">
            <td class="px-4 py-4 font-medium text-white">
                <div class="max-w-48 truncate">${project.name || 'Sin nombre'}</div>
                ${project.slug ? `<div class="text-xs text-gray-400">${project.slug}</div>` : ''}
            </td>
            <td class="px-4 py-4">${project.zone_name || 'Sin zona'}</td>
            <td class="px-4 py-4">
                <div class="max-w-32 truncate">${project.developer || 'Sin desarrollador'}</div>
            </td>
            <td class="px-4 py-4 text-center">
                <span class="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-medium">
                    ${project.total_units || 0}
                </span>
            </td>
            <td class="px-4 py-4">
                <div class="flex flex-wrap gap-1">
                    ${features.map(feature => `
                        <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-500/20 text-green-300">
                            ${feature}
                        </span>
                    `).join('')}
                </div>
            </td>
            <td class="px-4 py-4 text-center">
                <div class="flex items-center justify-center space-x-1">
                    <button onclick="viewProject('${project.id}')" class="p-2 text-gray-400 hover:text-gray-300 transition-colors" title="Ver Detalles">
                        <i data-lucide="eye"></i>
                    </button>
                    <button onclick="editProject('${project.id}')" class="p-2 text-blue-400 hover:text-blue-300 transition-colors" title="Editar Proyecto">
                        <i data-lucide="edit"></i>
                    </button>
                    <button onclick="deleteProject('${project.id}')" class="p-2 text-red-500 hover:text-red-400 transition-colors" title="Eliminar Proyecto">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </td>
        </tr>
        `;
    }).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

async function loadProjects() {
    if (loading) loading.style.display = 'flex';
    if (projectsTable) projectsTable.style.display = 'none';
    if (noProjects) noProjects.style.display = 'none';

    try {
        projects = await apiRequest('/projects');
        renderProjects();
    } catch (error) {
        console.error('Error loading projects:', error);
        showError('Error al cargar los proyectos');
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

function filterProjects(searchTerm) {
    if (!searchTerm) {
        renderProjects();
        return;
    }

    const filtered = projects.filter(project =>
        (project.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (project.developer || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (project.zone_name || '').toLowerCase().includes(searchTerm.toLowerCase())
    );

    renderProjects(filtered);
}

// Modal y CRUD
function openAddProjectModal() {
    editingProjectId = null;
    if (modalTitle) modalTitle.textContent = 'Nuevo Proyecto';
    if (projectForm) projectForm.reset();
    const first = document.getElementById('project-name');
    if (first) first.focus();
    if (projectModal) projectModal.classList.add('active');
}

function editProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    editingProjectId = projectId;
    if (modalTitle) modalTitle.textContent = 'Editar Proyecto';

    document.getElementById('project-name').value = project.name || '';
    document.getElementById('project-slug').value = project.slug || '';
    document.getElementById('project-developer').value = project.developer || '';
    document.getElementById('project-subzone').value = project.sub_zone || '';
    document.getElementById('project-units').value = project.total_units || '';
    document.getElementById('project-maps').value = project.maps_url || '';
    document.getElementById('project-concept').value = project.concept || '';
    document.getElementById('project-delivery').value = project.delivery_summary || '';
    document.getElementById('project-crypto').checked = project.accepts_crypto || false;
    document.getElementById('project-turnkey').checked = project.turn_key || false;
    document.getElementById('project-ocean').checked = project.has_ocean_view || false;
    document.getElementById('project-condo').checked = project.condo_regime || false;

    document.getElementById('project-name').focus();
    if (projectModal) projectModal.classList.add('active');
}

function closeProjectModal() {
    if (projectModal) projectModal.classList.remove('active');
    editingProjectId = null;
    if (projectForm) projectForm.reset();
}

async function saveProject(formData) {
    try {
        if (editingProjectId) {
            await apiRequest(`/projects/${editingProjectId}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            showSuccess('Proyecto actualizado correctamente');
        } else {
            await apiRequest('/projects', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            showSuccess('Proyecto creado correctamente');
        }

        await loadProjects();
        closeProjectModal();
    } catch (error) {
        console.error('Error saving project:', error);
        showError('Error al guardar el proyecto');
    }
}

async function deleteProject(projectId) {
    if (!confirm('¿Estás seguro de que quieres eliminar este proyecto?')) {
        return;
    }

    try {
        await apiRequest(`/projects/${projectId}`, {
            method: 'DELETE'
        });

        await loadProjects();
        showSuccess('Proyecto eliminado correctamente');
    } catch (error) {
        console.error('Error deleting project:', error);
        showError('Error al eliminar el proyecto');
    }
}

// Handle form submission for projects (exposed)
function handleFormSubmit(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('project-name').value.trim(),
        slug: document.getElementById('project-slug').value.trim() || null,
        developer: document.getElementById('project-developer').value.trim() || null,
        sub_zone: document.getElementById('project-subzone').value.trim() || null,
        total_units: parseInt(document.getElementById('project-units').value) || 0,
        maps_url: document.getElementById('project-maps').value.trim() || null,
        concept: document.getElementById('project-concept').value.trim() || null,
        delivery_summary: document.getElementById('project-delivery').value.trim() || null,
        accepts_crypto: document.getElementById('project-crypto').checked,
        turn_key: document.getElementById('project-turnkey').checked,
        has_ocean_view: document.getElementById('project-ocean').checked,
        condo_regime: document.getElementById('project-condo').checked
    };

    if (!formData.name) {
        alert('El nombre del proyecto es obligatorio.');
        return;
    }

    saveProject(formData);
}

// Search handler
function handleSearch(e) {
    filterProjects(e.target.value);
}

// Make some functions available on window (keeps same API as original inline)
window.editProject = editProject;
window.deleteProject = deleteProject;
window.viewProject = viewProject;
