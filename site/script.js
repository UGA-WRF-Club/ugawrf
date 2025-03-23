async function loadDirectories() {
    const response = await fetch('https://storage.googleapis.com/storage/v1/b/uga-wrf-website/o?delimiter=/&prefix=outputs/');
    const data = await response.json();
    const directories = data.prefixes || [];
    const dropdown = document.getElementById('runSelector');
    dropdown.innerHTML = '';
    directories.reverse();
    directories.forEach(dir => {
        let folderName = dir.replace('outputs/', '').replace(/\/$/, '');
        if (folderName) {
            let option = document.createElement('option');
            option.value = folderName;
            option.textContent = folderName;
            dropdown.appendChild(option);
        }
    updateImage();
    updateTextForecast();
    });
}

const outputs = "https://storage.googleapis.com/uga-wrf-website/outputs/"

const products = {"temperature": "2m Temperature", "dewp": "2m Dewpoint", "comp_reflectivity": "Composite Reflectivity", "wind": "10m Wind", "pressure": "MSLP", "helicity": "Helicity", "total_precip": "Total Precipitation", "1hr_precip": "1-Hour Precipitation", "snowfall": "Snowfall", "echo_tops": "Echo Tops"};
const productSelector = document.getElementById('productSelector');

const hours = 24
const slider = document.getElementById('timeSlider');
var timestep = Number(slider.value)
const weatherImage = document.getElementById('weatherImage');
const timeLabel = document.getElementById('timeLabel');
const meteogram = document.getElementById('meteogram')
const textForecast = document.getElementById('textForecast');
const sahn = document.getElementById('sahn');
const scni = document.getElementById('scni');
const satl = document.getElementById('satl')
const smcn = document.getElementById('smcn');
const srmg = document.getElementById('srmg');
const scsg = document.getElementById('scsg');
const sffc = document.getElementById('sffc');
const seet = document.getElementById('seet');
const sohx = document.getElementById('sohx');
const sgsp = document.getElementById('sgsp');
function updateImage() {
    const run = document.getElementById('runSelector').value;
    const product = productSelector.value;
    timestep = Number(slider.value);
    timeLabel.textContent = `Hour ${timestep}/${hours}`;
    weatherImage.src = outputs + `${run}/${product}/hour_${timestep}.png`;
    sahn.src = outputs + `${run}/skewt/ahn/hour_${timestep}.png`;
    scni.src = outputs + `${run}/skewt/cni/hour_${timestep}.png`;
    satl.src = outputs + `${run}/skewt/atl/hour_${timestep}.png`;
    smcn.src = outputs + `${run}/skewt/mcn/hour_${timestep}.png`;
    srmg.src = outputs + `${run}/skewt/rmg/hour_${timestep}.png`;
    scsg.src = outputs + `${run}/skewt/csg/hour_${timestep}.png`;
    sffc.src = outputs + `${run}/skewt/ffc/hour_${timestep}.png`;
    seet.src = outputs + `${run}/skewt/bmx/hour_${timestep}.png`;
    sohx.src = outputs + `${run}/skewt/ohx/hour_${timestep}.png`;
    sgsp.src = outputs + `${run}/skewt/gsp/hour_${timestep}.png`;
}
async function updateTextForecast() {
    const textSelector = await document.getElementById('textSelector').value;
    const run = await document.getElementById('runSelector').value;
    fetch(outputs + `${run}/text/${textSelector}/forecast.txt`)
    .then(response => response.text())
    .then((data) => {
        textForecast.textContent = data
      })
    meteogram.src = outputs + `${run}/meteogram/${textSelector}/meteogram.png`
}
slider.addEventListener('input', updateImage);
productSelector.addEventListener('change', updateImage);
document.getElementById('runSelector').addEventListener('change', updateImage);
document.getElementById('runSelector').addEventListener('change', updateTextForecast);
document.getElementById('textSelector').addEventListener('change', updateTextForecast)
updateImage();
updateTextForecast();

document.getElementById('weatherImage').addEventListener('click', function() {
    document.getElementById('timeSlider').focus();

});
document.getElementById('textForecast').addEventListener('click', function() {
    document.getElementById('textSelector').focus();

});
document.getElementById('meteogram').addEventListener('click', function() {
    document.getElementById('textSelector').focus();

});

const playButton = document.getElementById("playButton")
const pauseButton = document.getElementById("pauseButton")
const speedSelector = document.getElementById("speedSelector")

function startLoop() {
    if (timestep == hours) {
        timestep = 0
    }
    loopInterval = setInterval(advanceLoop, speedSelector.value)
    playButton.disabled = true;
    pauseButton.disabled = false;
    speedSelector.disabled = true;
}

function endLoop() {
    clearInterval(loopInterval)
    playButton.disabled = false;
    pauseButton.disabled = true;
    speedSelector.disabled = false;
}

function advanceLoop() {
    timestep += 1;
    if (timestep == hours) {
        setTimeout(function() {timestep = 0}, speedSelector.value * 2)
    }
    slider.value = timestep
    updateImage();
}

playButton.addEventListener('click', startLoop)
pauseButton.addEventListener('click', endLoop)

loadDirectories();
window.onload = function() {
    for (let key in products) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = products[key];
        productSelector.appendChild(option);
    }
    timestep = Number(slider.value);
    updateImage()
    updateTextForecast()
};
