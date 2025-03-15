const products = ['temperature', "comp_reflectivity", 'wind', 'pressure', 'cape', 'cape_mu', 'helicity', 'total_precip', 'snowfall'];
const productSelector = document.getElementById('productSelector');
products.forEach(product => {
    const option = document.createElement('option');
    option.value = product;
    option.textContent = product;
    productSelector.appendChild(option);
});

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