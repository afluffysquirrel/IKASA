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
});

/*
function search_redirect() {
    window.location.href += '?search='+document.getElementById("search").value;
}
document.getElementById("search_button").addEventListener("click", search_redirect);
*/