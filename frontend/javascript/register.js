// ─── CONFIG ───────────────────────────────────────────────────────────────────
const API_BASE = "http://127.0.0.1:8000"; // Cambia esto si tu backend corre en otro puerto

// ─── ESPERAR A QUE EL DOM ESTÉ LISTO ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {

  const form = document.querySelector(".register-form");

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // Evita que el formulario recargue la página

    // ── 1. LEER LOS VALORES DEL FORMULARIO ──────────────────────────────────
    const payload = {
      nombre:     document.getElementById("name").value.trim(),
      contrasena: document.getElementById("password").value,
      email:      document.getElementById("email").value.trim(),
      genero:     document.getElementById("gender").value,
      edad:       parseInt(document.getElementById("age").value, 10),
    };

    // ── 2. LLAMAR AL ENDPOINT /create_user/ ─────────────────────────────────
    try {
      const response = await fetch(`${API_BASE}/create_user/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      // ── 3. EVALUAR LA RESPUESTA ────────────────────────────────────────────
      if (response.ok) {
        // Registro exitoso → redirigir a events.html
        window.location.href = "events.html";
      } else {
        // El servidor respondió con un error HTTP (ej: 422 Unprocessable Entity)
        const errorData = await response.json();
        console.error("Error del servidor:", errorData);
        alert("No se pudo crear la cuenta. Revisa los datos e intenta de nuevo.");
      }

    } catch (error) {
      // Error de red (backend apagado, CORS, etc.)
      console.error("Error de conexión:", error);
      alert("No se pudo conectar con el servidor. ¿Está corriendo el backend?");
    }
  });

});