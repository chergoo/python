using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace UviLUX_CS
{
    /// <summary>Splits the UviLUX serial byte stream into complete protocol records.</summary>
    internal sealed class SerialFrameAssembler
    {
        private const string SensorHeader = "** UviLux **";
        private const string EhtHeader = "EHT Coefficients";
        private const string InstrumentPrefix = "chelsea Instrument Type - ";
        private const string VersionPrefix = "Code Version - ";

        private static readonly Regex EhtFrameRegex = new(
            @"^\d{3},[+-]\d\.\d{5}E[+-]\d{2},[+-]\d\.\d{5}E[+-]\d{2},\d{5}");
        private static readonly Regex MeasurementFrameRegex = new(
            @"^[+-]\d{3}\.\d{3},\d{3},\d{2}");
        private static readonly Regex SerialNumberRegex = new(@"^\d{6}-\d{3}");

        private readonly StringBuilder _buffer = new();

        public IEnumerable<string> Append(string data)
        {
            if (string.IsNullOrEmpty(data))
                yield break;

            _buffer.Append(data.Replace("\0", string.Empty));
            while (TryExtractLine(out var frame) || TryExtractProtocolFrame(out frame))
            {
                if (!string.IsNullOrWhiteSpace(frame))
                    yield return frame.Trim();
            }
        }

        private bool TryExtractLine(out string frame)
        {
            var newlineIndex = IndexOf('\n');
            if (newlineIndex < 0)
            {
                frame = string.Empty;
                return false;
            }

            frame = _buffer.ToString(0, newlineIndex).TrimEnd('\r');
            _buffer.Remove(0, newlineIndex + 1);
            return true;
        }

        private bool TryExtractProtocolFrame(out string frame)
        {
            TrimLeadingWhitespace();
            var content = _buffer.ToString();

            if (content.StartsWith(SensorHeader, StringComparison.OrdinalIgnoreCase))
                return Extract(SensorHeader.Length, out frame);

            var serialNumber = SerialNumberRegex.Match(content);
            if (serialNumber.Success)
                return Extract(serialNumber.Length, out frame);

            if (content.StartsWith(EhtHeader, StringComparison.OrdinalIgnoreCase))
                return Extract(EhtHeader.Length, out frame);

            var eht = EhtFrameRegex.Match(content);
            if (eht.Success)
                return Extract(eht.Length, out frame);

            var measurement = MeasurementFrameRegex.Match(content);
            if (measurement.Success)
                return Extract(measurement.Length, out frame);

            if (content.StartsWith(InstrumentPrefix, StringComparison.OrdinalIgnoreCase))
            {
                var next = content.IndexOf(VersionPrefix, InstrumentPrefix.Length, StringComparison.OrdinalIgnoreCase);
                if (next >= 0)
                    return Extract(next, out frame);
            }

            if (content.StartsWith(VersionPrefix, StringComparison.OrdinalIgnoreCase))
            {
                var next = content.IndexOf(EhtHeader, VersionPrefix.Length, StringComparison.OrdinalIgnoreCase);
                if (next >= 0)
                    return Extract(next, out frame);
            }

            frame = string.Empty;
            return false;
        }

        private bool Extract(int length, out string frame)
        {
            frame = _buffer.ToString(0, length);
            _buffer.Remove(0, length);
            return true;
        }

        private void TrimLeadingWhitespace()
        {
            var index = 0;
            while (index < _buffer.Length && char.IsWhiteSpace(_buffer[index]))
                index++;
            if (index > 0)
                _buffer.Remove(0, index);
        }

        private int IndexOf(char value)
        {
            for (var i = 0; i < _buffer.Length; i++)
            {
                if (_buffer[i] == value)
                    return i;
            }
            return -1;
        }
    }
}
