const token = localStorage.getItem("token");

if (!token) {
    // 🔑 CAMBIO: Redirige al LOGIN si no hay token para proteger la ruta
    window.location.href = "/login";
}

// Fetch info del usuario
fetch("/api/dashboard", {
    headers: { "Authorization": `Bearer ${token}` }
})
    .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
    })
    .then(data => {
        document.getElementById("username").innerText = data.username;
        document.getElementById("role").innerText = data.role;

        if (data.role === "admin") {
            document.getElementById("adminSection").style.display = "block";

            // Fetch lista de usuarios
            fetch("/api/users", {
                headers: { "Authorization": `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(users => {
                    const tbody = document.getElementById("usersTableBody");
                    tbody.innerHTML = "";
                    users.forEach(u => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
            <td>${u.username}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td>
                <button class="btn btn-sm btn-primary me-1" onclick="editUser('${u.id}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser('${u.id}')">Delete</button>
            </td>
        `;
                        tbody.appendChild(row);
                    });
                });
        }
    })
    .catch(err => {
        alert("Session expired or unauthorized. Please login again.");
        localStorage.clear();
        window.location.href = "/";
    });

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.clear();
    window.location.href = "/";
});

// Funciones para Edit y Delete (deben llamar endpoints protegidos)
function editUser(userId) {
    const newRole = prompt("Enter new role for user (user/admin):");
    if (!newRole) return;
    fetch(`/api/users/${userId}`, {
        method: "PATCH",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ role: newRole })
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
}

function deleteUser(userId) {
    if (!confirm("Are you sure you want to delete this user?")) return;
    fetch(`/api/users/${userId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            location.reload();
        });
}