// ── 全局状态 ──
let chart = null;
let chartData = [];
const MAX_POINTS = 300;
let connected = false;
let wailsReady = false;

// ── 日志辅助 ──
function log(msg, data) {
    console.log('[UviLUX] ' + msg, data || '');
}

// ── 等待 Wails runtime 就绪 ──
function waitForWails(callback, attempts) {
    attempts = attempts || 0;
    if (typeof window.runtime !== 'undefined' && typeof window.go !== 'undefined') {
        wailsReady = true;
        log('Wails runtime 就绪 (尝试 ' + attempts + ' 次)');
        document.getElementById('status-text').textContent = '未连接';
        callback();
        return;
    }
    if (attempts < 100) {
        setTimeout(function() { waitForWails(callback, attempts + 1); }, 50);
    } else {
        log('ERROR: Wails runtime 超时未就绪！');
        document.getElementById('status-text').textContent = 'Runtime 未加载';
        // 仍然尝试初始化，但只初始化图表
        try { initChart(); } catch(e) {}
    }
}

// ── 应用初始化 ──
function initApp() {
    log('应用初始化开始');

    // 检查 ECharts
    if (typeof echarts === 'undefined') {
        log('ERROR: ECharts 未加载！');
        document.getElementById('chart-placeholder').textContent = '图表库加载失败';
        return;
    }

    initChart();
    setupEvents();
    refreshPorts();
    log('应用初始化完成');
}

// ── 等待 DOM + Wails ──
document.addEventListener('DOMContentLoaded', function() {
    log('DOM 就绪，等待 Wails runtime...');
    waitForWails(initApp);
});

// ═══════════════════════════════════════════════
// ECharts 初始化
// ═══════════════════════════════════════════════
function initChart() {
    var container = document.getElementById('chart-container');
    // 移除占位符
    var ph = document.getElementById('chart-placeholder');
    if (ph) ph.style.display = 'none';

    chart = echarts.init(container);

    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                if (!params || params.length === 0) return '';
                var p = params[0];
                if (!p || !p.data || p.data.length < 2) return '';
                var d = new Date(p.data[0]);
                return d.toTimeString().slice(0,8) + '<br/>测量值: <b>' + p.data[1].toFixed(4) + '</b>';
            }
        },
        grid: { left: 55, right: 25, top: 15, bottom: 40 },
        xAxis: {
            type: 'time',
            splitLine: { show: true, lineStyle: { color: '#f0f0f0' } },
            axisLabel: {
                formatter: function(v) { return new Date(v).toTimeString().slice(0,8); }
            }
        },
        yAxis: {
            type: 'value',
            splitLine: { show: true, lineStyle: { color: '#f0f0f0' } }
        },
        series: [{
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: { color: '#1a73e8', width: 1.5 },
            data: [],
            markLine: {
                silent: true,
                symbol: 'none',
                data: [{ yAxis: 0, lineStyle: { color: '#999', type: 'dashed' } }]
            }
        }],
        dataZoom: [{ type: 'inside', start: 0, end: 100 }]
    });

    window.addEventListener('resize', function() { chart.resize(); });
    new ResizeObserver(function() { chart.resize(); }).observe(container);
    log('ECharts 初始化完成');
}

