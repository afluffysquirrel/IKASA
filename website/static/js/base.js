$(function() {
    $('nav a[href^="/' + location.pathname.split("/")[1] + '"]').addClass('active');
    navbar_height = document.querySelector('.navbar').offsetHeight;
    document.body.style.paddingTop = navbar_height + 'px';

    if(location.pathname.split("/")[1] == "articles" || location.pathname.split("/")[1] == "tickets"){
        document.getElementById('search').style.visibility='visible';
    } else 
    {
        document.getElementById('search').style.visibility='hidden';
    }
    setInterval(function() {
        if(document.getElementById('title').value.length == 0 || document.getElementById('tags').value.length == 0){
            document.getElementById('submit-btn').disabled = true;
        }
        else {
            document.getElementById('submit-btn').disabled = false;
        }
    }, 1000); // Wait 1000ms before running again
});