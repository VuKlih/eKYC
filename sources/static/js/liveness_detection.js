
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

let failCount = 0; // Counter for unsuccessful verification attempts
let count_frame = 0;
let isCorrect = false;
let count_correct = 0; // Count of correct answers
let count_delay_frame = 0;
let challenge, question;
get_challenge_and_question();

document.getElementById('startCamera').addEventListener('click', function() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    // Check if the browser supports getUserMedia
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;

                // Ensure video dimensions are available
                video.addEventListener('loadedmetadata', function() {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    
                    video.play();

                    video.addEventListener('play', function() {
                        const captureFrame = async () => {
                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            if (!isCorrect && count_correct < 3) {
                                updateChallengeLabel(null, question);
                                isCorrect = await liveness_detect();
                            } else if (isCorrect && count_correct < 3) {
                                updateChallengeLabel("Correct!");
                                count_frame += 1;

                                if (count_frame == 100) {
                                    count_correct += 1;
                                    count_frame = 0;
                                    if (count_correct == 3) {
                                        stream.getTracks().forEach(track => track.stop());
                                        Swal.fire({
                                            icon: 'success',
                                            title: 'Success',
                                            text: 'You have successfully established your identity',
                                        });

                                        // Show the "Next" button after extraction is successful
                                        document.getElementById('nextButton').style.display = 'block';

                                    } else {
                                        get_challenge_and_question();
                                        updateChallengeLabel(null, question);
                                        isCorrect = false;
                                    }
                                }
                            }
                        };

                        // Process frames sequentially
                        const processFrames = async () => {
                            await captureFrame();
                            if (count_correct < 3) {
                                requestAnimationFrame(processFrames);
                            }
};

// Start processing frames
processFrames();
                    });
                });
            })
            .catch(error => {
                console.error('Error accessing the camera: ', error);
            });
    } else {
        alert('Your browser does not support camera access.');
    }

    async function liveness_detect() {
        const imgData = canvas.toDataURL('image/jpeg');
        const formData = new FormData();
        formData.append('file', dataURLtoBlob(imgData), 'captured_image.jpg');
        formData.append('challenge', challenge);
        formData.append('question', JSON.stringify(question));

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/liveness_detect', true);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    resolve(true);
                } else {
                    console.log(xhr.responseText);
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

function updateChallengeLabel(text = null, question = null) {
    const label = document.getElementById('liveness-challenge');

    if (text && question) {
        throw new Error('Cannot provide both text and question');
    }
    
    if (text === "Correct!") {
        label.innerHTML = text;
        label.style.color = 'green';
    } else {
        label.style.color = '#006bbb';
    }

    if (text!= null) {
    }
    else if (text != null) {
        label.innerHTML = text;

    } 
    else if (question != null) {
        if (typeof question === 'string') {
            text = `Question ${count_correct + 1}/3: ${question}`;
        } else {
            text = `Question ${count_correct + 1}/3: ${question[0]}`;
        }
        label.innerHTML = text;
    }
}

function randomChallenge() {
    // const challenges = ['blink eyes','right', 'left', 'front', 'smile'];
    const challenges = ['right', 'left', 'front', 'smile'];
    const randomIndex = Math.floor(Math.random() * challenges.length);
    return challenges[randomIndex];
}

function get_question(challenge) {
    if (challenge === 'smile') {
        return `Please put on a ${challenge} expression`;
    } 
    else if (['right', 'left', 'front'].includes(challenge)) {
        return `Please turn your face to the ${challenge}`;
    } 
    else if (challenge === 'blink eyes') {
        const num = Math.floor(Math.random() * (4 - 2 + 1)) + 2;
        return [`Blink your eyes ${num} times`, num];
    }
}

function get_challenge_and_question() {
    challenge = randomChallenge();
    question = get_question(challenge);
}
