// the dreaded products key value pair system returns. it is currently used for the secondary map system (which will be made better with time)
const products = {
    "temperature": "Temperature",
    "dewp": "Dew Point",
    "pressure": "Pressure",
    "wind": "Wind",
    "wind_gust": "Wind Gust",
    "comp_reflectivity": "Composite Reflectivity",
    "helicity": "Helicity",
    "1hr_precip": "1-Hour Precipitation",
    "total_precip": "Total Precipitation",
    "1hr_snowfall": "1-Hour Snowfall",
    "snowfall": "Snowfall",
    "4panel_cloudcover": "4-Panel Cloud Cover",
    "cloudcover": "Cloud Cover",
    "echo_tops": "Echo Tops",
    "temp_850mb": "Temperature (850mb)",
    "temp_700mb": "Temperature (700mb)",
    "temp_500mb": "Temperature (500mb)",
    "temp_300mb": "Temperature (300mb)",
    "td_850mb": "Dew Point (850mb)",
    "rh_850mb": "Relative Humidity (850mb)",
    "td_700mb": "Dew Point (700mb)",
    "rh_700mb": "Relative Humidity (700mb)",
    "td_500mb": "Dew Point (500mb)",
    "rh_850mb": "Relative Humidity (500mb)",
    "td_300mb": "Dew Point (300mb)",
    "rh_300mb": "Relative Humidity (300mb)",
    "wind_850mb": "Wind (850mb)",
    "wind_700mb": "Wind (700mb)",
    "wind_500mb": "Wind (500mb)",
    "wind_300mb": "Wind (300mb)",
    "heights_700mb": "Heights (700mb)",
    "heights_500mb": "Heights (500mb)",
};

const outputs = "https://storage.googleapis.com/uga-wrf-website/outputs/";
//const outputs = "runs/"
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
const multiEnabler = document.getElementById("multiEnabler")
const multiSelector = document.getElementById("multiSelector")
const multiSubchooser = document.getElementById('multiSubchooser')
const secondaryImage = document.getElementById('secondaryImage')
const stationIds = ["sahn", "scni", "satl", "smcn", "srmg", "scsg", "sffc", "sbmx", "sohx", "sgsp"];
const stationElements = Object.fromEntries(
    stationIds.map(id => [id, document.getElementById(id)])
);

async function loadDirectories(pageToken = '') {
    const baseUrl = 'https://storage.googleapis.com/storage/v1/b/uga-wrf-website/o?delimiter=/&prefix=outputs/';
    let directories = [];
    while (true) {
        const response = await fetch(pageToken ? `${baseUrl}&pageToken=${pageToken}` : baseUrl);
        const data = await response.json();
        
        directories = directories.concat(data.prefixes || []);
        
        if (!data.nextPageToken) break;
        pageToken = data.nextPageToken;
    }
    directories.reverse().forEach(dir => {
        const folderName = dir.replace('outputs/', '').replace(/\/$/, '');
        if (folderName) {
            let option = document.createElement('option');
            option.value = folderName;
            option.textContent = folderName.replaceAll("-", '/').replace("_", " ").replaceAll("_", ":");
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
    updateSecondaryDisplay()
}
function updateSecondaryDisplay() {
    const run = runSelector.value;
    const subchoosed = multiSubchooser.value
    timestep = Number(slider.value);
    if (multiSelector.value == 'map')
        {
            secondaryImage.src = `${outputs}${run}/${subchoosed}/hour_${timestep}.png`
        }
    else if (multiSelector.value == 'skewt')
        {
            secondaryImage.src = `${outputs}${run}/skewt/${subchoosed}/hour_${timestep}.png`
        }
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
function toggleSecondaryDisplay() {
    if (multiEnabler.checked == true) {
        weatherImage.style.width = "700px"
        secondaryImage.setAttribute('style', 'display:')
        multiSelector.disabled = false
        multiSubchooser.disabled = false
        multiSubchooser.innerHTML = ''
        if (multiSelector.value == 'map')
            {
                for (const key in products) {
                    const option = document.createElement('option');
                    option.value = key;
                    option.textContent = products[key];
                    multiSubchooser.appendChild(option);
                }
            }
        else if (multiSelector.value == 'skewt') {
            for (const airport in stationIds) {
                const option = document.createElement('option');
                option.value = stationIds[airport].replace('s', '')
                option.textContent = stationIds[airport].replace('s', '')
                multiSubchooser.appendChild(option)
            }
        }
        secondaryImage.addEventListener('click', () => slider.focus());
        updateSecondaryDisplay()
    }
    if (multiEnabler.checked == false) {
        weatherImage.style.width = "900px"
        secondaryImage.setAttribute('style', 'display: none;')
        multiSelector.disabled = true
        multiSubchooser.disabled = true
        secondaryImage.removeEventListener('click', () => slider.focus());
    }
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
multiEnabler.addEventListener('click', toggleSecondaryDisplay)
multiSelector.addEventListener('change', toggleSecondaryDisplay)
multiSubchooser.addEventListener('change', updateSecondaryDisplay)
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
    multiEnabler.checked = false
    multiSelector.disabled = true
    multiSubchooser.disabled = true
};
updateTextForecast();