// ═══════════════════════════════════════════════
// Wails 事件监听
// ═══════════════════════════════════════════════
function setupEvents() {
    if (!wailsReady) {
        log('WARNING: setupEvents 调用时 runtime 未就绪');
        return;
    }

    window.runtime.EventsOn('measurement', function(data) {
        log('收到 measurement', data);
        appendMeasurement(data);
    });

    window.runtime.EventsOn('eht-update', function(rows) {
        log('收到 eht-update', rows);
        updateEHTTable(rows);
    });

    window.runtime.EventsOn('info-update', function(info) {
        log('收到 info-update', info);
        updateSensorInfo(info);
    });

    window.runtime.EventsOn('serial-status', function(status) {
        log('收到 serial-status: ' + status);
        updateSerialStatus(status);
    });

    window.runtime.EventsOn('log-status', function(data) {
        log('收到 log-status', data);
        if (data && data.status === 'opened') {
            document.getElementById('log-text').textContent = data.filename || '-';
        } else {
            document.getElementById('log-text').textContent = '已保存';
        }
    });

    window.runtime.EventsOn('serial-error', function(msg) {
        log('收到 serial-error: ' + msg);
        alert('串口错误: ' + msg);
        updateSerialStatus('error');
    });

    window.runtime.EventsOn('replay-data', function(data) {
        log('收到 replay-data, 数据点: ' + (data.points ? data.points.length : 0));
        loadReplayData(data);
    });

    window.runtime.EventsOn('clear-chart', function() {
        log('收到 clear-chart');
        clearChartData();
    });

    log('事件监听注册完成');
}

// ═══════════════════════════════════════════════
// 数据处理
// ═══════════════════════════════════════════════
function appendMeasurement(data) {
    if (!data) return;
    var ts = data.timestamp * 1000;
    chartData.push([ts, data.value]);
    if (chartData.length > MAX_POINTS) {
        chartData.splice(0, chartData.length - MAX_POINTS);
    }
    if (chart) {
        chart.setOption({ series: [{ data: chartData }] });
    }
    document.getElementById('mode-val').textContent = data.mode || '-';
    document.getElementById('cur-val').textContent = (data.value != null) ? data.value.toFixed(3) : '-.---';
    document.getElementById('count-text').textContent = data.count || 0;
    document.getElementById('last-text').textContent = new Date(ts).toTimeString().slice(0,8);
}

function loadReplayData(data) {
    if (!data || !data.points) return;
    chartData = data.points.map(function(p) { return [p.x * 1000, p.y]; });
    if (chart) {
        chart.setOption({ series: [{ data: chartData }] });
    }
    if (data.sensorInfo) updateSensorInfo(data.sensorInfo);
    if (data.ehtRows) updateEHTTable(data.ehtRows);
    document.getElementById('mode-val').textContent = data.mode || '-';
    document.getElementById('count-text').textContent = data.dataCount || 0;
    if (chartData.length > 0) {
        var last = chartData[chartData.length-1];
        document.getElementById('cur-val').textContent = last[1].toFixed(3);
        document.getElementById('last-text').textContent = new Date(last[0]).toTimeString().slice(0,8);
    }
}

// ═══════════════════════════════════════════════
// UI 更新
// ═══════════════════════════════════════════════
function updateSensorInfo(info) {
    if (!info) return;
    document.getElementById('serial').textContent = info.serialNumber || '-';
    document.getElementById('instype').textContent = info.instrumentType || '-';
    document.getElementById('firmware').textContent = info.firmwareVersion || '-';
}

