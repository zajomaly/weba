document.addEventListener('DOMContentLoaded', () => {
    fetch('/fetch_prices')
        .then(response => response.json())
        .then(data => {
            let todayPricesTable = document.getElementById('todayPrices');
            let tomorrowPricesTable = document.getElementById('tomorrowPrices');

            data.today.forEach((row, index) => {
                let tr = document.createElement('tr');
                let timeTd = document.createElement('td');
                let priceTd = document.createElement('td');
                timeTd.textContent = `${index + 1}:00`;
                priceTd.textContent = row.price;
                tr.appendChild(timeTd);
                tr.appendChild(priceTd);
                todayPricesTable.appendChild(tr);
            });

            data.tomorrow.forEach((row, index) => {
                let tr = document.createElement('tr');
                let timeTd = document.createElement('td');
                let priceTd = document.createElement('td');
                timeTd.textContent = `${index + 1}:00`;
                priceTd.textContent = row.price;
                tr.appendChild(timeTd);
                tr.appendChild(priceTd);
                tomorrowPricesTable.appendChild(tr);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});
