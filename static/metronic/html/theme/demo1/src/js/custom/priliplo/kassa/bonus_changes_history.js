
var datatable = $('.kt_datatable').DataTable( {
    ordering:  false,
    "dom": '<"top"i>rt<"bottom"flp><"clear">',
    "lengthMenu": [ [50, 100, 500, -1], [50, 100, 500, "Все"] ],
    language: {
        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Russian.json'
    },

} );
// Apply the search
datatable.columns().eq( 0 ).each( function ( colIdx ) {
    $( 'input', datatable.column( colIdx ).header() ).on( 'keyup change', function () {
        if (colIdx !== 0) {
            datatable.column( colIdx ).search( this.value ).draw();
        }
        else {
            datatable.column( colIdx ).draw();
        }
    } );
} );

$(function() {
    $(".datatable_header_search:first").daterangepicker({
    showDropdowns: true,
        autoUpdateInput: false,
    minYear: 2021,
        maxYear: parseInt(moment().format("YYYY"),10),
        locale: {
        format: "DD.MM.YYYY",
            "separator": " - ",
            cancelLabel: 'Очистить',
            "applyLabel": "Применить",
            "fromLabel": "С",
            "toLabel": "По",
            "customRangeLabel": "Произвольный",
            "weekLabel": "Нед",
            "daysOfWeek": [
            "Вс",
            "Пн",
            "Вт",
            "Ср",
            "Чт",
            "Пт",
            "Сб"
        ],
            "monthNames": [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь"
        ],
            "firstDay": 1
    }
},
);

    $('.datatable_header_search:first').change(function(){
        datatable.draw();
    });
    $('.datatable_header_search:first').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY') ).change();
    });
    $('.datatable_header_search:first').on('cancel.daterangepicker', function(ev, picker) {
        $(this).val('').change();
    });

    $.fn.dataTable.ext.search.push(
        function( settings, data, dataIndex ) {
            var date_str = $('.datatable_header_search:first').val();
            var arrayOfDates = date_str.split(" - ");


            var dateFrom = arrayOfDates[0];
            var dateTo = arrayOfDates[1];
            var dateCheckString = data[0] || "";
            var dateCheckArray = dateCheckString.split(" ");
            var dateCheck = dateCheckArray[0];
            if ((dateFrom !== '') && (dateTo !== '')) {
                var d1 = dateFrom.split(".");
                var d2 = dateTo.split(".");
                var c = dateCheck.split(".");

                var from = new Date(d1[2], parseInt(d1[1])-1, d1[0]);  // -1 because months are from 0 to 11
                var to   = new Date(d2[2], parseInt(d2[1])-1, d2[0]);
                var check = new Date(c[2], parseInt(c[1])-1, c[0]);

                if ( ( isNaN( from ) && isNaN( to ) ) ||
                    ( isNaN( from ) && check <= to ) ||
                    ( from <= check && isNaN( to ) ) ||
                    ( from <= check && check <= to ) )
                {
                    return true;
                }
                return false;
            } else {
                return true;
            }
        }
    );

});