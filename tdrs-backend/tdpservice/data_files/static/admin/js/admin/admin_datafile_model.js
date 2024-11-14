$(window).on('load', function() {
    console.log('loaded');
    var submitBtn=document.querySelector('button[type=submit]');    // add the first listener
    var theForm = submitBtn.parentNode.parentNode;
    var action = "";
    var number_of_files_line = "";

    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        for (var i = 0; i < theForm.childNodes.length; i++) {
          if (theForm.childNodes[i].className === "actions") {
            form_header = theForm.childNodes[i];
            for (var i = 0; i < form_header.childNodes.length; i++) {
                if (form_header.childNodes[i].nodeName === "LABEL") {
                  var select_node = form_header.childNodes[i].childNodes[1];
                  if (select_node.value === "reparse") { // action is reparse
                    action = select_node.value;
                  }
                }
                if (form_header.childNodes[i].className == "action-counter" || form_header.childNodes[i].className == "all") {
                  number_of_files_line = form_header.childNodes[i];
                  break;
                }
              }
  
            break;
          }
        }
        if (action === "reparse") {
          console.log('reparse');
          var splitted_number_of_files = number_of_files_line.innerHTML.split(/(\s+)/);
          if (Number(splitted_number_of_files[0]) > 0 ) {
            number_of_files = splitted_number_of_files[0];
          } else {
            number_of_files = splitted_number_of_files[2];
          }
          if (confirm("You are about to re-parse " + number_of_files + " files. Are you sure you want to continue?")) {
              console.log('submitting');
              theForm.submit();
          } else {
              console.log('not submitting');
          };
        } else {
          console.log('not reparse');
        }
    });

});
