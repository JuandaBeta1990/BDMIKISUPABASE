// app.js
// Variables globales (respetadas tal como en el original)
let projects = [];
let editingProjectId = null;
let zones = [];
let users = [];
let editingZoneId = null;
let editingUserId = null;
let allProjects = [];

// Elementos del DOM referenciados (se mantienen los mismos IDs)
const sidebar = document.getElementById('sidebar');
const menuButton = document.getElementById('menu-button');
const loading = document.getElementById('loading');
const projectsTable = document.getElementById('projects-table');
const projectsTbody = document.getElementById('projects-tbody');
const noProjects = document.getElementById('no-projects');
const searchInput = document.getElementById('search-input');
const addProjectBtn = document.getElementById('add-project-btn');
const projectModal = document.getElementById('project-modal');
const modalTitle = document.getElementById('modal-title');
const projectForm = document.getElementById('project-form');
const closeModal = document.getElementById('close-modal');
const cancelBtn = document.getElementById('cancel-btn');
const headerTitle = document.getElementById('header-title');
const headerSubtitle = document.getElementById('header-subtitle');
const dashboardLoading = document.getElementById('dashboard-loading');
const dashboardData = document.getElementById('dashboard-data');
const totalProjectsEl = document.getElementById('total-projects');
const availableUnitsEl = document.getElementById('available-units');
const soldUnitsEl = document.getElementById('sold-units');
const totalZonesEl = document.getElementById('total-zones');

const zonesLoading = document.getElementById('zones-loading');
const zonesTable = document.getElementById('zones-table');
const zonesTbody = document.getElementById('zones-tbody');
const noZones = document.getElementById('no-zones');
const addZoneBtn = document.getElementById('add-zone-btn');
const zoneModal = document.getElementById('zone-modal');
const zoneModalTitle = document.getElementById('zone-modal-title');
const zoneForm = document.getElementById('zone-form');
const closeZoneModal = document.getElementById('close-zone-modal');
const cancelZoneBtn = document.getElementById('cancel-zone-btn');

const usersLoading = document.getElementById('users-loading');
const usersTable = document.getElementById('users-table');
const usersTbody = document.getElementById('users-tbody');
const noUsers = document.getElementById('no-users');
const addUserBtn = document.getElementById('add-user-btn');
const userModal = document.getElementById('user-modal');
const userModalTitle = document.getElementById('user-modal-title');
const userForm = document.getElementById('user-form');
const closeUserModal = document.getElementById('close-user-modal');
const cancelUserBtn = document.getElementById('cancel-user-btn');
const userRoleFilter = document.getElementById('user-role-filter');
const userSearch = document.getElementById('user-search');
const clearUserFilters = document.getElementById('clear-user-filters');

// API Base URL
const API_BASE_URL = '/api';

// Función para hacer peticiones HTTP
async function apiRequest(url, options = {}) {
    try {
        // Asegurar que la URL termine con / para evitar redirects
        const finalUrl = url.endsWith('/') ? API_BASE_URL + url : API_BASE_URL + url + '/';

        const response = await fetch(finalUrl, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        // Handle cases where the response might be empty (e.g., 204 No Content)
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Navegación entre secciones
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });

    // Mostrar la sección seleccionada
    const targetSection = document.getElementById(sectionName + '-content');
    if (targetSection) {
        targetSection.style.display = 'block';
    }

    // Actualizar navegación activa
    document.querySelectorAll('aside nav a').forEach(link => {
        link.classList.remove('bg-white/10', 'text-white');
        link.classList.add('text-gray-300');
    });

    // Marcar el enlace actual como activo
    const currentLink = document.querySelector(`aside nav a[data-section="${sectionName}"]`);
    if (currentLink) {
        currentLink.classList.remove('text-gray-300');
        currentLink.classList.add('bg-white/10', 'text-white');
    }

    // Actualizar título de la cabecera
    switch(sectionName) {
        case 'dashboard':
            headerTitle.textContent = 'Dashboard';
            headerSubtitle.textContent = 'Resumen visual de la información más importante.';
            break;
        case 'projects':
            headerTitle.textContent = 'Gestión de Proyectos';
            headerSubtitle.textContent = 'Aquí puedes ver, editar y crear nuevos proyectos.';
            break;
        case 'units':
            headerTitle.textContent = 'Gestión de Unidades';
            headerSubtitle.textContent = 'Administra todas las unidades de tus proyectos.';
            break;
        case 'users':
            headerTitle.textContent = 'Gestión de Usuarios';
            headerSubtitle.textContent = 'Administra los usuarios del sistema y sus roles.';
            break;
        case 'zones':
            headerTitle.textContent = 'Gestión de Zonas';
            headerSubtitle.textContent = 'Gestiona las zonas geográficas del sistema.';
            break;
        case 'config':
            headerTitle.textContent = 'Configuración';
            headerSubtitle.textContent = 'Configuraciones generales del sistema.';
            break;
    }

    // Cargar datos específicos de la sección
    switch(sectionName) {
        case 'dashboard':
            if (typeof loadDashboard === 'function') loadDashboard();
            break;
        case 'projects':
            if (typeof loadProjects === 'function') loadProjects();
            break;
        case 'units':
            if (typeof loadUnits === 'function') loadUnits();
            break;
        case 'users':
            if (typeof loadUsers === 'function') loadUsers();
            break;
        case 'zones':
            if (typeof loadZones === 'function') loadZones();
            break;
        case 'config':
            // TODO: Implementar configuración
            break;
    }
}

