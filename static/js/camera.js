document.addEventListener('DOMContentLoaded', function () {
    const video = document.getElementById('video');
    const openBtn = document.getElementById('open-camera');
    const captureBtn = document.getElementById('capture');
    const canvas = document.getElementById('canvas');
    const fotoInput = document.getElementById('foto_base64');

    let stream = null;

    // Se não tiver os elementos na página, não faz nada
    if (!video || !openBtn || !captureBtn || !canvas || !fotoInput) {
        return;
    }

    async function startCamera() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('Seu navegador não suporta acesso à câmera.');
            return;
        }

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: true, // você pode trocar para { facingMode: "user" } se quiser frontal no celular
                audio: false
            });
            video.srcObject = stream;
            await video.play();
        } catch (err) {
            console.error('Erro ao acessar câmera:', err);
            alert(
                'Não foi possível acessar a câmera.\n' +
                'Verifique as permissões do navegador (ícone de cadeado ao lado do endereço) ' +
                'e se está acessando o site via HTTPS.'
            );
        }
    }

    function capturePhoto() {
        if (!stream) {
            alert('Abra a câmera antes de capturar a foto.');
            return;
        }

        const width = 320;
        const height = 240;

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, width, height);

        const dataURL = canvas.toDataURL('image/jpeg');
        fotoInput.value = dataURL;

        alert('Foto capturada com sucesso!');
    }

    openBtn.addEventListener('click', startCamera);
    captureBtn.addEventListener('click', capturePhoto);

    // Para não deixar a câmera ligada se o usuário sair da página
    window.addEventListener('beforeunload', () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });
});
