$(document).ready(function() {
    /* window force height */
    var force_height = function() { $('body').css({'min-height': $(window).height() + 'px'}); };
    $(window).resize(function() {force_height();});
    force_height();
});