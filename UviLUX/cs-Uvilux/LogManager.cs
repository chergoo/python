using System;
using System.IO;

namespace UviLUX_CS
{
    public class LogManager : IDisposable
    {
        private StreamWriter? _writer;
        private readonly string _logDir;
        public string CurrentFilePath { get; private set; } = "";

        public LogManager()
        {
            var desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
            _logDir = Path.Combine(desktop, "UviLUX_logs");
            Directory.CreateDirectory(_logDir);
        }

        public void OpenNewLog()
        {
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            CurrentFilePath = Path.Combine(_logDir, $"uvilux_{timestamp}.txt");
            _writer = new StreamWriter(CurrentFilePath, false, System.Text.Encoding.UTF8);
            _writer.WriteLine($"# UviLUX 原始数据日志");
            _writer.WriteLine($"# 开始时间: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
            _writer.WriteLine($"# ==========");
            _writer.Flush();
        }

        public void WriteLine(string line)
        {
            if (_writer != null)
            {
                var ts = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
                _writer.WriteLine($"[{ts}] {line}");
                _writer.Flush();
            }
        }

        public void Close()
        {
            if (_writer != null)
            {
                _writer.WriteLine($"# ==========");
                _writer.WriteLine($"# 结束时间: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
                _writer.Close();
                _writer.Dispose();
                _writer = null;
            }
        }

        public void Dispose() => Close();
    }
}