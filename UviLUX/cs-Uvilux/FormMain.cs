using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.IO.Ports;
using System.Linq;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using ScottPlot;

namespace UviLUX_CS
{
    public partial class FormMain : Form
    {
        private const int MaxDataPoints = 300;
        private readonly ConcurrentQueue<(string Type, string Payload)> _rxQueue = new();
        private SerialWorker? _worker;
        private readonly SensorInfo _sensorInfo = new();
        private readonly DataParser _parser = new();
        private readonly LogManager _logManager = new();

        private readonly List<DateTime> _timestamps = new();
        private readonly List<double> _measurements = new();
        private int _dataCount = 0;
        private string _currentMode = "-";

        // UI 控件（设计器生成，此处只声明）
        private Label lblSerial = null!, lblType = null!, lblFw = null!;
        private TreeView treeEht = null!;
        private Label lblModeValue = null!, lblModeLabel = null!;
        private FormsPlot plot = null!;
        private ComboBox comboPort = null!, comboBaud = null!;
        private Button btnConnect = null!, btnDisconnect = null!, btnReplay = null!, btnRefresh = null!, btnClear = null!;
        private Label lblStatus = null!, lblCount = null!, lblLast = null!, lblLog = null!;

        public FormMain()
        {
            InitializeComponent();
            SetupUI();
            RefreshPorts();
            Application.ApplicationExit += (s, e) => _logManager.Close();
        }

        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(FormMain));
            SuspendLayout();
            // 
            // FormMain
            // 
            ClientSize = new Size(1082, 673);
            if (resources.GetObject("$this.Icon") is Icon icon)
                Icon = icon;
            MinimumSize = new Size(900, 600);
            Name = "FormMain";
            Text = "UviLUX 传感器上位机";
            ResumeLayout(false);
        }

        private void SetupUI()
        {
            // 使用 TableLayoutPanel 布局
            var mainLayout = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 5,
                Padding = new Padding(8)
            };
            mainLayout.RowStyles.Add(new RowStyle(SizeType.AutoSize)); // 信息面板
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Absolute, 150)); // EHT + 模式（原约 100px，增加 50%）
            mainLayout.RowStyles.Add(new RowStyle(SizeType.Percent, 100)); // 图表
            mainLayout.RowStyles.Add(new RowStyle(SizeType.AutoSize)); // 控制栏
            mainLayout.RowStyles.Add(new RowStyle(SizeType.AutoSize)); // 状态栏
            this.Controls.Add(mainLayout);

            // ---- 信息面板 ----
            var infoPanel = new GroupBox { Text = "传感器信息", Padding = new Padding(8), Dock = DockStyle.Fill };
            mainLayout.Controls.Add(infoPanel, 0, 0);

            var infoLayout = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight };
            infoPanel.Controls.Add(infoLayout);
            infoLayout.Controls.Add(new Label { Text = "序列号:", AutoSize = true });
            lblSerial = new Label { Text = "-", Font = new Font("Consolas", 11, FontStyle.Bold), AutoSize = true };
            infoLayout.Controls.Add(lblSerial);
            infoLayout.Controls.Add(new Label { Text = "仪器类型:", AutoSize = true, Margin = new Padding(20, 0, 0, 0) });
            lblType = new Label { Text = "-", AutoSize = true };
            infoLayout.Controls.Add(lblType);
            infoLayout.Controls.Add(new Label { Text = "固件版本:", AutoSize = true, Margin = new Padding(20, 0, 0, 0) });
            lblFw = new Label { Text = "-", AutoSize = true };
            infoLayout.Controls.Add(lblFw);

            // ---- EHT + 模式面板 ----
            var ehtModePanel = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2, RowCount = 1 };
            ehtModePanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));
            ehtModePanel.ColumnStyles.Add(new ColumnStyle(SizeType.AutoSize));
            mainLayout.Controls.Add(ehtModePanel, 0, 1);

            // EHT 表格
            var ehtGroup = new GroupBox { Text = "EHT 校准系数", Padding = new Padding(4), Dock = DockStyle.Fill };
            ehtModePanel.Controls.Add(ehtGroup, 0, 0);
            treeEht = new TreeView { Dock = DockStyle.Fill, Height = 150, ShowRootLines = false };
            ehtGroup.Controls.Add(treeEht);

            // 模式显示
            var modeGroup = new GroupBox { Text = "测量模式", Padding = new Padding(8), Dock = DockStyle.Fill, Width = 180 };
            ehtModePanel.Controls.Add(modeGroup, 1, 0);
            var modeFlow = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown };
            modeGroup.Controls.Add(modeFlow);
            lblModeValue = new Label { Text = "-", Font = new Font("Consolas", 28, FontStyle.Bold), AutoSize = true };
            modeFlow.Controls.Add(lblModeValue);
            lblModeLabel = new Label { Text = "Gain", AutoSize = true };
            modeFlow.Controls.Add(lblModeLabel);

            // ---- 图表 ----
            var chartGroup = new GroupBox { Text = "实时测量数据", Padding = new Padding(4), Dock = DockStyle.Fill };
            mainLayout.Controls.Add(chartGroup, 0, 2);
            plot = new FormsPlot { Dock = DockStyle.Fill };
            chartGroup.Controls.Add(plot);
            plot.Plot.Title("测量值");
            plot.Plot.YLabel("测量值");
            plot.Plot.XLabel("时间");
            plot.Plot.Grid(true);

            // ---- 控制栏 ----
            var ctrlPanel = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(6) };
            mainLayout.Controls.Add(ctrlPanel, 0, 3);

            ctrlPanel.Controls.Add(new Label { Text = "串口:", AutoSize = true });
            comboPort = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Width = 120 };
            ctrlPanel.Controls.Add(comboPort);
            ctrlPanel.Controls.Add(new Label { Text = "波特率:", AutoSize = true });
            comboBaud = new ComboBox { DropDownStyle = ComboBoxStyle.DropDownList, Width = 100 };
            comboBaud.Items.AddRange(new object[] { "9600", "19200", "38400", "57600", "115200", "230400" });
            comboBaud.SelectedItem = "9600";
            ctrlPanel.Controls.Add(comboBaud);

            btnConnect = new Button { Text = "● 连接", Width = 80 };
            btnConnect.Click += BtnConnect_Click;
            ctrlPanel.Controls.Add(btnConnect);

            btnDisconnect = new Button { Text = "断开", Width = 80, Enabled = false };
            btnDisconnect.Click += BtnDisconnect_Click;
            ctrlPanel.Controls.Add(btnDisconnect);

            btnReplay = new Button { Text = "📁 文件回放", Width = 100 };
            btnReplay.Click += BtnReplay_Click;
            ctrlPanel.Controls.Add(btnReplay);

            btnRefresh = new Button { Text = "刷新", Width = 70 };
            btnRefresh.Click += (s, e) => RefreshPorts();
            ctrlPanel.Controls.Add(btnRefresh);

            btnClear = new Button { Text = "清空图表", Width = 90, Dock = DockStyle.Right };
            btnClear.Click += (s, e) => ClearChart();
            ctrlPanel.Controls.Add(btnClear);

            // ---- 状态栏 ----
            var statusPanel = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.LeftToRight, Padding = new Padding(4) };
            mainLayout.Controls.Add(statusPanel, 0, 4);
            lblStatus = new Label { Text = "状态: 未连接", BorderStyle = BorderStyle.Fixed3D, AutoSize = false, Width = 200 };
            statusPanel.Controls.Add(lblStatus);
            lblCount = new Label { Text = "数据: 0 条", BorderStyle = BorderStyle.Fixed3D, AutoSize = false, Width = 100 };
            statusPanel.Controls.Add(lblCount);
            lblLast = new Label { Text = "最后更新: -", BorderStyle = BorderStyle.Fixed3D, AutoSize = false, Width = 120 };
            statusPanel.Controls.Add(lblLast);
            lblLog = new Label { Text = "日志: -", BorderStyle = BorderStyle.Fixed3D, AutoSize = false, Width = 200 };
            statusPanel.Controls.Add(lblLog);
        }

        // ---- 串口操作 ----
        private void RefreshPorts()
        {
            var ports = SerialPort.GetPortNames();
            comboPort.Items.Clear();
            comboPort.Items.AddRange(ports);
            if (ports.Length > 0) comboPort.SelectedIndex = 0;
        }

        private void BtnConnect_Click(object? sender, EventArgs e)
        {
            if (_worker != null && _worker.IsBusy)
                return;

            var port = comboPort.SelectedItem?.ToString();
            if (string.IsNullOrEmpty(port))
            {
                MessageBox.Show("请先选择串口", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            if (!int.TryParse(comboBaud.SelectedItem?.ToString(), out int baud))
                baud = 115200;

            ConnectSerial(port, baud);
        }

        private void ConnectSerial(string port, int baud)
        {
            Disconnect();
            ClearData();

            _worker = new SerialWorker(port, baud);
            _worker.DataReceived += OnDataReceived;
            _worker.ErrorOccurred += OnErrorOccurred;
            _worker.Connected += OnConnected;
            _worker.Disconnected += OnDisconnected;
            _worker.RunWorkerAsync();
        }

        private void Disconnect()
        {
            if (_worker != null)
            {
                _worker.Stop();
                _worker.DataReceived -= OnDataReceived;
                _worker.ErrorOccurred -= OnErrorOccurred;
                _worker.Connected -= OnConnected;
                _worker.Disconnected -= OnDisconnected;
                _worker = null;
            }
            SetConnectedState(false);
            _logManager.Close();
            lblLog.Text = "日志: -";
        }

        private void SetConnectedState(bool connected)
        {
            btnConnect.Enabled = !connected;
            btnDisconnect.Enabled = connected;
            if (!connected)
                lblStatus.Text = "状态: 已断开";
        }

        // ---- 事件处理 ----
        private void OnConnected(object? sender, EventArgs e)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => OnConnected(sender, e)));
                return;
            }

            SetConnectedState(true);
            lblStatus.Text = $"状态: 已连接 ({((SerialWorker)sender!).PortName})";
            _logManager.OpenNewLog();
            lblLog.Text = $"日志: {Path.GetFileName(_logManager.CurrentFilePath)}";
        }

        private void OnDisconnected(object? sender, EventArgs e)
        {
            if (InvokeRequired)
            {
                BeginInvoke(new Action(() => OnDisconnected(sender, e)));
                return;
            }

            SetConnectedState(false);
            lblStatus.Text = "状态: 已断开";
            _logManager.Close();
            lblLog.Text = "日志: 已保存";
        }

        private void OnDataReceived(object? sender, string line)
        {
            _rxQueue.Enqueue(("__DATA__", line));
            BeginInvoke(new Action(ProcessQueue));
        }

        private void OnErrorOccurred(object? sender, string msg)
        {
            _rxQueue.Enqueue(("__ERROR__", msg));
            BeginInvoke(new Action(ProcessQueue));
        }

        private void BtnDisconnect_Click(object? sender, EventArgs e) => Disconnect();

        private void BtnReplay_Click(object? sender, EventArgs e)
        {
            using var ofd = new OpenFileDialog
            {
                Title = "选择数据日志文件",
                Filter = "Text files (*.txt)|*.txt|All files (*.*)|*.*",
                InitialDirectory = Environment.GetFolderPath(Environment.SpecialFolder.Desktop)
            };
            if (ofd.ShowDialog() != DialogResult.OK) return;

            Disconnect();
            ClearData();
            _timestamps.Clear();
            _measurements.Clear();

            try
            {
                var lines = File.ReadAllLines(ofd.FileName, System.Text.Encoding.UTF8);
                foreach (var rawLine in lines)
                {
                    var line = rawLine.Trim();
                    if (string.IsNullOrEmpty(line)) continue;

                    // 剥离时间戳
                    var tsMatch = Regex.Match(line, @"^\[(\d{4}-\d{2}-\d{2}\s+)?(\d{2}:\d{2}:\d{2}\.\d{3})\]");
                    DateTime? replayTs = null;
                    if (tsMatch.Success)
                    {
                        var tsStr = tsMatch.Groups[0].Value.Substring(1, tsMatch.Length - 2);
                        if (DateTime.TryParse(tsStr, out var dt))
                            replayTs = dt;
                        line = line.Substring(tsMatch.Length);
                    }
                    line = Regex.Replace(line, @"^[^\x20-\x7E\*一-鿿]+", "");
                    line = line.Trim();
                    if (string.IsNullOrEmpty(line)) continue;

                    ProcessLine(line, replayTs, skipUi: true);
                }

                // 更新 UI
                UpdateChart();
                UpdateInfoDisplay();
                UpdateEhtTable();
                UpdateModeDisplay();
                UpdateStatus();
                lblStatus.Text = $"状态: 文件回放完成 ({Path.GetFileName(ofd.FileName)})";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"回放错误: {ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                lblStatus.Text = "状态: 回放失败";
            }
        }

        private void ClearChart()
        {
            _timestamps.Clear();
            _measurements.Clear();
            UpdateChart();
        }

        // ---- 队列处理 ----
        private void ProcessQueue()
        {
            while (_rxQueue.TryDequeue(out var msg))
            {
                var (type, payload) = msg;
                if (type == "__DATA__")
                    ProcessLine(payload);
                else if (type == "__ERROR__")
                {
                    MessageBox.Show($"串口错误: {payload}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    SetConnectedState(false);
                    lblStatus.Text = "状态: 错误";
                }
            }
        }

        private void ProcessLine(string line, DateTime? timestamp = null, bool skipUi = false)
        {
            _logManager.WriteLine(line);

            var result = _parser.Parse(line);
            switch (result.Type)
            {
                case ParseResultType.Measurement:
                    var value = result.Value;
                    var mode = result.Mode;
                    var now = timestamp ?? DateTime.Now;
                    _timestamps.Add(now);
                    _measurements.Add(value);
                    if (_timestamps.Count > MaxDataPoints)
                    {
                        _timestamps.RemoveAt(0);
                        _measurements.RemoveAt(0);
                    }
                    _currentMode = mode;
                    _dataCount++;
                    if (!skipUi)
                    {
                        UpdateChart();
                        UpdateModeDisplay();
                        UpdateStatus();
                    }
                    break;

                case ParseResultType.Eht:
                    _sensorInfo.EhtCoefficients.Add(new EhtCoefficient
                    {
                        Wavelength = result.Wavelength,
                        C1 = result.C1,
                        C2 = result.C2,
                        C3 = result.C3
                    });
                    if (!skipUi) UpdateEhtTable();
                    break;

                case ParseResultType.Info:
                    switch (result.Key)
                    {
                        case "serial_number": _sensorInfo.SerialNumber = result.ValueStr; break;
                        case "instrument_type": _sensorInfo.InstrumentType = result.ValueStr; break;
                        case "firmware_version": _sensorInfo.FirmwareVersion = result.ValueStr; break;
                    }
                    if (!skipUi) UpdateInfoDisplay();
                    break;
            }
        }

        // ---- UI 更新 ----
        private void UpdateInfoDisplay()
        {
            lblSerial.Text = _sensorInfo.SerialNumber ?? "-";
            lblType.Text = _sensorInfo.InstrumentType ?? "-";
            lblFw.Text = _sensorInfo.FirmwareVersion ?? "-";
        }

        private void UpdateEhtTable()
        {
            treeEht.Nodes.Clear();
            foreach (var e in _sensorInfo.EhtCoefficients)
            {
                var node = new TreeNode($"{e.Wavelength}  A:{e.C1}  B:{e.C2}  C:{e.C3}");
                treeEht.Nodes.Add(node);
            }
        }

        private void UpdateModeDisplay()
        {
            lblModeValue.Text = _currentMode;
        }

        private void UpdateChart()
        {
            var plt = plot.Plot;
            plt.Clear();

            if (_timestamps.Count > 0 && _measurements.Count > 0)
            {
                // 转换为 OHLC 或散点时间序列
                var xs = _timestamps.Select(t => t.ToOADate()).ToArray();
                var ys = _measurements.ToArray();

                var scatter = plt.AddScatter(xs, ys, color: System.Drawing.Color.Blue, lineWidth: 1.2f);
                scatter.Label = "测量值";

                // 标注最新值
                if (ys.Length > 0)
                {
                    var lastX = xs[xs.Length - 1];
                    var lastY = ys[ys.Length - 1];
                    plt.Title($"当前测量值: {lastY:F3}");
                    plt.AddText($"{lastY:F3}", lastX, lastY, 10);
                }

                plt.XAxis.DateTimeFormat(true);
                plt.XAxis.Label("时间");
                plt.YAxis.Label("测量值");
                plt.Grid(true);
                plt.AxisAuto();
            }
            else
            {
                plt.Title("无数据");
            }

            plot.Refresh();
        }

        private void UpdateStatus()
        {
            lblCount.Text = $"数据: {_dataCount} 条";
            if (_timestamps.Count > 0)
                lblLast.Text = $"最后更新: {_timestamps[_timestamps.Count - 1]:HH:mm:ss}";
        }

        private void ClearData()
        {
            _timestamps.Clear();
            _measurements.Clear();
            _dataCount = 0;
            _currentMode = "-";
            _sensorInfo.Reset();
            _parser.Reset();
            UpdateChart();
            UpdateInfoDisplay();
            UpdateEhtTable();
            UpdateModeDisplay();
            UpdateStatus();
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            Disconnect();
            _logManager.Dispose();
            base.OnFormClosing(e);
        }
    }
}
