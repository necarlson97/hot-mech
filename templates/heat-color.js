function getHeatColor(heat) {
    if (heat <= -6) return getComputedStyle(document.documentElement).getPropertyValue('--cool').trim();
    if (heat >= 6) return getComputedStyle(document.documentElement).getPropertyValue('--blaze').trim();

    let startColor, endColor, factor;
    if (heat < 0) {
        // Interpolate between cool and white
        startColor = hexToRgb(getComputedStyle(document.documentElement).getPropertyValue('--cool').trim());
        endColor = { r: 255, g: 255, b: 255 }; // white
        factor = (heat + 3) / 3;
    } else {
        // Interpolate between white and blaze
        startColor = { r: 255, g: 255, b: 255 }; // white
        endColor = hexToRgb(getComputedStyle(document.documentElement).getPropertyValue('--blaze').trim());
        factor = heat / 6;
    }

    let resultColor = interpolateColor(startColor, endColor, factor);
    return `rgb(${resultColor.r}, ${resultColor.g}, ${resultColor.b})`;
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function interpolateColor(color1, color2, factor) {
    if (arguments.length < 3) { 
        factor = 0.5; 
    }
    var result = color1;
    result.r = Math.round(result.r + factor * (color2.r - color1.r));
    result.g = Math.round(result.g + factor * (color2.g - color1.g));
    result.b = Math.round(result.b + factor * (color2.b - color1.b));
    return result;
}

addEventListener("load",function(event) {
    console.log("Coloring cards");
    document.querySelectorAll('.card-heat').forEach(element => {
        const heat = parseInt(element.textContent.trim());
        element.style.backgroundColor = getHeatColor(heat);
    });
});

console.log("Heat color");
