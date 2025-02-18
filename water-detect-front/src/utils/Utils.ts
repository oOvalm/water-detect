export function size2Str(limit: number): string {
    let size = "";
    if (limit < 1024) {
        size = limit.toFixed(2) + "B"
    } else if (limit < 1024 * 1024) {
        size = (limit / 1024).toFixed(2) + "KB"
    } else if (limit < 1024 * 1024 * 1024) {
        size = (limit / (1024 * 1024)).toFixed(2) + "MB"
    } else {
        size = (limit / (1024 * 1024 * 1024)).toFixed(2) + "GB"
    }
    var sizeStr = size + "";
    var index = sizeStr.indexOf(".");
    var dou = sizeStr.substring(index + 1, 2)
    if (dou == "00") {
        return sizeStr.substring(0, index) + sizeStr.substring(index + 3, 2)
    }
    return size;
}

export function formatDuration(duration: number): string {
    let ss = duration % 60
    duration = (duration / 60) | 0
    let mm = duration % 60
    duration = (duration / 60) | 0
    let hh = duration % 60
    if (hh == 0) {
        return `${mm}:${ss}`
    } else {
        return `${hh}:${mm}:${ss}`
    }
}
