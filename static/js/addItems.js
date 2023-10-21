console.log(invoice_pk);
console.log(site_url);





    
$(document).ready(function () {
    $(document).on('click', '.add-item', function () {
        var form = $(this).closest('form');  // You can update this with the appropriate invoice value
        var product = form.find('input[name="product"]').val();
        var quantity = form.find('input[name="quantity"]').val();
        var csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        var apiUrl = form.data('url');  // Access the URL from the data-url attribute

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
                // Add code here to update the page as needed, e.g., displaying the newly added item
            }
        });
    });
});
