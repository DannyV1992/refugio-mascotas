const API_BASE = 'http://localhost:8001';
let editingMascotaId = null;
let selectedImage = null;

// Elementos del DOM
const mascotaForm = document.getElementById('mascotaForm');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const cancelBtn = document.getElementById('cancelBtn');
const formTitle = document.getElementById('formTitle');
const imagenInput = document.getElementById('imagenInput');
const uploadArea = document.getElementById('uploadArea');
const uploadContent = document.getElementById('uploadContent');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const removeImageBtn = document.getElementById('removeImage');

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const colors = { success: 'border-green-500', error: 'border-red-500', info: 'border-blue-500' };
    toastIcon.textContent = icons[type];
    toastMessage.textContent = message;
    toast.firstElementChild.className = `bg-white rounded-lg shadow-lg border-l-4 ${colors[type]} p-4 max-w-sm`;
    toast.classList.remove('translate-x-full');
    toast.classList.add('translate-x-0');
    setTimeout(() => {
        toast.classList.remove('translate-x-0');
        toast.classList.add('translate-x-full');
    }, 3000);
}

// Manejo de imágenes
uploadArea.addEventListener('click', () => imagenInput.click());
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageFile(files[0]);
    }
});
function handleImageFile(file) {
    if (file.size > 5 * 1024 * 1024) {
        showToast('La imagen no debe superar los 5MB', 'error');
        return;
    }
    if (!file.type.startsWith('image/')) {
        showToast('Por favor selecciona un archivo de imagen válido', 'error');
        return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
        selectedImage = e.target.result;
        previewImage.src = selectedImage;
        uploadContent.classList.add('hidden');
        previewContainer.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}
removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    selectedImage = null;
    imagenInput.value = '';
    uploadContent.classList.remove('hidden');
    previewContainer.classList.add('hidden');
});

imagenInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleImageFile(e.target.files[0]); // ← CORREGIDO: agregué 
    }
});

// Envío del formulario
mascotaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(mascotaForm);
    let imagen_url = null;

    // 🔥 DEBUG: Verificar si hay archivos
    console.log('🔥 DEBUG: Archivos seleccionados:', imagenInput.files.length);
    if (imagenInput.files.length > 0) {
        console.log('🔥 DEBUG: Archivo:', imagenInput.files[0].name, imagenInput.files.size, 'bytes');
    }

    // PASO 1: SUBIR IMAGEN SI EXISTE
    if (imagenInput.files.length > 0) {
        const imgFormData = new FormData();
        imgFormData.append("file", imagenInput.files[0]); // ✅ CORREGIDO: agregué 
        
        console.log('🔥 DEBUG: Subiendo imagen...');
        try {
            const resp = await fetch(`${API_BASE}/upload-image`, { // ✅ CORREGIDO: usar API_BASE
                method: "POST",
                body: imgFormData
            });
            
            console.log('🔥 DEBUG: Respuesta de upload:', resp.status);
            
            if (!resp.ok) {
                const errorText = await resp.text();
                console.log('❌ ERROR: Error en upload:', errorText);
                showToast("Error al subir imagen: " + resp.status + " - " + errorText, "error");
                return;
            }
            const data = await resp.json();
            imagen_url = data.url;
            console.log('✅ SUCCESS: Imagen subida, URL:', imagen_url);
        } catch (err) {
            console.log('❌ ERROR: JavaScript error en subida:', err);
            showToast("Error JS en subida imagen: " + err, "error");
            return;
        }
    } else {
        console.log('ℹ️ INFO: No hay imagen para subir');
    }

    // PASO 2: PREPARAR DATOS DE MASCOTA
    const mascotaData = {
        nombre: formData.get('nombre'),
        especie: formData.get('especie'),
        edad: formData.get('edad') ? parseInt(formData.get('edad')) : null,
        descripcion: formData.get('descripcion') || '',
        tamano: formData.get('tamano') || null,  // ✅ CORREGIDO: sin n
        genero: formData.get('genero') || null,
        contacto_nombre: formData.get('contacto_nombre') || null,
        contacto_telefono: formData.get('contacto_telefono') || null,
        estado: 'disponible',
        imagen_url: imagen_url
    };

    console.log('🔥 DEBUG: Datos de mascota a enviar:', mascotaData);

    // PASO 3: ENVIAR MASCOTA
    try {
        submitBtn.disabled = true;
        submitText.textContent = 'Registrando...';
        
        const url = editingMascotaId ? `${API_BASE}/mascotas/${editingMascotaId}` : `${API_BASE}/mascotas`;
        const method = editingMascotaId ? 'PUT' : 'POST';
        
        console.log('🔥 DEBUG: Enviando mascota a:', url);
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mascotaData)
        });

        console.log('🔥 DEBUG: Respuesta de mascota:', response.status);

        // Capturar mensajes de error específicos
        if (!response.ok) {
            const errorData = await response.json();
            const errorMessage = errorData.detail || 'Error desconocido';
            console.log('❌ ERROR: Error al guardar mascota:', errorMessage);
            showToast(errorMessage, 'error');
            return; // Salir sin continuar
        }

        // Si llegamos aquí, todo salió bien
        const result = await response.json();
        console.log('✅ SUCCESS: Mascota guardada:', result);
        
        showToast(
            editingMascotaId ?
            '¡Información de la mascota actualizada!' :
            '¡Mascota registrada exitosamente! Pronto aparecerá disponible para adopción.'
        );
        resetForm();
        if (typeof cargarMascotasRecientes === 'function') {
            cargarMascotasRecientes();
        }
        
    } catch (error) {
        console.error('❌ ERROR: Error de conexión:', error);
        showToast('Error de conexión. Por favor intenta de nuevo.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitText.textContent = editingMascotaId ? 'Actualizar Mascota' : 'Registrar en el Refugio';
    }
});

function resetForm() {
    mascotaForm.reset();
    selectedImage = null;
    uploadContent.classList.remove('hidden');
    previewContainer.classList.add('hidden');
    editingMascotaId = null;
    formTitle.textContent = 'Registrar Nueva Mascota';
    submitText.textContent = 'Registrar en el Refugio';
    cancelBtn.classList.add('hidden');
}
// Cargar mascotas recientes
async function cargarMascotasRecientes() {
    try {
        const response = await fetch(`${API_BASE}/mascotas`);
        if (!response.ok) throw new Error('Error al cargar mascotas');
        const mascotas = await response.json();
        const recientes = mascotas.slice(0, 3);
        const container = document.getElementById('mascotasRecientes');
        if (recientes.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">No hay mascotas registradas aún</p>';
            return;
        }
        container.innerHTML = recientes.map(mascota => `
            <div class="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <span class="text-2xl">${mascota.especie === 'perro' ? '🐕' : mascota.especie === 'gato' ? '🐱' : '🐾'}</span>
                <div>
                    <p class="font-medium text-gray-800">${mascota.nombre}</p>
                    <p class="text-sm text-gray-600">${mascota.especie}</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('mascotasRecientes').innerHTML =
            '<p class="text-red-500 text-center text-sm">Error al cargar datos</p>';
    }
}
cancelBtn.addEventListener('click', resetForm);
document.addEventListener('DOMContentLoaded', () => {
    cargarMascotasRecientes();
});
