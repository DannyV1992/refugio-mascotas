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
imagenInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleImageFile(e.target.files); // CORRECTO: solo pasas el primer archivo
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

// Envío del formulario (implementando el "test que funciona")
mascotaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(mascotaForm);
    let imagen_url = null;

    // --- CLAVE: SOLO INTENTA LA SUBIDA SI HAY ARCHIVO! ---
    if (imagenInput.files.length > 0) {
        const imgFormData = new FormData();
        imgFormData.append("file", imagenInput.files[0]);
        try {
            const resp = await fetch("http://localhost:8001/upload-image", {
                method: "POST",
                body: imgFormData
            });
            if (!resp.ok) {
                showToast("Error al subir la imagen: " + resp.status, "error");
                return;
            }
            const data = await resp.json();
            imagen_url = data.url;
        } catch (err) {
            showToast("Error JS en subida de imagen: " + err, "error");
            return;
        }
    }

    const mascotaData = {
        nombre: formData.get('nombre'),
        especie: formData.get('especie'),
        edad: formData.get('edad') ? parseInt(formData.get('edad')) : null,
        descripcion: formData.get('descripcion') || '',
        tamaño: formData.get('tamaño') || null,
        genero: formData.get('genero') || null,
        contacto_nombre: formData.get('contacto_nombre') || null,
        contacto_telefono: formData.get('contacto_telefono') || null,
        estado: 'disponible',
        imagen_url: imagen_url
    };

    try {
        submitBtn.disabled = true;
        submitText.textContent = 'Registrando...';
        const url = editingMascotaId ? `${API_BASE}/mascotas/${editingMascotaId}` : `${API_BASE}/mascotas`;
        const method = editingMascotaId ? 'PUT' : 'POST';
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mascotaData)
        });
        if (!response.ok) throw new Error('Error en el servidor');
        showToast(
            editingMascotaId ?
            '¡Información de la mascota actualizada!' :
            '¡Mascota registrada exitosamente! Pronto aparecerá disponible para adopción.'
        );
        resetForm();
        cargarMascotasRecientes();
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al registrar la mascota. Por favor intenta de nuevo.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitText.textContent = 'Registrar en el Refugio';
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
