$('.search-select').select2({
    ajax: {
        url: '/get_usuarios',
        dataType: 'json',
        delay: 250,  // Retraso para la búsqueda
        data: function (params) {
            return {
                q: params.term,  // Término de búsqueda
                page: params.page
            };
        },
        processResults: function (data, params) {
            params.page = params.page || 1;
            return {
                results: data.results,
                pagination: {
                    more: (params.page * 30) < data.total_count
                }
            };
        },
        cache: true
    },
    minimumInputLength: 1,  // Mínimo de caracteres para iniciar la búsqueda
});