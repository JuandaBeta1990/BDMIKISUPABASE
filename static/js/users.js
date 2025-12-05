// users.js

async function loadUsers() {
    if (usersLoading) usersLoading.style.display = 'flex';
    if (usersTable) usersTable.style.display = 'none';
    if (noUsers) noUsers.style.display = 'none';

    try {
        users = await apiRequest('/users');
        renderUsers();
    } catch (error) {
        console.error('Error loading users:', error);
        showError('Error al cargar los usuarios');
    } finally {
        if (usersLoading) usersLoading.style.display = 'none';
    }
}

function renderUsers(filtered = null) {
    const list = filtered || users;

    if (!list || list.length === 0) {
        if (usersTable) usersTable.style.display = 'none';
        if (noUsers) noUsers.style.display = 'block';
        return;
    }

    if (usersTable) usersTable.style.display = 'block';
    if (noUsers) noUsers.style.display = 'none';

    usersTbody.innerHTML = list.map(u => `
        <tr class="border-b border-white/10 hover:bg-white/5 transition-colors">
            <td class="px-4 py-4 font-medium text-white">${u.username}</td>
            <td class="px-4 py-4 text-gray-300">${u.role}</td>
            <td class="px-4 py-4 text-gray-300">${u.status || 'Activo'}</td>
            <td class="px-4 py-4 text-gray-400">${new Date(u.created_at).toLocaleDateString()}</td>
            <td class="px-4 py-4 text-center">
                <div class="flex items-center justify-center space-x-1">
                    <button onclick="editUser('${u.id}')" class="p-2 text-blue-400 hover:text-blue-300 transition-colors" title="Editar Usuario">
                        <i data-lucide="edit"></i>
                    </button>
                    <button onclick="deleteUser('${u.id}', '${u.username}')" class="p-2 text-red-500 hover:text-red-400 transition-colors" title="Eliminar Usuario">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function filterUsers() {
    const searchTerm = (userSearch && userSearch.value || '').toLowerCase();
    const roleFilter = (userRoleFilter && userRoleFilter.value) || '';

    const filtered = (users || []).filter(user => {
        const matchesSearch = !searchTerm || (user.username || '').toLowerCase().includes(searchTerm);
        const matchesRole = !roleFilter || user.role === roleFilter;
        return matchesSearch && matchesRole;
    });

    renderUsers(filtered);
}

function clearUserFiltersHandler() {
    if (userRoleFilter) userRoleFilter.value = '';
    if (userSearch) userSearch.value = '';
    renderUsers();
}

function openAddUserModal() {
    editingUserId = null;
    userModalTitle.textContent = 'Nuevo Usuario';
    if (userForm) userForm.reset();
    document.getElementById('password-field').style.display = 'block';
    document.getElementById('user-password').required = true;
    document.getElementById('user-username').focus();
    if (userModal) userModal.classList.add('active');
}

function editUser(userId) {
    const user = users.find(u => u.id === userId);
    if (!user) return;

    editingUserId = userId;
    userModalTitle.textContent = 'Editar Usuario';
    document.getElementById('user-username').value = user.username || '';
    document.getElementById('user-role').value = user.role || '';
    document.getElementById('password-field').style.display = 'none';
    document.getElementById('user-password').required = false;
    document.getElementById('user-username').focus();
    if (userModal) userModal.classList.add('active');
}

function closeUserModalHandler() {
    if (userModal) userModal.classList.remove('active');
    editingUserId = null;
    if (userForm) userForm.reset();
}

async function saveUser(formData) {
    try {
        if (editingUserId) {
            delete formData.password;
            await apiRequest(`/users/${editingUserId}`, {
                method: 'PUT',
                body: JSON.stringify(formData)
            });
            showSuccess('Usuario actualizado correctamente');
        } else {
            await apiRequest('/users', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            showSuccess('Usuario creado correctamente');
        }
        await loadUsers();
        closeUserModalHandler();
    } catch (error) {
        console.error('Error saving user:', error);
        showError('Error al guardar el usuario');
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`¿Estás seguro de que quieres eliminar el usuario "${username}"?`)) {
        return;
    }

    try {
        await apiRequest(`/users/${userId}`, { method: 'DELETE' });
        await loadUsers();
        showSuccess('Usuario eliminado correctamente');
    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Error al eliminar el usuario');
    }
}

// Exponer funciones globales
window.editUser = editUser;
window.deleteUser = deleteUser;
window.openAddUserModal = openAddUserModal;
window.saveUser = saveUser;
window.closeUserModalHandler = closeUserModalHandler;
window.filterUsers = filterUsers;
