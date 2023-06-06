
const BoxMaker = {

	MM_PER_INCH: 25.4,
	MAX_DECIMAL_PLACES: 5,

	init: function() {
		BoxMaker._currentUnit =  BoxMaker._getUnit();
	    $('.bm-btn-popover').popover({'placement':'bottom','trigger':'hover'});
	    // setup event handles
	    $('#bm-units').change(BoxMaker.handleUnitChange);
	    $('#bm-material_thickness').change(BoxMaker.updateNotchLength);
	    $('#bm-auto').change(BoxMaker.updateNotchLength);
	    // populate UI elements
		BoxMaker.updateNotchLength();
	    $('#BoxWidth').focus();
	},

	_getUnit: () => $('#bm-units').val(),

	alert: str => alert(str),

	handleUnitChange: () => BoxMaker.debug("change units to " + $('#bm-units').val()),

	_useAutoNotchLength: () => ($('#bm-auto').is(':checked')),

	_setNotchLength: value => $('#bm-notch_length').val( BoxMaker._roundNumber(value,BoxMaker.MAX_DECIMAL_PLACES) ),

	_getMaterialWidth: () => $('#bm-material_thickness').val(),

	_roundNumber: (num, dec)  => Math.round(num*Math.pow(10,dec))/Math.pow(10,dec),

	_hasMaterialWidth: () => BoxMaker._getMaterialWidth().length != 0,

	_millimetersToUnits: function(value){
		switch (BoxMaker._getUnit()) {
			case "in":
				return value / BoxMaker.MM_PER_INCH;
				break;
			case "mm":
				return value;
				break;
			case "cm":
				return value / 10;
				break;
		}
		BoxMaker.alert("Uknown unit - can't from millimeters to it");
		return 0;
	},

	_unitsToMillimeters: function(value) {
		switch(BoxMaker._getUnit()){
			case "in":
			    return value*BoxMaker.MM_PER_INCH;
	            break;
	        case "mm":
	            return value;
	            break;
	        case "cm":
			    return value*10;
	            break;
		}
		BoxMaker.alert("Uknown unit - can't convert it to millimeters");
		return 0;
	},

	updateNotchLength: function() {
		BoxMaker.debug("updateNotchLength");
	    if (!BoxMaker._useAutoNotchLength()) return;
		if (!BoxMaker._hasMaterialWidth()) return;
		mmWidth = BoxMaker._unitsToMillimeters( BoxMaker._getMaterialWidth() );
		notchLength = mmWidth * 2.5;
		BoxMaker._setNotchLength( BoxMaker._millimetersToUnits(notchLength) );
	},

	debug: (str) => {
		//console.log("BM: "+str);
	}

};
