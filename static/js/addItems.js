console.log(invoice_pk);
console.log(site_url);
console.log(apiUrl);

var api = apiUrl
console.log(api)


$(document).ready(function () {
    $(document).on('click', '.add-item', function () {
        var form = $(this).closest('form');  // You can update this with the appropriate invoice value
        var product = form.find('input[name="product"]').val();
        var quantity = form.find('input[name="quantity"]').val();
        var csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        var apiUrl = apiUrl;  // Access the URL from the data-url attribute

        $.ajax({
            type: 'POST',
            url: apiUrl,  // Use the dynamically generated URL
            data: {
                invoice: invoice_pk,
                product: product,
                quantity: quantity,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function () {
                populateTable(apiUrl)
                // Add code here to update the page as needed, e.g., displaying the newly added item
            }
        });
    });
});


function populateTable(api) { // Replace with the correct URL
    var csrfToken = crsfToken; // Replace with the correct CSRF token
    $.ajax({
        type: 'GET',
        url: apiUrl,
        success: function (data) {
            console.log(data); // Log the response directly
        }
    });
}