const outputs = "https://storage.googleapis.com/uga-wrf-website/outputs/";
const hours = 24;
let timestep = 0;
let product = "temperature";
const slider = document.getElementById('timeSlider');
const runSelector = document.getElementById('runSelector');
const productSelector = document.getElementById('productSelector');
const textSelector = document.getElementById('textSelector');
const weatherImage = document.getElementById('weatherImage');
const timeLabel = document.getElementById('timeLabel');
const meteogram = document.getElementById('meteogram');
const textForecast = document.getElementById('textForecast');
const playButton = document.getElementById("playButton");
const pauseButton = document.getElementById("pauseButton");
const speedSelector = document.getElementById("speedSelector");
const stationIds = ["sahn", "scni", "satl", "smcn", "srmg", "scsg", "sffc", "sbmx", "sohx", "sgsp"];
const stationElements = Object.fromEntries(
    stationIds.map(id => [id, document.getElementById(id)])
);

async function loadDirectories() {
    const response = await fetch('https://storage.googleapis.com/storage/v1/b/uga-wrf-website/o?delimiter=/&prefix=outputs/');
    const data = await response.json();
    const directories = data.prefixes || [];
    runSelector.innerHTML = '';
    directories.reverse().forEach(dir => {
        const folderName = dir.replace('outputs/', '').replace(/\/$/, '');
        if (folderName) {
            let option = document.createElement('option');
            option.value = folderName;
            option.textContent = folderName;
            runSelector.appendChild(option);
        }
    });
    updateImage("temperature");
    updateTextForecast();
}
function updateImage(selectedProduct = product) {
    product = selectedProduct;
    const run = runSelector.value;
    timestep = Number(slider.value);
    timeLabel.textContent = `Hour ${timestep}/${hours}`;
    weatherImage.src = `${outputs}${run}/${product}/hour_${timestep}.png`;
    stationIds.forEach(id => {
        stationElements[id].src = `${outputs}${run}/skewt/${id.replace('s', '')}/hour_${timestep}.png`;
    });
}
async function updateTextForecast() {
    const run = runSelector.value;
    const textOption = textSelector.value;
    fetch(`${outputs}${run}/text/${textOption}/forecast.txt`)
        .then(response => response.text())
        .then(data => {
            textForecast.textContent = data;
        });
    meteogram.src = `${outputs}${run}/meteogram/${textOption}/meteogram.png`;
}
document.querySelectorAll('.dropdown-content a').forEach(item => {
    item.addEventListener('click', event => {
        event.preventDefault();
        updateImage(event.target.id);
    });
});
slider.addEventListener('input', () => updateImage());
runSelector.addEventListener('change', () => {
    updateImage();
    updateTextForecast();
});
textSelector.addEventListener('change', updateTextForecast);
weatherImage.addEventListener('click', () => slider.focus());
textForecast.addEventListener('click', () => textSelector.focus());
meteogram.addEventListener('click', () => textSelector.focus());
let loopInterval;
function startLoop() {
    if (timestep === hours) timestep = 0;
    loopInterval = setInterval(advanceLoop, speedSelector.value);
    playButton.disabled = true;
    pauseButton.disabled = false;
    speedSelector.disabled = true;
}
function endLoop() {
    clearInterval(loopInterval);
    playButton.disabled = false;
    pauseButton.disabled = true;
    speedSelector.disabled = false;
}
function advanceLoop() {
    timestep = (timestep + 1) % hours;
    slider.value = timestep;
    updateImage();
}
playButton.addEventListener('click', startLoop);
pauseButton.addEventListener('click', endLoop);
loadDirectories();
window.onload = function () {
    timestep = Number(slider.value);
    updateImage("temperature");
    updateTextForecast();
};