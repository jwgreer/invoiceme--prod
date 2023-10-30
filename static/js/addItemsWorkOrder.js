

    
    function closeModal() {
        $('#error-modal').modal('hide');
    }
    function showErrorModal(message) {
        var errorText = document.getElementById("error-message");
        errorText.innerHTML = message;
        $('#error-modal').modal('show');
    }
    document.getElementById('close-modal-button').addEventListener('click', function() {
        closeModal(); // Call the function to close the modal
    });
    
        $(document).ready(function() {
            // what we need for the payload
            // the crsf token
            // the endpoint url
            // the workorder id
            // the workOrder_id
            // the id of the item you want to delete
            // this is the process for the item delete
            var csrfToken = $('input[name=csrfmiddlewaretoken]').val();
            var apiUrlDelete = site_url + '/workOrder/api/deleteWorkOrderItem/';
            var apiUrlUpdate = site_url + '/workOrder/api/workOrderEnrichment/';
            var postUrl = site_url + '/workOrder/api/addItemTestAPI/';
    
            
            $("#table-container-item").on("click", ".delete-link", function() {
                var $button = $(this);
                var $row = $button.closest("tr");
                var id = $(this).data('itemid');
                console.log(workOrder_id);
                
    
                deleteData(apiUrlDelete, csrfToken, workOrder_id, id)
    
            });
    
            $("#table-container-add-item").on("click", ".submit-button", function() {
            // Access the clicked button
            var $button = $(this);
            var $row = $button.closest("tr");
            $quantityInput = $row.find(".quantity").val();
            $mfgnumInput= $row.find(".mfgnum").val();
            $descriptionTextarea= $row.find(".description").val();
            $issueTextarea= $row.find(".issue").val();
            productValue= $row.find("[name='product']").val();
            workOrderValue= $row.find("[name='workOrder']").val();
            // Traverse the DOM to find elements within the same row
            var data = {
                    quantity: $quantityInput,
                    mfgnum: $mfgnumInput,
                    description: $descriptionTextarea,
                    issue: $issueTextarea,
                    product: productValue,
                    workOrder: workOrderValue
                };
    
            postData(postUrl, crsfToken, data, $row);
    
        });
    
    
        function clearInputBoxes($row) {
                // Clear the input boxes within a specific row.
                $row.find(".description").val("");
                $row.find(".quantity").val("");
                $row.find(".mfgnum").val("");
                $row.find(".issue").val("");
            }
    
            
            // change event on the is_rush box
            $('input[name="is_rush"]').on('change', function() {
                var isRush = $(this).is(':checked');
                var type = "is_rush";
        
                updateData(apiUrlUpdate, csrfToken,workOrder_id,type, isRush);
            });
            
            // change event on the quote required box
            $('input[name="quote_required"]').on('change', function() {
                var quote_required = $(this).is(':checked');
                var type = "quote_required";
        
                updateData(apiUrlUpdate, csrfToken,workOrder_id,type, quote_required);
            });
            
            // when the user keys in enter, it updates the text input
            $('#specialInstructions').on('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent the default Enter key behavior
                    var specialInstructionsValue = $(this).val(); // Get the value from the text box
                    var type = "specialInstructions";
    
                    updateData(apiUrlUpdate, csrfToken, workOrder_id,type, specialInstructionsValue);
                }
            });
    
            // when user selects the new date update the date
            $('input[name="return_by"]').on('change', function() {
                var return_by = $(this).val();
                var type = "return_by";
    
                updateData(apiUrlUpdate, csrfToken, workOrder_id, type, return_by);
            });
            
            
            // this script is used to display the calendar date picker
            $('.datepicker').datepicker({
                format: 'yyyy-mm-dd',  // This is the way the model accepts the date
                autoclose: true
            });
            
            
            
    
    
            function deleteData(apiEndpoint, csrfToken, workOrder_id, id) {
                // Set up the CSRF token in the request headers
                var headers = {
                    'X-CSRFToken': csrfToken
                };
    
                $.ajax({
                    type: 'DELETE',
                    url: apiEndpoint,
                    data: JSON.stringify({ workOrder_id: workOrder_id, id: id }),
                    contentType: 'application/json',
                    headers: headers,
                    success: function(data) {
                        $("#item-table").load(window.location.href + " #item-table");
    
                    },
                    error: function(error) {
                        console.error(error);
                    }
                });
            }
    
    
      
    
           function postData(postUrl, crsfToken, data, $row){

            var headers = {
                'X-CSRFToken': csrfToken
            };

            $.ajax({
                type: 'POST',
                url: postUrl,
                data: JSON.stringify({ data: data }),
                contentType: 'application/json',
                headers: headers,
                success: function(data) {
                    loadTable();
                    clearInputBoxes($row);
    
                },
                error: function(error) {
                console.error(error);
                showErrorModal("Enter a number greater than 0"); // Display the error message
            }
    
            });
           }
    
           function loadTable() {
                // Reload the table with the id "item-table" from the current URL.
                $("#item-table").load(window.location.href + " #item-table", function() {
                    
                });
            }
      
            function updateData(apiEndpoint, csrfToken,workOrder_id,type, value) {
                // Set up the CSRF token in the request headers
                var headers = {
                    'X-CSRFToken': csrfToken
                };
        
                $.ajax({
                    type: 'POST',
                    url: apiEndpoint,
                    data: JSON.stringify({ workOrder_id: workOrder_id, type: type, value: value }),
                    contentType: 'application/json',
                    headers: headers,
                    success: function(data) {
                        
                        // Update the specific content within the container
                        if (type === 'specialInstructions') {
                            $( "#specialInstructions_d" ).load(window.location.href + " #specialInstructions_d" );
                            
                        } else if (type === 'is_rush') {
                            $( "#is_rush_d" ).load(window.location.href + " #is_rush_d" );
                        } else if (type === 'return_by') {
                            $( "#return_by_d" ).load(window.location.href + " #return_by_d" );
                        } else if (type === 'quote_required') {
                            $( "#quote_required_d" ).load(window.location.href + " #quote_required_d" );
                        } else {
                            // Handle other content updates
                        }
                    },
                    error: function(error) {
                        console.error(error);
                    }
                });
            }
    
        });
    