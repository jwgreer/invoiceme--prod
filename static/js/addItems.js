
var api = apiUrl;



/*
No longer needed afer fixing cors issue

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
            // Add code here to update the page as needed
        }
    });
}
*/

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];
    return cookieValue;
}

function postInvoiceData(invoice, product, quantity) {
    console.log(product)
    console.log(quantity)
    const apiUrl = site_url+ '/invoice/api/itemInvoice/' + invoice_pk + '/';
    const postData = {
        invoice: invoice_pk,
        product: product,
        quantity: quantity,
    };

    return fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(postData),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('POST request failed');
        }
    });
}

function callProductApi(productId) {
    const apiUrl = site_url +'/invoice/api/productsID/' + productId + '/';

    return fetch(apiUrl, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Include the CSRF token in the request headers if needed
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('GET request failed');
        }
    });
}


function getInvoiceData() {// Replace with the actual Django template variable

    const table = document.getElementById('item-table');
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    const apiUrl = site_url +'/invoice/api/itemInvoice/' + invoice_pk + '/';


    fetch(apiUrl, {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('GET request failed');
        }
    })
    .then(data => {
        data.forEach(item => {
            const row = table.insertRow();
            const invoiceCell = row.insertCell(0);
            const productCell = row.insertCell(1);
            const quantityCell = row.insertCell(2);
            const editCell = row.insertCell(3);
            const deleteCell = row.insertCell(4);
            const idCell = row.insertCell(5);


            // Call the callProductApi function for each item
            callProductApi(item.product).then(productData => {
                // Populate the cells with product data
                invoiceCell.textContent = productData.name;
                productCell.textContent = productData.price;
                quantityCell.textContent = item.quantity;
                idCell.textContent = item.id;

                // Hide the 5th cell with the ID
                idCell.hidden = true;
                id = item.id
                const editLink = document.createElement('a');
                editLink.href = site_url+'/editInvoiceItem/' + invoice_pk + '/' +id + '/';
                editLink.onclick = function() {
                    return confirm('Are you sure you want to edit?');
                };
                editLink.textContent = 'Edit';
                editCell.appendChild(editLink);
                const deleteLink = document.createElement('a');
                deleteLink.className = "delete-button";
                deleteLink.href = "#";
                deleteLink.onclick = function() {
                    return confirm('Are you sure you want to delete?');
                };
                deleteLink.textContent = 'Delete';
                deleteCell.appendChild(deleteLink);
            });
        });
    })
    .catch(error => console.error('Error:', error));
}



function getNewestItem(invoice_pk) {
    const apiUrl = site_url + '/invoice/api/newestProduct/' + invoice_pk + '/';
    const headers = new Headers({
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
    });

    return fetch(apiUrl, {
        method: 'GET',
        headers: headers,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('GET request failed');
        }
    })
    .then(data => {
        if (data.length > 0) {
            const firstItem = data[0];
            const productId = firstItem.product;
            const quantity = firstItem.quantity;
            const id = firstItem.id;
            return callProductApi(productId)
                .then(productData => {
                    const newestItem = {
                        name: productData.name,
                        price: productData.price,
                        quantity: quantity,
                        id: id
                    };
                    return newestItem;
                });
        } else {
            throw new Error('No data found in the response.');
        }
    });
}

function getNewestItemAndAddToTable() {
    // Replace 'invoice' with the actual invoice ID
    getNewestItem(invoice_pk).then(newestItem => {
        const table = document.getElementById('item-table');
        const row = table.insertRow(); // Insert a new row at the end of the table
        const invoiceCell = row.insertCell(0);
        const productCell = row.insertCell(1);
        const quantityCell = row.insertCell(2);
        const editCell = row.insertCell(3);
        const deleteCell = row.insertCell(4);
        const idCell = row.insertCell(5);

        // Add content to visible cells
        invoiceCell.textContent = newestItem.name;
        productCell.textContent = newestItem.price;
        quantityCell.textContent = newestItem.quantity;


        // Set a value for the hidden cell with the ID
        idCell.textContent = newestItem.id;

        // Hide the 5th cell with the ID
        idCell.hidden = true;

        // Create edit and delete links as before
        const editLink = document.createElement('a');
        editLink.href = site_url+'/invoice/api/editInvoiceItem/'+invoice_pk+'/'+newestItem.id+'/';
        editLink.onclick = function() {
            return confirm('Are you sure you want to edit?');
        };
        editLink.textContent = 'Edit';
        editCell.appendChild(editLink);

        const deleteLink = document.createElement('a');
        deleteLink.className = "delete-button";
        deleteLink.href = "#";
        deleteLink.onclick = function() {
            return confirm('Are you sure you want to delete?');
        };
        deleteLink.textContent = 'Delete';
        deleteCell.appendChild(deleteLink);
       
    });
}



