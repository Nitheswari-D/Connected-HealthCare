
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Get the selected userType
    const userType = document.querySelector('input[name="userType"]:checked').value;

    // Check if the selected userType is 'patient'
    if (userType === 'patient') {
        window.location.href = 'patpage.html'; // Redirect to patient page
    } else {
        // Add logic for doctor or any other actions if necessary
        document.getElementById('loginMessage').textContent = "You have logged in successfully!";
        document.getElementById('loginMessage').classList.remove('hidden');
    }
});
