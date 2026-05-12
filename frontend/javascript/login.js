// ─── CONFIG ───────────────────────────────────────────────────────────────────
const API_BASE = "http://127.0.0.1:8000";

// ─── ESPERAR A QUE EL DOM ESTÉ LISTO ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {

  const form = document.querySelector(".register-form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    // ── 1. LEER LOS VALORES DEL FORMULARIO ──────────────────────────────────
    const payload = {
      nombre:     document.getElementById("name").value.trim(),
      contrasena: document.getElementById("password").value,
    };

    // ── 2. LLAMAR AL ENDPOINT /login/ ────────────────────────────────────────
    try {
      const response = await fetch(`${API_BASE}/login/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      // ── 3. EVALUAR LA RESPUESTA ────────────────────────────────────────────
      if (response.ok) {
        const data = await response.json();

        if (data.status === "ok") {
          // Guardar el nombre de usuario en sessionStorage para usarlo en events.html
          sessionStorage.setItem("usuario", data.data.usuario);

          // Login exitoso → redirigir a events.html
          window.location.href = "events.html";

        } else {
          // El backend respondió 200 pero con status "error" (usuario no existe)
          alert("Usuario o contraseña incorrectos.");
        }

      } else {
        const errorData = await response.json();
        console.error("Error del servidor:", errorData);
        alert("Error al iniciar sesión. Intenta de nuevo.");
      }

    } catch (error) {
      console.error("Error de conexión:", error);
      alert("No se pudo conectar con el servidor. ¿Está corriendo el backend?");
    }
  });

});