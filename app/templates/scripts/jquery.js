$(document).ready(function () {
        
    $('#forwarding-open-select-user').change(function () {
        var clients = $('#forwarding-open-select-user').val();
        fetch('/client_list')
            .then(response => response.json())
            .then(users => {
                $('#forwarding-open-select-client').attr('disabled', false);
                $('#forwarding-open-select-client').find('option').remove();
                users.forEach(e => {
                    $('#forwarding-open-select-client').append('<option value="' + e.id + '">' + e.name + '</option>');
                });
            })
            .catch(err =>{
                alert("Возникла ошибка при загрузке данных");
            });
    });


    $('#forwarding-open-select-client').change(function () {
        var client = $('#forwarding-open-select-client').val();        
        fetch('/port_list' + '/' + client)
            .then(response => response.json())
            .then(users => {
                $('#forwarding-open-select-port').attr('disabled', false);
                $('#forwarding-open-select-port').find('option').remove();
                users.forEach(e => {
                    $('#forwarding-open-select-port').append('<option value="' + e.id + '">' + e.name + '</option>');
                });
            })
            .catch(err =>{
                alert("Возникла ошибка при загрузке данных");
            });
    });
});
