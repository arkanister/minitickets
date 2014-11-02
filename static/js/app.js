$(function () {

    $.loaders.tooltip();
    $.loaders.popover();

    // MODAL
    $.loaders.modal.load();

    // popover click in everywhere hide
    $('body').on('click', function (e) {
		var $popover = $("[rel=popover]");
		$popover.each(function () {
			if (!$(this).is(e.target) && !$(this).find(e.target).is($(this).find("i")) && $('.popover').has(e.target).length === 0)
	        	$popover.popover('hide');
    	});
	});

});