// get current form by id
/*
$('button[type="submit"]').submit(function() {
    //this.submit();
    console.log('submitting');
    disableFields(); // your own function
    return false;
});
*/

$(window).on('load', function() {
    //your code here
    console.log('loaded');
    var S=document.querySelector('button[type=submit]');
    console.log(S);
    // add the first listener
    var theForm = S.parentNode.parentNode;
    console.log(theForm);
    S.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('submitting');
        disableFields(); // your own function
        e.preventDefault();
        
        alert("Ensure you input a value in both fields!");
        theForm.submit(); //this is working
    });

    
});


disableFields = function() {
    console.log('disabling fields');
}

