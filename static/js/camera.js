document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('capture');
    const canvas = document.getElementById('canvas');
    const fotoInput = document.getElementById('foto_base64');

    if (!video || !captureBtn || !canvas || !fotoInput) return;

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                video.play();
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });
}

    camptureBtn.addEventListener('click', function() {
        const width = 320;
        const height = 240;
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, width, height);
        const dataURL = canvas.toDataURL('image/jpeg');
        fotoInput.value = dataURL;
        alert('Photo captured!');
    });
});
