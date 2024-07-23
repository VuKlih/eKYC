const previousPage_btn = document.querySelector('.previousPage');
const nextPage_btn = document.querySelector('.nextButton');


// ---------Responsive-navbar-active-animation-----------
function test(){
	var tabsNewAnim = $('#navbarSupportedContent');
	var selectorNewAnim = $('#navbarSupportedContent').find('li').length;
	var activeItemNewAnim = tabsNewAnim.find('.active');
	var activeWidthNewAnimHeight = activeItemNewAnim.innerHeight();
	var activeWidthNewAnimWidth = activeItemNewAnim.innerWidth();
	var itemPosNewAnimTop = activeItemNewAnim.position();
	var itemPosNewAnimLeft = activeItemNewAnim.position();
	$(".hori-selector").css({
		"top":itemPosNewAnimTop.top + "px", 
		"left":itemPosNewAnimLeft.left + "px",
		"height": activeWidthNewAnimHeight + "px",
		"width": activeWidthNewAnimWidth + "px"
	});
	$("#navbarSupportedContent").on("click","li",function(e){
		$('#navbarSupportedContent ul li').removeClass("active");
		$(this).addClass('active');
		var activeWidthNewAnimHeight = $(this).innerHeight();
		var activeWidthNewAnimWidth = $(this).innerWidth();
		var itemPosNewAnimTop = $(this).position();
		var itemPosNewAnimLeft = $(this).position();
		$(".hori-selector").css({
			"top":itemPosNewAnimTop.top + "px", 
			"left":itemPosNewAnimLeft.left + "px",
			"height": activeWidthNewAnimHeight + "px",
			"width": activeWidthNewAnimWidth + "px"
		});
	});
};
$(document).ready(function(){
	setTimeout(function(){ test(); });
});
$(window).on('resize', function(){
	setTimeout(function(){ test(); }, 500);
});
$(".navbar-toggler").click(function(){
	$(".navbar-collapse").slideToggle(300);
	setTimeout(function(){ test(); });
});

// --------------add active class-on another-page move----------
jQuery(document).ready(function($){
	// Get current path and find target link
	var path = window.location.pathname.split("/").pop();

	// Account for home page with empty path
	if ( path == '' ) {
		path = 'index.html';
	}

	var target = $('#navbarSupportedContent ul li a[href="'+path+'"]');
	// Add active class to target link
	target.parent().addClass('active');
});

// -------------- content part----------
document.getElementById('startCamera').addEventListener('click', function() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    let frameCount = 0;
    let failCount = 0; // Counter for unsuccessful verification attempts

    // Check if the browser supports getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;

                video.addEventListener('play', function() {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;

                    const captureFrame = async () => {
                        if (frameCount < 50) {
                            frameCount++;
                            requestAnimationFrame(captureFrame);
                        } else {
                            frameCount = 0; // Reset frame count after 50 frames
                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            let verify = await face_verify();
                            if (!verify) {
                                failCount++;
                                if (failCount == 5 ) {
                                    console.error('Verification failed 5 times. Stopping camera.');
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Oops...',
                                        text: 'Verification failed 5 times, you are not the same person in the ID card!',
                                    })
                                    stream.getTracks().forEach(track => track.stop());
                                    return
                                }
                            } 
                            else {
                                console.log('Verification successful. Stopping camera.');
                                stream.getTracks().forEach(track => track.stop());
                                document.getElementById('nextButton').style.display = 'block';
                                return
                            }
                            // Continue capturing frames if the verification is not successful 5 times yet
                            requestAnimationFrame(captureFrame);
                        }
                    };
                    captureFrame();
                });
            })
            .catch(error => {
                console.error('Error accessing the camera: ', error);
            });
    } else {
        alert('Your browser does not support camera access.');
        cameraStarted = false; // Reset the cameraStarted flag if the browser does not support camera access
    }

    async function face_verify() {
        const imgData = canvas.toDataURL('image/jpeg');
        const formData = new FormData();
        formData.append('file', dataURLtoBlob(imgData), 'captured_image.jpg');

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/verify-face', true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: 'Face verification successfully!',
                        // footer: `CODE: ${xhr.status}`
                    })                    
                      // Show the "Next" button after extraction is successful
                    resolve(true);
                } else {

                    console.log('Failed to verify')
                    resolve(false);
                }
            };
            xhr.onerror = () => reject(new Error('Network error'));
            xhr.send(formData);
        });
    }

    function dataURLtoBlob(dataurl) {
        const arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
        for (let i = 0; i < n; i++) {
            u8arr[i] = bstr.charCodeAt(i);
        }
        return new Blob([u8arr], { type: mime });
    }

});