const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('user-name').textContent = user.nombre || 'Usuario';

    loadAnalisisData();
});

function showView(view) {
    document.getElementById('analisis-view').classList.add('d-none');
    document.getElementById('graficos-view').classList.add('d-none');
    document.getElementById('proyectos-view').classList.add('d-none');
    document.getElementById(`${view}-view`).classList.remove('d-none');
}

async function loadAnalisisData() {
    const data = await ipcRenderer.invoke('get-analisis-data');

    // Búsquedas más utilizadas
    const topKeywords = document.getElementById('top-keywords');
    topKeywords.innerHTML = data.top_keywords?.map(item => `
        <tr>
            <td>${item.palabra_clave}</td>
            <td>${item.total}</td>
        </tr>
    `).join('') || '<tr><td colspan="2">No hay datos</td></tr>';

    // Provincias más buscadas
    const topProvinces = document.getElementById('top-provinces');
    topProvinces.innerHTML = data.top_provinces?.map(item => `
        <tr>
            <td>${item.provincia === '0' ? 'Toda España' : item.provincia}</td>
            <td>${item.total}</td>
        </tr>
    `).join('') || '<tr><td colspan="2">No hay datos</td></tr>';

    // Consultas por día
    const dailyQueries = document.getElementById('daily-queries');
    dailyQueries.innerHTML = data.daily_queries?.map(item => `
        <tr>
            <td>${item.day}</td>
            <td>${item.total}</td>
        </tr>
    `).join('') || '<tr><td colspan="2">No hay datos</td></tr>';
}

function logout() {
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}