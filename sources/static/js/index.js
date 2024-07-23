const dropArea = document.getElementById('drop-area');
const inputFile  = document.getElementById('input-file');
const imgView = document.getElementById('img-view');
const btn_extract = document.querySelector('.btn.btn-primary');

let file;
let dataExtracted;

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
}
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


// content part
inputFile.addEventListener('change',uploadImage);

function uploadImage(){
    file = inputFile.files[0];
    console.log(file)
    if (inputFile.files && inputFile.files[0]) {
        let imgLink = URL.createObjectURL(inputFile.files[0]);
        console.log(imgLink)
        imgView.style.backgroundImage = `url("${imgLink}")`;
        imgView.textContent = "";
        imgView.style.border = 0;
    } else {
        console.error("No file selected or file input is invalid.");
    }
}

dropArea.addEventListener("dragover",function(e){
    e.preventDefault();
});

dropArea.addEventListener("drop",function(e){
    e.preventDefault();
    inputFile.files = e.dataTransfer.files;
    uploadImage();
});

function file_validation(){
  if (file == 'wrong_exts'){
    const URL = '/uploader';
    const formData = new FormData();
    var f = new File([""], "WRONG_EXTS"); // Empty file trick
    formData.append('file', f);
    xhr.open('POST', URL, true);
    xhr.send(formData);
  }
}

btn_extract.addEventListener("click", function(e) {
  e.preventDefault();
  const formData = new FormData();

  if (file == null){
    var f = new File([""], "NULL"); // Empty file trick
    formData.append('file', f);
  }
  else{
    formData.append('file', file);
  }
  
  const URL = '/uploader';
  xhr.open('POST', URL, true);
  xhr.send(formData);
});

const xhr = new XMLHttpRequest();
xhr.onreadystatechange = function(e) {
  e.preventDefault();

  if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
    const data = JSON.parse(xhr.responseText).data;
    const update =  new Date();
    document.querySelector('.person__img').innerHTML = `<img src="/static/images_collected/id_card_parts/0.jpg?v=${update.getTime()}" />`; // To update avoid using image from cache
    document.querySelector('.info__id input').value = data[0];
    document.querySelector('.info__name input').value = data[1];

    // Split the date to match the input[type="date"] format
    const [day, month, year] = data[2].split('/');
    const formattedDate = `${year}-${month}-${day}`;    
    document.querySelector('.info__date input').value = formattedDate;

    document.querySelector('.info__sex select').value = data[3];
    document.querySelector('.info__nation input').value = data[4];
    document.querySelector('.info__hometown input').value = data[5];
    document.querySelector('.info__address input').value = data[6];

    // Split the expiry date to match the input[type="date"] format if required
    const [expDay, expMonth, expYear] = data[7].split('/');
    const formattedExpDate = `${expYear}-${expMonth}-${expDay}`;
    document.querySelector('.info__doe input').value = formattedExpDate;    
    
    dataExtracted = {
      id: data[0],
      name: data[1],
      date_of_birth: data[2],
      sex: data[3],
      nationality: data[4],
      hometown: `"${data[5]}"`,
      address: `"${data[6]}"`,
      date_of_expiry: data[7]
    };
    
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Extract successfully!',
      footer: `CODE: ${xhr.status}`
    })

    // Show the "Next" button after extraction is successful
    document.getElementById('nextButton').style.display = 'block';


  }
  else if (xhr.status >= 400 && xhr.status <= 500){
    const data = JSON.parse(xhr.responseText);
    loading_off();
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: String(data.message),
      footer: `CODE: ${xhr.status}`
    })
  }
}

document.getElementById('nextButton').addEventListener('click', function() {
  // Collect the form data
  const dataExtracted = {
      id: document.querySelector('.info__id input').value,
      name: document.querySelector('.info__name input').value,
      date_of_birth: document.querySelector('.info__date input').value,
      sex: document.querySelector('.info__sex select').value,
      nationality: document.querySelector('.info__nation input').value,
      hometown: document.querySelector('.info__hometown input').value,
      address: document.querySelector('.info__address input').value,
      date_of_expiry: document.querySelector('.info__doe input').value
  };

  // Make an API call to update the data
  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/correct_id_infor", true);

  // Define what happens on successful data submission
  xhr.onload = function () {
      if (xhr.status === 200) {
          // Redirect to /verification page
          if (dataExtracted != null){
            window.location.href = "/verification";
          }
      } else {
          console.error('Error:', xhr.statusText);
      }
  };

  // Define what happens in case of error
  xhr.onerror = function () {
      console.error('Request failed');
  };

  // Send the request with the data
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify(dataExtracted));
  console.log(JSON.stringify(dataExtracted))
});


