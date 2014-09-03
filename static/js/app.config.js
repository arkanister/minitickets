// Calculate nav height
$.fn.hasAttr = function(name) {
   return this.attr(name) !== undefined;
};

$.calc_navbar_height = function() {
    var height = null;

    if ($('#header').length)
        height = $('#header').height();

    if (height === null)
        height = $('<div id="header"></div>').height();

    if (height === null)
        return 49;
    // default
    return height;
};

$.navbar_height = $.calc_navbar_height();

/*
 * APP DOM REFERENCES
 * Description: Obj DOM reference, please try to avoid changing these
 */
$.root_ = $('body');
$.left_panel = $('#left-panel');
$.shortcut_dropdown = $('#shortcut');
$.bread_crumb = $('#ribbon ol.breadcrumb');

$.loaders = {};
$.defaults = {};

$(document).ready(function() {

    var actions = {
        toggleMenu: function(){
	    	if (!$.root_.hasClass("menu-on-top")){
				$('html').toggleClass("hidden-menu-mobile-lock");
				$.root_.toggleClass("hidden-menu");
				$.root_.removeClass("minified");
	    	} else if ( $.root_.hasClass("menu-on-top") && $.root_.hasClass("mobile-view-activated") ) {
	    		$('html').toggleClass("hidden-menu-mobile-lock");
				$.root_.toggleClass("hidden-menu");
				$.root_.removeClass("minified");
	    	}
	    },
        resizeRoot: function() {
            $.root_.css({'min-height': $(window).height() + 'px'});
        }
    };

    $.root_.on('click', '[data-action="toggleMenu"]', function(e) {
		actions.toggleMenu();
		e.preventDefault();
	});

    $(window).resize(function() {
        actions.resizeRoot();
    });

    actions.resizeRoot();

    /==========================================================================================/

    // Loader for Tooltips
    $.loaders['tooltip'] = function() {
        $('[rel=tooltip].top').tooltip({placement: 'top'});
        $('[rel=tooltip].bottom').tooltip({placement: 'bottom'});
        $('[rel=tooltip].right').tooltip({placement: 'right'});
        $('[rel=tooltip].left').tooltip({placement: 'left'});
        $('[rel=tooltip]').tooltip();
    };

    // Loader for popovers
    $.loaders['popover'] = function() {
        $('[rel=popover].top.hover').popover({trigger: 'hover', placement: 'top'});
        $('[rel=popover].bottom.hover').popover({trigger: 'hover', placement: 'bottom'});
        $('[rel=popover].left.hover').popover({trigger: 'hover', placement: 'left'});
        $('[rel=popover].right.hover').popover({trigger: 'hover', placement: 'right'});

        $('[rel=popover].hover').popover({trigger: 'hover', placement: 'top'});

        $('[rel=popover].top').popover({placement: 'top'});
        $('[rel=popover].bottom').popover({placement: 'bottom'});
        $('[rel=popover].left').popover({placement: 'left'});
        $('[rel=popover].right').popover({placement: 'right'});

        $('[rel=popover]').popover();
    };

    // Modal
    $.loaders['modal'] = {
        load: function() {
            var $modal = $('<div>').addClass('modal fade');
            $.root_.append($modal);
            $.defaults['modal'] = $modal;

            $('[rel=modal]').on('click', function(e) {
                var modal = $(this).data('modal'),
                    action = $(this).data('action');

                if (modal == undefined || modal == null)
                    modal = $.defaults.modal;
                else
                    modal = $(modal);

                if (action == undefined || modal == null)
                    action = $(this).attr('href');

                $.ajax({
                    url: action,
                    data: null,
                    headers: {'AJAX_REQUEST_TYPE': 'modal'},
                    method: 'get',
                    beforeSend: function () {
                        modal.html('<center>Loading ...</center>').modal('show');
                    },
                    success: function (data) {
                        modal.html(data);
                    },
                    error: function (data) {
                        modal.html(
                                '<div class="modal-dialog">' +
                                '<div class="modal-content">' +
                                '<div class="modal-body">' +
                                data.responseText +
                                '</div>' +
                                '</div>' +
                                '</div'
                        );
                    }
                });

                e.preventDefault();
            });

        },

        // todo: see you later
        addModal: function(modal) {
            var $modal = $('<div>').addClass('modal fade').attr('id', modal);
            $.root_.append($modal);
        }
    };

    // Masks
    $.loaders['inputMask'] = {
        _getDataOptions: function(input) {
            opts = {};
            if (input.hasAttr('data-reverse') == 1)
                opts['reverse'] = input.data('reverse') == 1;
            if (input.hasAttr('data-clearifnotmatch'))
                opts['clearIfNotMatch'] = input.data('clearifnotmatch') == 1;
            return opts
        },
        _getElement: function(name) {
            return $('[data-input-mask='+ name +'], .input-mask-' + name);
        },
        cep: function() {
            var input = this._getElement('cep');
            input.attr('placeholder', '99999-99')
                .mask('99999-999', this._getDataOptions(input));
            return input;
        },
        telefone: function(){
            var input = this._getElement('telefone');
                input.attr('placeholder', '(99)9999-9999')
                    .mask('(99)9999-9999', this._getDataOptions(input));
            return input;
        },
        cnpj: function() {
            var input = this._getElement('cnpj');
            input.attr('placeholder', '999.999.999/9999-99')
                .mask('999.999.999/9999-99', this._getDataOptions(input));
            return input;
        },
        cpf: function() {
            var input = this._getElement('cpf');
            input.attr('placeholder', '999.999.999-99')
                .mask('999.999.999-99', this._getDataOptions(input));
            return input;
        },

        all: function() {
            this.cep(); this.telefone();this.cnpj(); this.cpf();
        }
    }

});