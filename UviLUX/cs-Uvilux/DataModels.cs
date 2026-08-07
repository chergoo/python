using System.Collections.Generic;

namespace UviLUX_CS
{
    public class SensorInfo
    {
        public string SerialNumber { get; set; } = "";
        public string InstrumentType { get; set; } = "";
        public string FirmwareVersion { get; set; } = "";
        public List<EhtCoefficient> EhtCoefficients { get; } = new();

        public bool IsComplete => !string.IsNullOrEmpty(SerialNumber) && EhtCoefficients.Count > 0;

        public void Reset()
        {
            SerialNumber = "";
            InstrumentType = "";
            FirmwareVersion = "";
            EhtCoefficients.Clear();
        }
    }

    public class EhtCoefficient
    {
        public string Wavelength { get; set; } = "";
        public string C1 { get; set; } = "";
        public string C2 { get; set; } = "";
        public string C3 { get; set; } = "";
    }
}