function updateEHTTable(rows) {
    if (!rows) return;
    var tbody = document.querySelector('#eht-table tbody');
    tbody.innerHTML = '';
    rows.forEach(function(row) {
        var tr = document.createElement('tr');
        row.forEach(function(cell) {
            var td = document.createElement('td');
            td.textContent = cell;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function updateSerialStatus(status) {
    var btn = document.getElementById('btn-connect');
    var st = document.getElementById('status-text');
    if (status === 'connected') {
        connected = true;
        btn.textContent = '■ 断开';
        btn.classList.add('connected');
        st.textContent = '已连接';
    } else if (status === 'error') {
        connected = false;
        btn.textContent = '● 连接';
        btn.classList.remove('connected');
        st.textContent = '错误';
    } else {
        connected = false;
        btn.textContent = '● 连接';
        btn.classList.remove('connected');
        st.textContent = (status === 'disconnected') ? '已断开' : '未连接';
    }
}

// ═══════════════════════════════════════════════
// 用户操作
// ═══════════════════════════════════════════════
function toggleConnect() {
    if (!wailsReady) { alert('应用未就绪，请稍候'); return; }
    if (connected) { disconnect(); } else { connect(); }
}

async function connect() {
    var port = document.getElementById('port-select').value;
    if (!port) { alert('请先选择串口'); return; }
    var baud = parseInt(document.getElementById('baud-select').value) || 115200;
    log('连接串口: ' + port + ' @ ' + baud);
    try {
        await window.go.main.App.Connect(port, baud);
        log('Connect() 返回成功');
    } catch(e) {
        log('Connect() 失败: ' + e);
        alert('连接失败: ' + e);
    }
}

async function disconnect() {
    log('断开连接');
    try { await window.go.main.App.Disconnect(); } catch(e) { log('Disconnect 错误: ' + e); }
}

async function refreshPorts() {
    if (!wailsReady) return;
    try {
        var ports = await window.go.main.App.ListPorts();
        log('获取串口列表', ports);
        var select = document.getElementById('port-select');
        select.innerHTML = '<option value="">-- 选择串口 --</option>';
        if (ports && ports.length > 0) {
            ports.forEach(function(p) {
                var opt = document.createElement('option');
                opt.value = p; opt.textContent = p;
                select.appendChild(opt);
            });
            select.value = ports[0];
        }
    } catch(e) {
        log('ListPorts 错误: ' + e);
    }
}

async function replayFile() {
    if (!wailsReady) { alert('应用未就绪'); return; }
    try {
        var filepath = await window.go.main.App.OpenFileDialog();
        if (filepath) {
            log('回放文件: ' + filepath);
            document.getElementById('status-text').textContent = '回放中...';
            await window.go.main.App.ReplayFile(filepath);
            document.getElementById('status-text').textContent = '文件回放完成';
        }
    } catch(e) {
        log('ReplayFile 错误: ' + e);
        alert('回放失败: ' + e);
    }
}

async function clearAll() {
    log('清空全部数据');
    chartData = [];
    if (chart) { chart.setOption({ series: [{ data: [] }] }); }
    try { if (wailsReady) await window.go.main.App.ClearData(); } catch(e) {}
    document.getElementById('serial').textContent = '-';
    document.getElementById('instype').textContent = '-';
    document.getElementById('firmware').textContent = '-';
    document.getElementById('mode-val').textContent = '-';
    document.getElementById('cur-val').textContent = '-.---';
    document.getElementById('count-text').textContent = '0';
    document.getElementById('last-text').textContent = '-';
    document.querySelector('#eht-table tbody').innerHTML = '';
}

function clearChartData() {
    chartData = [];
    if (chart) { chart.setOption({ series: [{ data: [] }] }); }
}

// ═══════════════════════════════════════════════
// 调试面板
// ═══════════════════════════════════════════════
var debugLines = [];
var debugMaxLines = 200;
var debugVisible = false;

function toggleDebug() {
    debugVisible = !debugVisible;
    var panel = document.getElementById('debug-panel');
    var btn = document.getElementById('btn-debug');
    if (debugVisible) {
        panel.style.display = 'block';
        btn.style.background = '#d93025';
        btn.style.color = '#fff';
        btn.textContent = '隐藏';
    } else {
        panel.style.display = 'none';
        btn.style.background = '';
        btn.style.color = '';
        btn.textContent = '调试';
    }
}

function appendDebug(msg) {
    if (!msg) return;
    debugLines.push(msg);
    if (debugLines.length > debugMaxLines) {
        debugLines.splice(0, debugLines.length - debugMaxLines);
    }
    var el = document.getElementById('debug-log');
    if (el) {
        el.textContent = debugLines.join('\n');
        el.scrollTop = el.scrollHeight;
    }
}

function clearDebugLog() {
    debugLines = [];
    var el = document.getElementById('debug-log');
    if (el) el.textContent = '';
}
