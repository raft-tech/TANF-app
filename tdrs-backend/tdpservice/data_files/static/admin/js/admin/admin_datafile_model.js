$(window).on('load', function() {
    //your code here
    console.log('loaded');
    var submitBtn=document.querySelector('button[type=submit]');    // add the first listener
    var theForm = submitBtn.parentNode.parentNode;

    for (var i = 0; i < theForm.childNodes.length; i++) {
        console.log(theForm.childNodes[i].className)
        if (theForm.childNodes[i].className == "actions") {
          form_header = theForm.childNodes[i];
          break;
        }        
    }
    for (var i = 0; i < form_header.childNodes.length; i++) {
        console.log(form_header.childNodes[i].className)
        if (form_header.childNodes[i].className == "action-counter") {
          number_of_files = form_header.childNodes[i];
          break;
        }        
    }
    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        disableFields();
        if (confirm("You are about to re-parse " + number_of_files.innerHTML.split(/(\s+)/)[0] + " files. Are you sure you want to continue?")) {
            console.log('submitting');
            theForm.submit();
        } else {
            console.log('not submitting');
        };
    });

    
});
