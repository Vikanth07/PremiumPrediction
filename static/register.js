function formatAadhaar(input) {
    // Remove non-digit characters
    let value = input.value.replace(/\D/g, '').substring(0, 12);
    // Format the value as 4-4-4
    const formattedValue = value.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
    input.value = formattedValue;
}

function validateAadhaar() {
    const aadhaarInput = document.getElementById('aadhaarNumber').value.replace(/\D/g, '');
    if (aadhaarInput.length < 12) {
        showPopup("Aadhaar number must be exactly 12 digits");
        return false; // Prevent form submission
    }
    return true; // Allow Aadhaar submission
}

function validateForm() {
    const name = document.getElementById('name').value.trim();
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    const dob = document.getElementById('dob').value;
    const aadhaar = document.getElementById('aadhaarNumber').value.trim();
    const userPhoto = document.getElementById('userPhoto').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!name || !age || !gender || !dob || !aadhaar || !userPhoto || !password || !confirmPassword) {
        showPopup("Please fill in all the required details.");
        return false; // Prevent form submission
    }else if (password !== confirmPassword) {
        showPopup("Passwords do not match!");
        return false;
    }

    // Check if Aadhaar validation passes
    return validateAadhaar();
}

function showPopup(message) {
    document.getElementById('popupMessage').textContent = message; // Set the popup message
    document.getElementById('popup').style.display = 'block';
    document.getElementById('popupOverlay').style.display = 'block';
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('popupOverlay').style.display = 'none';
}