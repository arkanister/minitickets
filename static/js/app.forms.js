$(function () {

    // load masks
    $.loaders.mask.all();

    // form group addon fix prepend class
    $(':input').on('focus focusout', function () {
        $(this).parent().find('.input-group-addon').toggleClass('focus');
        $(this).parent().find('.icon-prepend, .icon-append').toggleClass('focus');
        $(this).parent().parent().find('.input-icon-left i, .input-icon-right i').toggleClass('focus');
    });

    // checkbox and radio button fix
    $('input.checkbox[type="checkbox"], input.radiobox[type="radio"]').on('focus focusout', function() {
       $(this).parent().toggleClass('focus');
    });

});