// Mostrar mensajes de éxito/error
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 z-50 px-4 py-2 rounded-lg text-white ${
        type === 'success' ? 'bg-green-600' :
        type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    messageDiv.textContent = message;
    document.body.appendChild(messageDiv);

    setTimeout(() => {
        if (document.body.contains(messageDiv)) {
            document.body.removeChild(messageDiv);
        }
    }, 3000);
}

function showSuccess(message) { showMessage(message, 'success'); }
function showError(message) { showMessage(message, 'error'); }

// Toggle sidebar visibility
function toggleSidebar() {
    sidebar.classList.toggle('-translate-x-full');
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Lucide Icons
    if (typeof lucide !== 'undefined') lucide.createIcons();

    // Add event listeners for section switching
    document.querySelectorAll('[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) {
                showSection(section);
            }
        });
    });

    // Mostrar dashboard por defecto (llama a loadDashboard si está definido)
    showSection('dashboard');

    // Event listeners para proyectos
    if (addProjectBtn) addProjectBtn.addEventListener('click', openAddProjectModal);
    if (closeModal) closeModal.addEventListener('click', closeProjectModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeProjectModal);
    if (projectForm) projectForm.addEventListener('submit', handleFormSubmit);
    if (searchInput) searchInput.addEventListener('input', handleSearch);
    if (menuButton) menuButton.addEventListener('click', toggleSidebar);

    // Close modal when clicking outside
    if (projectModal) {
        projectModal.addEventListener('click', function(e) {
            if (e.target === projectModal) {
                closeProjectModal();
            }
        });
    }

    // Close sidebar if click outside
    document.addEventListener('click', function(e) {
        if (!sidebar.classList.contains('-translate-x-full') && !sidebar.contains(e.target) && !menuButton.contains(e.target)) {
            sidebar.classList.add('-translate-x-full');
        }
    });

    // Units filters event listeners (existirán cuando loadUnits se haya cargado)
    const applyBtn = document.getElementById('apply-filters-btn');
    const clearBtn = document.getElementById('clear-filters-btn');
    if (applyBtn) applyBtn.addEventListener('click', applyUnitsFilters);
    if (clearBtn) clearBtn.addEventListener('click', clearUnitsFilters);

    const filterSearch = document.getElementById('filter-search');
    const filterProject = document.getElementById('filter-project');
    const filterStatus = document.getElementById('filter-status');
    const filterTypology = document.getElementById('filter-typology');
    if (filterSearch) filterSearch.addEventListener('input', applyUnitsFilters);
    if (filterProject) filterProject.addEventListener('change', applyUnitsFilters);
    if (filterStatus) filterStatus.addEventListener('change', applyUnitsFilters);
    if (filterTypology) filterTypology.addEventListener('change', applyUnitsFilters);

    // Zonas & Usuarios listeners will be attached in their respective files but keep safety checks:
    if (addZoneBtn) addZoneBtn.addEventListener('click', openAddZoneModal);
    if (closeZoneModal) closeZoneModal.addEventListener('click', closeZoneModalHandler);
    if (cancelZoneBtn) cancelZoneBtn.addEventListener('click', closeZoneModalHandler);
    if (zoneForm) {
        zoneForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                name: document.getElementById('zone-name').value.trim(),
                description: document.getElementById('zone-description').value.trim() || null
            };
            if (!formData.name) {
                alert('El nombre de la zona es obligatorio.');
                return;
            }
            saveZone(formData);
        });
    }

    if (addUserBtn) addUserBtn.addEventListener('click', openAddUserModal);
    if (closeUserModal) closeUserModal.addEventListener('click', closeUserModalHandler);
    if (cancelUserBtn) cancelUserBtn.addEventListener('click', closeUserModalHandler);
    if (userRoleFilter) userRoleFilter.addEventListener('change', filterUsers);
    if (userSearch) userSearch.addEventListener('input', filterUsers);
    if (clearUserFilters) clearUserFilters.addEventListener('click', clearUserFiltersHandler);
    if (userForm) {
        userForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                username: document.getElementById('user-username').value.trim(),
                role: document.getElementById('user-role').value
            };
            if (!editingUserId) {
                formData.password = document.getElementById('user-password').value;
            }
            if (!formData.username || !formData.role) {
                alert('El nombre de usuario y rol son obligatorios.');
                return;
            }
            if (!editingUserId && !formData.password) {
                alert('La contraseña es obligatoria para nuevos usuarios.');
                return;
            }
            saveUser(formData);
        });
    }

    // Close modals when clicking outside (zones & users)
    if (zoneModal) {
        zoneModal.addEventListener('click', function(e) {
            if (e.target === zoneModal) {
                closeZoneModalHandler();
            }
        });
    }
    if (userModal) {
        userModal.addEventListener('click', function(e) {
            if (e.target === userModal) {
                closeUserModalHandler();
            }
        });
    }
});
