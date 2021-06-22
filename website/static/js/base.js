$(function() {
    $('nav a[href^="/' + location.pathname.split("/")[1] + '"]').addClass('active');
    navbar_height = document.querySelector('.navbar').offsetHeight;
    document.body.style.paddingTop = navbar_height + 'px';
});