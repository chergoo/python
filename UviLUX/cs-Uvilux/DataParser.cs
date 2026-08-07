using System;
using System.Globalization;
using System.Text.RegularExpressions;

namespace UviLUX_CS
{
    public class DataParser
    {
        private const string NumberPattern = @"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?";
        private static readonly Regex MeasurementRegex = new($@"^\s*({NumberPattern})\s*,\s*(\d+)\s*,\s*(\d+)\s*$");
        private static readonly Regex EhtRegex = new($@"^\s*(\d+)\s*,\s*({NumberPattern})\s*,\s*({NumberPattern})\s*,\s*(\d+)\s*$");
        private static readonly Regex SerialRegex = new(@"^\d{6}-\d{3}$");

        public void Reset() { }

        public ParseResult Parse(string line)
        {
            // 测量数据
            var m = MeasurementRegex.Match(line);
            if (m.Success && double.TryParse(m.Groups[1].Value, NumberStyles.Float,
                CultureInfo.InvariantCulture, out var measurement))
            {
                return new ParseResult
                {
                    Type = ParseResultType.Measurement,
                    Value = measurement,
                    Mode = m.Groups[2].Value,
                    Status = m.Groups[3].Value
                };
            }

            // EHT 系数
            var e = EhtRegex.Match(line);
            if (e.Success)
            {
                return new ParseResult
                {
                    Type = ParseResultType.Eht,
                    Wavelength = e.Groups[1].Value,
                    C1 = e.Groups[2].Value,
                    C2 = e.Groups[3].Value,
                    C3 = e.Groups[4].Value
                };
            }

            // EHT header
            if (line.IndexOf("EHT", StringComparison.OrdinalIgnoreCase) >= 0 &&
                line.IndexOf("Coefficient", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                return new ParseResult { Type = ParseResultType.Info, Key = "eht_header", ValueStr = line };
            }

            // 序列号
            if (SerialRegex.IsMatch(line))
            {
                return new ParseResult { Type = ParseResultType.Info, Key = "serial_number", ValueStr = line };
            }

            // Instrument Type
            if (line.IndexOf("Instrument Type", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                var val = line;
                if (line.IndexOf('-') >= 0)
                    val = line.Split('-')[1].Trim();
                return new ParseResult { Type = ParseResultType.Info, Key = "instrument_type", ValueStr = val };
            }

            // Firmware Version
            if (line.IndexOf("Code Version", StringComparison.OrdinalIgnoreCase) >= 0 ||
                line.IndexOf("Version", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                var val = line;
                if (line.IndexOf('-') >= 0)
                    val = line.Split('-')[1].Trim();
                return new ParseResult { Type = ParseResultType.Info, Key = "firmware_version", ValueStr = val };
            }

            // Sensor name / brand
            if (line.IndexOf("UviLux", StringComparison.OrdinalIgnoreCase) >= 0)
                return new ParseResult { Type = ParseResultType.Info, Key = "sensor_name", ValueStr = line.Trim('*', ' ') };
            if (line.IndexOf("chelsea", StringComparison.OrdinalIgnoreCase) >= 0)
                return new ParseResult { Type = ParseResultType.Info, Key = "brand", ValueStr = line.Trim('*', ' ') };

            return new ParseResult { Type = ParseResultType.Unknown, Raw = line };
        }
    }

    public enum ParseResultType { Measurement, Eht, Info, Unknown }

    public class ParseResult
    {
        public ParseResultType Type { get; set; }
        public double Value { get; set; }
        public string Mode { get; set; } = "";
        public string Status { get; set; } = "";
        public string Wavelength { get; set; } = "";
        public string C1 { get; set; } = "";
        public string C2 { get; set; } = "";
        public string C3 { get; set; } = "";
        public string Key { get; set; } = "";
        public string ValueStr { get; set; } = "";
        public string Raw { get; set; } = "";
    }
}
