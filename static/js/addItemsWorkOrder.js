
var api = apiUrl;

// Assuming you have jQuery for AJAX, but you can use vanilla JavaScript as well

function getWorkOrderItemCount(workOrderId) {
    return fetch(site_url + '/workOrder/getWorkOrderItemCount/' + workOrder_id + '/')
        .then(response => response.json())
        .then(data => {
            return data.count;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function updateWorkOrderItemNumber(id, number) {
    const payload = {
        number: number,
    };

    return fetch(site_url + '/workOrder/api/workOrderItemNumber/' + id + '/', {
        method: 'PUT', // Specify the HTTP method as PUT
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload), // Include the 'number' value in the payload
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('PUT request failed');
        }
    })
    .then(data => {
        return data;
    })
    .catch(error => {
        console.error('Error:', error);
        throw error;
    });
}



function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        .split('=')[1];
    return cookieValue;
}


function postWorkOrderData(workOrder_id, product, description) {

    const apiUrl = site_url + '/workOrder/api/itemWorkOrder/' + workOrder_id + '/';
    const postData = {
        "workOrder": workOrder_id,
        "product": product,
        "description": description,
        "status": "Waiting_on_Assignment",
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
            return response.json(); // Parse the JSON response
        } else {
            throw new Error('POST request failed');
        }
    })
    .then(data => {
        return data; // Return the data if needed
    })
    .catch(error => {
        console.error(error); // Handle any errors here
        throw error; // Re-throw the error if needed
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

function callProductApiOther(productId) {

    const apiUrl = site_url +'/workOrder/api/workOrderItemOther/' + productId + '/';
    

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


function getWorkOrderData() {// Replace with the actual Django template variable

    const table = document.getElementById('item-table');
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }
    
    const apiUrl = site_url +'/workOrder/api/itemWorkOrder/' + workOrder_id + '/';


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
            const numberCell = row.insertCell(0);
            const workOrderCell = row.insertCell(1);
            const quantityCell = row.insertCell(2);
            const descriptionCell = row.insertCell(3);
            const editCell = row.insertCell(4);
            const deleteCell = row.insertCell(5);
            const idCell = row.insertCell(6);


            // Call the callProductApi function for each item
            
            if(item.product_id == 2){
                callProductApiOther(item.id).then(productData => {

                    // Populate the cells with product data
                    numberCell.textContent = item.number;
                    workOrderCell.textContent = productData.name;
                    quantityCell.textContent = item.quantity;
                    descriptionCell.textContent = item.description;
                    idCell.textContent = item.id;
    
                    // Hide the 5th cell with the ID
                    idCell.hidden = true;
                    id = item.id
                    const editLink = document.createElement('a');
                    editLink.href = site_url+'/editWorkOrderItem/' + workOrder_id + '/' +id + '/';
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
            else{
            
            callProductApi(item.product_id).then(productData => {

                // Populate the cells with product data
                numberCell.textContent = item.number;
                workOrderCell.textContent = productData.name;
                quantityCell.textContent = item.quantity;
                descriptionCell.textContent = item.description;
                idCell.textContent = item.id;

                // Hide the 5th cell with the ID
                idCell.hidden = true;
                id = item.id
                const editLink = document.createElement('a');
                editLink.href = site_url+'/editWorkOrderItem/' + workOrder_id + '/' +id + '/';
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
        });
    })
    .catch(error => console.error('Error:', error));
}



function getNewestItem(workOrder_id) {
    const apiUrl = site_url + '/workOrder/api/newestProduct/' + workOrder_id + '/';
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
            console.log(firstItem);
            const productId = firstItem.product;
            const quantity = firstItem.quantity;
            const id = firstItem.id;
            const number = firstItem.number;
            const desc = firstItem.description;
            return callProductApi(productId)
                .then(productData => {
                    console.log(productData);
                    const newestItem = {
                        name: productData.name,
                        price: productData.price,
                        quantity: quantity,
                        id: id
                    };
                    return result = {
                        newestItem: newestItem,
                        number: number,
                        desc: desc

                    };
                });
        } else {
            throw new Error('No data found in the response.');
        }
    });
}


function getNewestItemAndAddToTable() {
    // Replace 'invoice' with the actual invoice ID
    getNewestItem(workOrder_id).then(result => {
        console.log(result);

        const table = document.getElementById('item-table');
        const row = table.insertRow(); // Insert a new row at the end of the table
        const numberCell = row.insertCell(0);
        const productNameCell = row.insertCell(1);
        const quantityCell = row.insertCell(2);
        const descriptionCell = row.insertCell(3);
        const editCell = row.insertCell(4);
        const deleteCell = row.insertCell(5);
        const idCell = row.insertCell(6);

        // Add content to visible cells
        console.log(result.desc);

        numberCell.textContent = result.number;
        productNameCell.textContent = result.newestItem.name;
        quantityCell.textContent = "1";
        descriptionCell.textContent = result.desc;
        


        // Set a value for the hidden cell with the ID
        idCell.textContent = result.newestItem.id;

        // Hide the 5th cell with the ID
        idCell.hidden = true;

        // Create edit and delete links as before
        const editLink = document.createElement('a');
        editLink.href = site_url+'/editWorkOrderItem/'+ workOrder_id +'/'+ result.newestItem.id+'/';
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



function deleteWorkOrderItem(id) {
    const apiUrl = site_url+ '/workOrder/api/deleteWorkOrderItem/' +id + '/';

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


function renumberTable() {
    // Get the table
    var table = document.getElementById('item-table');

    // Get all rows except the header row
    var rows = table.querySelectorAll('tbody tr');

    // Iterate through the rows to update the numbers
    for (var i = 1; i < rows.length; i++) {
        const idCell = rows[i].cells[6];
        const id = idCell.textContent;
        const number = i;
        updateWorkOrderItemNumber(id, number)
            // Make the API call to update the item using 'id' and 'number'
 
        
    }
}


async function postDataAndGetData(workOrder_id, product, description) {
    try {
        const data = await postWorkOrderData(workOrder_id, product, description);
        await sleep(250); // Wait for .25 seconds
        

        getWorkOrderItemCount(workOrder_id) // This is a promise
            .then(number => {
                // Now you can call updateInvoiceItemNumber with 'number'
                return updateWorkOrderItemNumber(data.id, number);
            })
            .then(result => {
                getNewestItemAndAddToTable();
            })
            .catch(error => {
                console.error('Error:', error);
            });

        await sleep(250);
    } catch (error) {
        console.error('Error:', error);
    }
}




const workOrderForm = document.getElementById('workOrderForm');
workOrderForm.addEventListener('submit',  e => {
    
    e.preventDefault();  // Prevent the default form submission
    const product = document.getElementById('product').value;
    const description = document.getElementById('description').value;
    const workOrder_id = "{{ workOrder_id }}";
    postDataAndGetData(workOrder_id, product, description)
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
        await deleteWorkOrderItem(itemID);
        await sleep(250); // Wait for .25 seconds
        await getWorkOrderData();
        await sleep(250);
        await renumberTable();
        await sleep(250); // Wait for .25 seconds
        await getWorkOrderData();
        
        
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
                const itemID = parentRow.cells[6].textContent; 
                // Now 'cellValue' contains the value from the cell within that row
                deleteDataAndGetData(itemID)
            }
        
    }
});


const addItemButtons = document.querySelectorAll(".submit-button");

const reOrderButton = document.getElementById("re-order");


reOrderButton.addEventListener("click", function (e) {
    renumberTable();
    getWorkOrderData();

});

addItemButtons.forEach(button => {
    button.addEventListener("click", function (e) {
        e.preventDefault(); // Prevent the default form submission

        
        // Get the input values for this specific row
        const productInput = this.parentElement.parentElement.querySelector("input[name='product']");
        const workOrderInput = this.parentElement.parentElement.querySelector("input[name='workOrder']");
        const descriptionInput = this.parentElement.parentElement.querySelector("input[name='description']");

        // Get the input values from the DOM elements
        const product = productInput.value;
        const workOrder_id = workOrderInput.value;
        const description = descriptionInput.value;





        // Call the postDataAndGetData function with the input values
        postDataAndGetData(workOrder_id, product, description);
        
    });
});





document.addEventListener('DOMContentLoaded', function() {
    getWorkOrderData();
    
});
