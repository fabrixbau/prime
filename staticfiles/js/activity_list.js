document.querySelectorAll('.btn-edit-activity').forEach(button => {
    button.addEventListener('click', function (){
        const activityId= this.getAttribute('data-id');
        // fill out the modal form with activity data
        fetch(`/activities/${activityId}/`) 
            .then(response => response.json())
            .then(data=> {
                document.getElementById('activity_id').value = data.id;
                document.getElementById('name').value = data.name;
                document.getElementById('description').value = data.description;
                document.getElementById('days_of_week').value = data.days_of_week.split();
                document.getElementById('start_time').value = data.start_time;
                document.getElementById('duration_minutes').value = data.duration_minutes;
            });
        cocument.getElementById('editActivityModal').style.display = 'block';
    });
});
// close the modal
document.querySelector('.close').addEventListener('click', function(){
    document.getElementById('editActivityModal').style.display = 'none';
})