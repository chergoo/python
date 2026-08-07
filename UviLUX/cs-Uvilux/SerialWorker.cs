using System;
using System.ComponentModel;
using System.IO.Ports;
using System.Threading;

namespace UviLUX_CS
{
    public class SerialWorker : BackgroundWorker
    {
        private readonly string _port;
        private readonly int _baudrate;
        private SerialPort? _serialPort;
        private readonly object _lock = new();

        public event EventHandler<string>? DataReceived;
        public event EventHandler<string>? ErrorOccurred;
        public event EventHandler? Connected;
        public event EventHandler? Disconnected;

        public bool IsConnected { get; private set; }
        public string PortName => _port;

        public SerialWorker(string port, int baudrate)
        {
            _port = port;
            _baudrate = baudrate;
            WorkerSupportsCancellation = true;
            DoWork += SerialWorker_DoWork;
        }

        private void SerialWorker_DoWork(object? sender, DoWorkEventArgs e)
        {
            try
            {
                _serialPort = new SerialPort(_port, _baudrate, Parity.None, 8, StopBits.One);
                _serialPort.ReadTimeout = 500;
                _serialPort.Open();
                IsConnected = true;
                Connected?.Invoke(this, EventArgs.Empty);
                var frameAssembler = new SerialFrameAssembler();

                while (!CancellationPending)
                {
                    try
                    {
                        var serialPort = _serialPort;
                        if (serialPort == null)
                            break;

                        if (serialPort.BytesToRead == 0)
                        {
                            Thread.Sleep(20);
                            continue;
                        }

                        var chunk = serialPort.ReadExisting();
                        foreach (var frame in frameAssembler.Append(chunk))
                            DataReceived?.Invoke(this, frame);
                    }
                    catch (TimeoutException) { /* 超时继续 */ }
                    catch (Exception ex)
                    {
                        ErrorOccurred?.Invoke(this, ex.Message);
                        break;
                    }
                }
            }
            catch (Exception ex)
            {
                ErrorOccurred?.Invoke(this, $"无法打开串口 {_port}: {ex.Message}");
            }
            finally
            {
                ClosePort();
                IsConnected = false;
                Disconnected?.Invoke(this, EventArgs.Empty);
            }
        }

        public void Stop()
        {
            CancelAsync();
            ClosePort();
        }

        private void ClosePort()
        {
            lock (_lock)
            {
                if (_serialPort != null)
                {
                    try
                    {
                        if (_serialPort.IsOpen)
                            _serialPort.Close();
                    }
                    catch { }
                    _serialPort.Dispose();
                    _serialPort = null;
                }
            }
        }
    }
}
