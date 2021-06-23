// https://usefulangle.com/post/352/javascript-capture-image-from-camera

let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let click_button = document.querySelector("#click-photo");
let canvas = document.querySelector("#canvas");

camera_button.addEventListener('click', async function() {
    document.getElementById("capture-phase").style.display = "initial";
    document.getElementById("start-camera").style.display = "none";
   	let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	video.srcObject = stream;
});

click_button.addEventListener('click', function() {
    document.getElementById("review-phase").style.display = "initial";
    document.getElementById("capture-phase").style.display = "none";
   	canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
   	dispatchCommand("LOG_IMAGE", "PAYLOAD", canvas.toDataURL('image/jpeg'));
});

document.getElementById("camera-reset").addEventListener('click', function() {
    document.getElementById("start-camera").style.display = "initial";
    document.getElementById("review-phase").style.display = "none";
})
