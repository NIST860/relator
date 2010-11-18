function recount(wrapper) {
	var length = $('tbody tr', wrapper).length;
	var selected = $('tbody tr.ui-selected', wrapper).length;
	$('.selection_info', wrapper).html(selected + ' of ' + length + ' selected');
};

function select() {
	if(!$(this).length) return;
	$(this).addClass('ui-selected');
	$('.select :checkbox', this).attr('checked', true);
	var wrapper = $(this).parents('.dataTables_wrapper');
	$('.selectall :checkbox', wrapper).attr('checked', true);
	$('.continuer', wrapper).button('option', 'disabled', false);
	recount(wrapper);
};

function deselect() {
	if(!$(this).length) return;
	$(this).removeClass('ui-selected');
	$('.select :checkbox', this).removeAttr('checked');
	if(!$(this).parents('tbody').find('.select :checked').length) {
		var wrapper = $(this).parents('.dataTables_wrapper');
		$('.selectall :checkbox', wrapper).removeAttr('checked');
		$('.continuer', wrapper).button('option', 'disabled', true);
	};
	recount(wrapper);
};

function toggle() {
	if($(this).hasClass('ui-selected')) deselect.apply(this);
	else select.apply(this);
};

function setDefault(obj, other) {
	for(var i in other) if(obj[i] === undefined) obj[i] = other[i];
	return obj;
};

function tablify(container, options) {
	var wrapper = $('.dataTables_wrapper', container);
	options = setDefault(options || {}, {
		bJQueryUI: true,
		bPaginate: false,
		sScrollY: '400px',
		bStateSave: true,
	});

	$('table.main', container).dataTable(options);
	$('.selectall :checkbox', container).click(function() {
		if($(this).attr('checked')) select.apply($('tbody tr', container));
		else deselect.apply($('tbody tr', container));
	});
	$('tbody tr', container).click(toggle);
	$('.options', container).prependTo($('.fg-toolbar:first', container));
	$('.continue', container).appendTo($('.fg-toolbar:last', container));
	$('.extra button', container).button();
	$('.dataTables_info', container).hide().after('<div class="selection_info"></div>');
	recount(container);
	$('tbody tr .select :checked', container).each(function() {
		select.apply($(this).parents('tr'));
	});
};
