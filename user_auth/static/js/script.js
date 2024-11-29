$("form").submit(
    function(event) {
        event.preventDefault();

        let url = $(this).attr('action');
        let method = $(this).attr('method');
        let formData = $(this).serialize();

        $.ajax({
            url,
            type: method,
            data: formData,
            success: function (response) {
                console.log(response);
            }
        })
    }
)