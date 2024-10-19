// Toggle the health card modal
function toggleCardModal() {
    var cardModal = document.getElementById('cardModal');
    if (cardModal.style.display === "flex") {
        cardModal.style.display = "none";
    } else {
        cardModal.style.display = "flex";
    }
}
// Toggle the premium eligibility modal
function togglePremiumModal() {
    var modal = document.getElementById('premiumModal');
    modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
}

// Check if the user is eligible to apply for premium
// function checkPremiumEligibility() {
//     // Make AJAX call to retrieve the registration date
//     fetch('/check_premium_eligibility')
//         .then(response => response.json())
//         .then(data => {
//             const messageElement = document.getElementById('premiumMessage');
//             if (data.is_eligible) {
//                 messageElement.innerText = "You are eligible to apply for premium.";
//             } else {
//                 messageElement.innerText = "You are not eligible to apply as you have recently registered with our agency.";
//             }
//             togglePremiumModal(); // Show the modal with the eligibility message
//         })
//         .catch(error => {
//             console.error('Error fetching premium eligibility:', error);
//         });
// }

// Check if the user is eligible to apply for premium
function checkPremiumEligibility() {
    fetch('/check_premium_eligibility')
        .then(response => response.json())
        .then(data => {
            const messageElement = document.getElementById('premiumMessage');
            if (data.is_eligible) {
                messageElement.innerText = `You are eligible to apply for premium. Predicted premium: ₹${data.predicted_premium.toFixed(2)}`;
            } else {
                messageElement.innerText = "You are not eligible to apply as you have recently registered with our agency.";
            }
            togglePremiumModal(); // Show the modal with the eligibility message
        })
        .catch(error => {
            console.error('Error fetching premium eligibility:', error);
        });
}



// Function to download the card
function downloadCard(healthCardId) {
    // Hide the close button and download button temporarily
    var closeButton = document.querySelector('.close-btn');
    var downloadButton = document.getElementById('downloadBtn');
    closeButton.style.display = 'none';
    downloadButton.style.display = 'none';

    // Select the card element
    var card = document.getElementById('healthCard');

    // Use html2canvas to capture the card as an image
    html2canvas(card).then(function (canvas) {
        // Create a link element to trigger download
        var link = document.createElement('a');
        link.href = canvas.toDataURL('image/png');  // Convert canvas to PNG
        link.download = `healthCard_${healthCardId}.png`;  // Name of the downloaded image
        link.click();  // Trigger the download

        // Show the close button and download button again after the download
        closeButton.style.display = 'block';
        downloadButton.style.display = 'block';
    });
}