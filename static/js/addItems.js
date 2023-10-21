
var api = apiUrl;

$(document).ready(function () {
    $(document).on('click', '.add-item', function () {
        var form = $(this).closest('form');
        var product = form.find('input[name="product"]').val();
        var quantity = form.find('input[name="quantity"]').val();
        var csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        var apiUrl = apiUrl;

        $.ajax({
            type: 'POST',
            url: apiUrl,
            data: {
                invoice: invoice_pk,
                product: product,
                quantity: quantity,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function (response) {
                populateTable(apiUrl);
                // Add code here to update the page as needed, e.g., displaying the newly added item
            }
        });
    });
});

function populateTable(apiUrl) {
    var csrfToken = crsfToken;
    $.ajax({
        type: 'GET',
        url: apiUrl,
        success: function (data) {
            // Remove all console.log statements
            // Add code here to update the page as needed
        }
    });
}