/*
Template Name: Color Admin - Responsive Admin Dashboard Template build with Twitter Bootstrap 4
Version: 4.6.0
Author: Sean Ngu
Website: http://www.seantheme.com/color-admin/admin/
*/

// IE8 browser support
if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function(elt /*, from*/) {
    	var len = this.length >>> 0;
    	var from = Number(arguments[1]) || 0;
    	from = (from < 0) ? Math.ceil(from) : Math.floor(from);
    	if (from < 0)
      		from += len;

    	for (; from < len; from++) {
      		if (from in this && this[from] === elt)
        		return from;
    	}
    	return -1;
	};
}
if(typeof String.prototype.trim !== 'function') {
	String.prototype.trim = function() {
		return this.replace(/^\s+|\s+$/g, ''); 
	}
}


var handleDatepicker = function() {
	$('#datepicker-default').datepicker({
		todayHighlight: true
	});
	$('#datepicker-inline').datepicker({
		todayHighlight: true
	});
	$('.input-daterange').datepicker({
		todayHighlight: true
	});
	$('#datepicker-disabled-past').datepicker({
		todayHighlight: true
	});
	$('#datepicker-autoClose').datepicker({
		todayHighlight: true,
		autoclose: true
	});
};

var handleFormMaskedInput = function() {
	"use strict";
	$("#masked-input-date").mask("9999-99-99");
	$("#masked-input-phone").mask("(99) 999-99-99");
	$("#masked-input-tid").mask("99-9999999");
	$("#masked-input-ssn").mask("999-99-9999");
	$("#masked-input-pno").mask("aaa-9999-a");
	$("#masked-input-pkey").mask("a*-999-a999");
	$("#masked-input-passport").mask("aa 9999999");
	$("#masked-input-jshshr").mask("99999999999999");
};

var handleFormTimePicker = function () {
	"use strict";
	$('#timepicker').timepicker();
};

var handleTagsInput = function() {
	$('.bootstrap-tagsinput input').focus(function() {
		$(this).closest('.bootstrap-tagsinput').addClass('bootstrap-tagsinput-focus');
	});
	$('.bootstrap-tagsinput input').focusout(function() {
		$(this).closest('.bootstrap-tagsinput').removeClass('bootstrap-tagsinput-focus');
	});
};

var handleSelectpicker = function() {
	$('.selectpicker').selectpicker('render');
};

var handleSelect2 = function() {
	$(".default-select2").select2();
	$(".multiple-select2").select2({ placeholder: "Select a state" });
};

var handleDateTimePicker = function() {
	$('#datetimepicker1').datetimepicker();
	$('#datetimepicker2').datetimepicker({
		format: 'LT'
	});
	$('#datetimepicker3').datetimepicker();
	$('#datetimepicker4').datetimepicker();
	$("#datetimepicker3").on("dp.change", function (e) {
		$('#datetimepicker4').data("DateTimePicker").minDate(e.date);
	});
	$("#datetimepicker4").on("dp.change", function (e) {
		$('#datetimepicker3').data("DateTimePicker").maxDate(e.date);
	});
};


var FormPlugins = function () {
	"use strict";
	return {
		init: function () {
			handleDatepicker();
			handleFormMaskedInput();
			handleFormTimePicker();
			handleSelect2();
			handleSelectpicker();
			handleTagsInput();
			handleDateTimePicker();
		}
	};
}();

$(document).ready(function() {
	FormPlugins.init();
});