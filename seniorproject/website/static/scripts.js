/*
function searchFarmersMarket() {
    const zipcode = document.getElementById('zipcode').value;
    const radius = document.getElementById('radius').value;

    const apikey = 'tlnUddS4mT';

    const apiUrl = `https://www.usdalocalfoodportal.com/api/farmersmarket/?apikey=${apikey}&zip=${zipcode}&radius=${radius}`;

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(responseData => {
            const data = responseData.data;

            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = ''; // Clear previous results

            const resultsTable = document.getElementById('resultsTable').getElementsByTagName('tbody')[0];
            resultsTable.innerHTML = ''; // Clear previous table rows

            if (Array.isArray(data)) {
                data.forEach(farm => {
                    const row = resultsTable.insertRow();
                    const cell1 = row.insertCell(0);
                    const cell2 = row.insertCell(1);
                    const cell3 = row.insertCell(2);

                    cell1.textContent = farm.listing_name;
                    const addressLink = `https://www.google.com/maps?q=${encodeURIComponent(farm.location_address)}`;
                    cell2.innerHTML = `<a href="${addressLink}" target="_blank">${farm.location_city}, ${farm.location_state}, ${farm.location_zipcode}</a>`;
                    //cell3.innerHTML = `<a href="${farm.media_website}" target="_blank">${farm.media_website}</a>`;
                    if (farm.media_website) {
                        cell3.innerHTML = `<a href="${farm.media_website}" target="_blank">${farm.media_website}</a>`;
                    } else {
                        cell3.textContent = 'No website';
                    }
                });
            } else {
                resultsContainer.textContent = 'No data found.';
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

function deletePost(postId) {
    fetch('/deletepost', {
    method: 'POST',
    body: JSON.stringify({ postId: postId})
    }).then((_res) => {
        window.location.href="/"
    });
}
*/
