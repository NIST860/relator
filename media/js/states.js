$(document).ready(function() {
	$('#options').tabs();

	/*
	tablify($('#states'), {
		aaSorting: [[1, 'asc']],
		aoColumns: [{bSortable: false, sWidth: '20px'}, null, null],
	});
	*/
	tablify($('#standards'), {
		aaSorting: [[1, 'asc']],
		aoColumns: [{bSortable: false, sWidth: '20px'}, null],
		sScrollY: false,
	});

});
