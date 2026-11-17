
const formulario = document.getElementById("formulario");
const entrada = document.getElementById("mensaje");
const conversacion = document.getElementById("conversacion");
const boton = document.getElementById("enviar");

const botonNuevaConversacion =
    document.getElementById("nueva-conversacion");

let conversacionId = null;
let ocupado = false;


function mostrarMensaje(autor, texto, clase) {
    const elemento = document.createElement("div");

    elemento.className = "mensaje " + clase;
    elemento.textContent = autor + ": " + texto;

    conversacion.appendChild(elemento);
    conversacion.scrollTop = conversacion.scrollHeight;
}


function bloquearInterfaz(bloqueada) {
    ocupado = bloqueada;
    boton.disabled = bloqueada;
    botonNuevaConversacion.disabled = bloqueada;
}


async function crearConversacion() {
    const respuesta = await fetch("/nueva-conversacion", {
        method: "POST"
    });

    const datos = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(
            datos.error || "No se pudo crear la conversación."
        );
    }

    conversacionId = datos.conversacion_id;
}


formulario.addEventListener("submit", async function(evento) {
    evento.preventDefault();

    const mensaje = entrada.value.trim();

    if (!mensaje || ocupado) return;

    bloquearInterfaz(true);

    try {
        // Crear la conversación al enviar
        // el primer mensaje.
        if (conversacionId === null) {
            await crearConversacion();
        }

        const respuesta = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                conversacion_id: conversacionId,
                mensaje: mensaje
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.error || "Error del servidor."
            );
        }

        mostrarMensaje("Tú", mensaje, "usuario");

        mostrarMensaje(
            "DeepSeek",
            datos.respuesta,
            "ia"
        );

        entrada.value = "";

    } catch (error) {
        mostrarMensaje(
            "Error",
            error.message,
            "error"
        );

    } finally {
        bloquearInterfaz(false);
        entrada.focus();
    }
});


botonNuevaConversacion.addEventListener(
    "click",
    function() {
        if (ocupado) return;

        // La conversación anterior permanece
        // guardada en MongoDB.
        conversacionId = null;

        // Limpiar la pantalla actual.
        conversacion.innerHTML = "";
        entrada.value = "";
        entrada.focus();
    }
);