function deleteInvoiceItem(id) {
    const apiUrl = site_url+'/invoice/api/deleteInvoiceItem/' +id + '/';

    return fetch(apiUrl, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(), // Include the CSRF token in the request headers if needed
        },
    })
    .then(response => {
        if (response.ok) {
            // Check if the response has content
            if (response.status === 204) {
                // No content in the response (HTTP 204 No Content status)
                return null; // Return null or any other appropriate value
            } else {
                return response.json(); // Parse JSON when available
            }
        } else {
            throw new Error('DELETE request failed');
        }
    });
}



function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function postDataAndGetData(invoice, product, quantity) {
// Call the POST method
    try {
        await postInvoiceData(invoice, product, quantity);
        await sleep(250); // Wait for .25 seconds
        await getNewestItemAndAddToTable();
    } catch (error) {
        console.error('Error:', error);
    }
}


const invoiceForm = document.getElementById('invoiceForm');
invoiceForm.addEventListener('submit',  e => {
    e.preventDefault();  // Prevent the default form submission
    const product = document.getElementById('product').value;
    const quantity = document.getElementById('quantity').value;
    const invoice = "{{ invoice }}"; // You should replace this with the actual invoice value
    postDataAndGetData(invoice, product, quantity)
        .then(data => {
            // Handle the response data as needed
        })
        .catch(error => {
            // Handle any errors
            console.error(error);
        });
});

const table = document.getElementById('item-table');

async function deleteDataAndGetData(itemID) {
// Call the POST method
    try {
        await deleteInvoiceItem(itemID);
        await sleep(250); // Wait for .25 seconds
        await getInvoiceData();
    } catch (error) {
        console.error('Error:', error);
    }
}

table.addEventListener('click', function(event) {
    // Check if the clicked element has the "delete-button" class
    if (event.target.classList.contains('delete-button')) {
        // Confirm the deletion
        
            // Access the row identifier from the data attribute
            const rowId = event.target.dataset.rowId;
            
            // Find the parent row of the clicked button
            const parentRow = event.target.closest('tr');
            
            if (parentRow) {
                // Find the specific cell within the row
                const itemID = parentRow.cells[5].textContent; 
                // Now 'cellValue' contains the value from the cell within that row
                deleteDataAndGetData(itemID)
            }
        
    }
});


const addItemButtons = document.querySelectorAll(".submit-button");

addItemButtons.forEach(button => {
    button.addEventListener("click", function (e) {
        e.preventDefault(); // Prevent the default form submission

        // Get the input values for this specific row
        const quantityInput = this.parentElement.parentElement.querySelector(".quantity-input");
        const productInput = this.parentElement.parentElement.querySelector("input[name='product']");
        const invoiceInput = this.parentElement.parentElement.querySelector("input[name='invoice']");

        // Get the input values from the DOM elements
        const quantity = quantityInput.value;
        const product = productInput.value;
        const invoice = invoiceInput.value;

        // Check if the quantity is less than 1
        if (quantity < 1) {
            alert("Quantity must be 1 or greater.");
            quantityInput.value = ""; // Set it to an empty string
        } else {
            // Log the input values to the console
            console.log({
                quantity,
                product,
                invoice,
            });

            // Call the postDataAndGetData function with the input values
            postDataAndGetData(invoice, product, quantity);
            quantityInput.value = ""; // Set it to an empty string
        }
    });
});





document.addEventListener('DOMContentLoaded', function() {
    getInvoiceData();
});



