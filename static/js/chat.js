
const formulario = document.getElementById("formulario");
const entrada = document.getElementById("mensaje");
const conversacion = document.getElementById("conversacion");
const boton = document.getElementById("enviar");
const botonNuevaConversacion = document.getElementById("nueva-conversacion");

// Aquí guardaremos todos los mensajes
let historial = [];


function mostrarMensaje(autor, texto, clase) {
    const elemento = document.createElement("div");

    elemento.className = "mensaje " + clase;
    elemento.textContent = autor + ": " + texto;

    conversacion.appendChild(elemento);
    conversacion.scrollTop = conversacion.scrollHeight;
}


formulario.addEventListener("submit", async function(evento) {
    evento.preventDefault();

    const mensaje = entrada.value.trim();
    if (!mensaje || boton.disabled) return;

    // Añadir el mensaje del usuario al historial
    historial.push({
        role: "user",
        content: mensaje
    });

    mostrarMensaje("Tú", mensaje, "usuario");

    entrada.value = "";
    boton.disabled = true;

    try {
        const respuesta = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                historial: historial
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || "Error del servidor");
        }

        // Guardar también la respuesta de DeepSeek
        historial.push({
            role: "assistant",
            content: datos.respuesta
        });

        mostrarMensaje("DeepSeek", datos.respuesta, "ia");

    } catch (error) {
        // Si falla la petición, retirar el mensaje
        // para poder intentarlo de nuevo
        historial.pop();

        mostrarMensaje("Error", error.message, "ia");

    } finally {
        boton.disabled = false;
        entrada.focus();
    }
});

botonNuevaConversacion.addEventListener("click", function() {
    if (boton.disabled) return;

    // Borrar el historial de mensajes
    historial = [];

    // Limpiar los mensajes de la pantalla
    conversacion.innerHTML = "";

    // Limpiar el campo de texto
    entrada.value = "";

    entrada.focus();
});
