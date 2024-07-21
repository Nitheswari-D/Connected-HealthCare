document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("form").addEventListener("submit", function(event) {
        if (!validatepatientForm()) {
            event.preventDefault();
        }
    });
});

function validatepatientForm() {
    let name = document.getElementById("name").value;
    let email = document.getElementById("mail").value;
    let mobile = document.getElementById("no").value;
    let age = document.getElementById("age").value;
    let genderMale = document.getElementById("male").checked;
    let genderFemale = document.getElementById("female").checked;
    let password = document.getElementById("pass").value;
    let confirmPassword = document.getElementById("confirm pass").value;

    if (name == "" || email == "" || mobile == "" || age == "" || (!genderMale && !genderFemale) || password == "" || confirmPassword == "") {
        alert("All fields must be filled out");
        return false;
    }

    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert("Invalid email address");
        return false;
    }

    let mobilePattern = /^\d{10}$/;
    if (!mobilePattern.test(mobile)) {
        alert("Invalid mobile number");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return false;
    }

    return true;
}
