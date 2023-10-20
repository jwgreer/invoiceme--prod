// Function to extract the CSRF token from a cookie
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];
    return cookieValue;
}

function postInvoiceData(invoice, product, quantity) {
    const apiUrl = `http://127.0.0.1:8000/invoice/itemInvoice/${invoice}/`;
    const postData = {
        invoice: invoice,
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
// Function to call the product API
function callProductApi(productId) {
    const apiUrl = `http://127.0.0.1:8000/invoice/productsID/${productId}/`;

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



function getNewestItem(invoice) {
    const apiUrl = `http://127.0.0.1:8000/invoice/newestProduct/${invoice}/`;
    let testInvoice; // Declare these variables at a higher scope
    let quantity;
    let id;

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
    })
    .then(data => {
        if (data.length > 0) {
            const firstItem = data[0]; // Get the first object in the array
            const productId = firstItem.product;
            quantity = firstItem.quantity; // Assign quantity to the variable
            testInvoice = firstItem.invoice;
            id = firstItem.id; // Assign testInvoice to the variable
            return callProductApi(productId);
        } else {
            throw new Error('No data found in the response.');
        }
    })
    .then(productData => {

        // You can create a 'newestItem' object with the data you need
        const newestItem = {
            name: productData.name,
            price: productData.price,
            quantity: quantity,
            id: id // You can access the 'quantity' from the initial response
        };

        return newestItem;
    });
}


// Function to get the newest item and add it to the table
function getNewestItemAndAddToTable() {
    // Replace 'invoice' with the actual invoice ID
    const invoice = "{{invoice}}"; 
    getNewestItem(invoice).then(newestItem => {
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
        console.log(newestItem.id)

        // Hide the 5th cell with the ID
        idCell.hidden = true;

        // Create edit and delete links as before
        const invoice_pk = invoice
        const editLink = document.createElement('a');
        editLink.href = `http://127.0.0.1:8000/invoice/editInvoiceItem/${invoice_pk}/${newestItem.id}/`;
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
    const apiUrl = `http://127.0.0.1:8000/invoice/deleteInvoiceItem/${id}/`;

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





function getInvoiceData() {
    const invoice = "{{ invoice }}"; // Replace with the actual Django template variable

    const table = document.getElementById('item-table');
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    const apiUrl = `http://127.0.0.1:8000/invoice/itemInvoice/${invoice}/`;

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
                console.log(invoice)

                // Hide the 5th cell with the ID
                idCell.hidden = true;
                id = item.id
                const invoice_pk = invoice
                const editLink = document.createElement('a');
                editLink.href = `http://127.0.0.1:8000/invoice/editInvoiceItem/${invoice_pk}/${id}/`;
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

// Function to add a delay
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



// Automatically load invoice data when the page loads
document.addEventListener('DOMContentLoaded', function() {
    getInvoiceData();
});