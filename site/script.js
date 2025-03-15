const products = {"temperature": "Temperature", "comp_reflectivity": "Composite Reflectivity", "wind": "Wind", "pressure": "Pressure", "cape": "CAPE", "cape_mu": "CAPE (Mixed Layer)", "helicity": "Helicity", "total_precip": "Total Precipitation", "snowfall": "Snowfall", "echo_tops": "Echo Tops"};
const productSelector = document.getElementById('productSelector');
for (const key in products) {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = products[key];
    productSelector.appendChild(option);
}

const slider = document.getElementById('timeSlider');
const weatherImage = document.getElementById('weatherImage');
function updateImage() {
    const run = document.getElementById('runSelector').value;
    const product = productSelector.value;
    const timestep = slider.value;

    weatherImage.src = `runs/${run}/${product}/hour_${timestep}.png`;
}
slider.addEventListener('input', updateImage);
productSelector.addEventListener('change', updateImage);
document.getElementById('runSelector').addEventListener('change', updateImage);
updateImage();