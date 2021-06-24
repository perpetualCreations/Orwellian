// https://usefulangle.com/post/352/javascript-capture-image-from-camera

async function startCameraPreview() {
    document.getElementById("capture-phase").style.display = "initial";
    document.getElementById("camera-ready").style.display = "none";
    let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    document.getElementById("video-stream-player").srcObject = stream;
}

function collectCamera() {
    let canvas = document.querySelector("#canvas");
    document.getElementById("review-phase").style.display = "initial";
    document.getElementById("capture-phase").style.display = "none";
    canvas.getContext('2d').drawImage(document.getElementById("video-stream-player"), 0, 0, canvas.width, canvas.height);
    dispatchCommand("LOG_IMAGE", "PAYLOAD", canvas.toDataURL('image/jpeg'));
}

function resetCamera() {
    document.getElementById("camera-ready").style.display = "initial";
    document.getElementById("review-phase").style.display = "none";
}
