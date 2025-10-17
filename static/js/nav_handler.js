// static/js/nav_handler.js

// 🔑 FUNCIÓN DE UTILIDAD PARA DECODIFICAR JWT 🔑
function parseJwt(token) {
    try {
        // El payload es la segunda parte (índice 1)
        return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
        // Devuelve null si el token es inválido o no se puede decodificar
        return null;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const authenticatedOptions = document.getElementById('authenticated-options');
    const unauthenticatedOptions = document.getElementById('unauthenticated-options');
    const logoutButton = document.getElementById('logout-button');
    // 🔑 NUEVO: Referencia al enlace del administrador (ID del layout.html)
    const adminDashboardLink = document.getElementById('admin-dashboard-link'); 
    
    const token = localStorage.getItem('token'); 

    // ----------------------------------------------------------------------
    // --- LÓGICA DE AUTENTICACIÓN Y ROLES ---
    // ----------------------------------------------------------------------

    if (token) {
        // El usuario está autenticado
        unauthenticatedOptions.style.display = 'none';
        authenticatedOptions.style.display = 'flex';

        // Decodificar token para verificar rol
        const payload = parseJwt(token);

        if (payload && payload.role === 'admin') {
            // Mostrar enlace del Dashboard para el administrador
            if (adminDashboardLink) {
                // 🔑 CAMBIO: Usar 'flex' para que se muestre correctamente en el contenedor 'flex'
                adminDashboardLink.style.display = 'flex'; 
            }
        } else {
            // Ocultar enlace del Dashboard para usuarios normales
            if (adminDashboardLink) {
                adminDashboardLink.style.display = 'none';
            }
        }

    } else {
        // El usuario NO está autenticado
        unauthenticatedOptions.style.display = 'flex';
        authenticatedOptions.style.display = 'none';

        // Asegurar que el enlace del admin esté oculto si no hay token
        if (adminDashboardLink) {
            adminDashboardLink.style.display = 'none';
        }
    }

    // Lógica para cerrar sesión
    if (logoutButton) {
        logoutButton.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '/'; 
        });
    }

    // ----------------------------------------------------------------------
    // --- LÓGICA INTEGRADA DEL ESTADO DEL PASO Y CAMBIO DE IMÁGENES ---
    // ----------------------------------------------------------------------

    const statusContainer = document.getElementById('pass-status-container');
    const statusText = document.getElementById('pass-status-text');
    const passImage = document.getElementById('pass-image');

    async function fetchAndUpdatePassStatus() {
        try {
            const res = await fetch("/paso/public_api"); 
            
            if (!res.ok) {
                statusContainer.style.backgroundColor = 'gray';
                statusText.textContent = 'ERROR al cargar estado';
                return;
            }

            const data = await res.json();
            
            const estado = data.estado ? data.estado.toLowerCase() : 'desconocido'; 
            
            // 1. Actualiza el estado del paso
            if (estado === "abierto" || estado === "habilitado") {
                statusContainer.style.backgroundColor = 'green';
                statusText.textContent = 'PASO ABIERTO';
            } else if (estado === "cerrado") {
                statusContainer.style.backgroundColor = 'red';
                statusText.textContent = 'PASO CERRADO';
            } else {
                statusContainer.style.backgroundColor = 'gray';
                statusText.textContent = 'ESTADO DESCONOCIDO';
            }
            
            // 2. Actualiza la imagen
            const imageFilename = data.image_filename || 'default_pass.jpg'; 
            passImage.src = `/static/images/${imageFilename}`;

        } catch (error) {
            console.error("Fallo al obtener la información del paso:", error);
            statusContainer.style.backgroundColor = 'gray';
            statusText.textContent = 'ERROR de conexión';
        }
    }

    fetchAndUpdatePassStatus();

}); // Cierre del document.addEventListener