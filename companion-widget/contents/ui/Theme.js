.pragma library

function palette(light, accent) {
    var hue=Math.max(0,accent.hslHue);
    function tone(saturation, luminance) {return Qt.hsla(hue,saturation,luminance,1);}
    return {
        ink:tone(.35,light?.13:.96),
        muted:tone(.25,light?.36:.76),
        panel:tone(.55,light?.985:.075),
        field:tone(.55,light?.955:.12),
        line:Qt.hsla(hue,.45,light?.35:.75,light?.18:.16),
        backgroundStart:tone(.7,light?.965:.04),
        backgroundEnd:Qt.hsla((hue+.045)%1,.6,light?.935:.14,1),
        secondary:Qt.hsla((hue+.075)%1,.7,.65,1),
        lifted:tone(.5,light?.93:.17)
    };
}
