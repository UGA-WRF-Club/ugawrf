const products = {"temperature": "2m Temperature", "dewp": "2m Dewpoint", "comp_reflectivity": "Composite Reflectivity", "wind": "10m Wind", "pressure": "MSLP", "cape": "CAPE", "cape_mu": "CAPE (Most Unstable)", "helicity": "Helicity", "total_precip": "Total Precipitation", "snowfall": "Snowfall", "echo_tops": "Echo Tops"};
const productSelector = document.getElementById('productSelector');
for (key in products) {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = products[key];
    productSelector.appendChild(option);
}

const slider = document.getElementById('timeSlider');
const weatherImage = document.getElementById('weatherImage');
const timeLabel = document.getElementById('timeLabel');
const ahn = document.getElementById('ahn');
const atl = document.getElementById('atl');
const ffc = document.getElementById('ffc');
const mcn = document.getElementById('mcn');
const rmg = document.getElementById('rmg');
const csg = document.getElementById('csg');
function updateImage() {
    const run = document.getElementById('runSelector').value;
    const product = productSelector.value;
    const timestep = slider.value;
    timeLabel.textContent = `Hour ${timestep}/24`;
    weatherImage.src = `runs/${run}/${product}/hour_${timestep}.png`;
    ahn.src = `runs/${run}/skewt/AHN/hour_${timestep}.png`;
    atl.src = `runs/${run}/skewt/ATL/hour_${timestep}.png`;
    ffc.src = `runs/${run}/skewt/FFC/hour_${timestep}.png`;
    mcn.src = `runs/${run}/skewt/MCN/hour_${timestep}.png`;
    rmg.src = `runs/${run}/skewt/RMG/hour_${timestep}.png`;
    csg.src = `runs/${run}/skewt/CSG/hour_${timestep}.png`;
}
slider.addEventListener('input', updateImage);
productSelector.addEventListener('change', updateImage);
document.getElementById('runSelector').addEventListener('change', updateImage);
updateImage();

document.getElementById('weatherImage').addEventListener('click', function() {
    document.getElementById('timeSlider').focus();
});

