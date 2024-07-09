function validateForm() {
    let name = document.getElementById('name').value;
    let email = document.getElementById('mail').value;
    let mobile = document.getElementById('no').value;
    let age = document.getElementById('age').value;
    let genderMale = document.getElementById('male').checked;
    let genderFemale = document.getElementById('female').checked;
    let experience = document.getElementById('exp').value;
    let designation = document.getElementById('designation').value;
    let specialization = document.getElementById('specialization').value;
    let password = document.getElementById('pass').value;
    let confirmPassword = document.getElementById('confirm pass').value;

    if (name == "" || email == "" || mobile == "" || age == "" || (!genderMale && !genderFemale) || experience == "" || designation == "Designation" || specialization == "" || password == "" || confirmPassword == "") {
        alert("All fields must be filled out");
        return false;
    }

    let emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        alert("Please enter a valid email address");
        return false;
    }

    if (mobile.length != 10) {
        alert("Please enter a valid 10-digit mobile number");
        return false;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return false;
    }

    return true;
}
