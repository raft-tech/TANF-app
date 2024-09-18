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


reparseFiles = function() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            alert(xhr.response);
        }
    }
    xhr.open('POST', '/v1/data_files/run_action_reparse_cmd/', false);
    xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    formData = new FormData();
    formData.append('file_ids', '{{ file_ids }}');
    data = {'file_ids': '{{ file_ids }}'};
    console.log(xhr)
    xhr.send(JSON.stringify(data));
}

/*
<script>
    function submit() {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                alert(xhr.response);
            }
        }
        xhr.open('POST', '/v1/data_files/run_action_reparse_cmd/', false);
        xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        formData = new FormData();
        formData.append('file_ids', '{{ file_ids }}');
        data = {'file_ids': '{{ file_ids }}'};
        console.log(xhr)
        xhr.send(JSON.stringify(data));
    }
</script>
*/
