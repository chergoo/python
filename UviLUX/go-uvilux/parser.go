package main

import (
	"regexp"
	"strconv"
	"strings"
)

// ParseResult 解析结果类型
type ParseResult struct {
	Type string // "measurement", "eht", "info", "unknown"
	Value  float64
	Mode   string
	Status string
	Wavelength string
	C1, C2, C3 string
	Key   string
	Info  string
	Raw   string
}

// DataParser 传感器数据解析器
type DataParser struct {
	reMeasurement *regexp.Regexp
	reEHT         *regexp.Regexp
	reSerial      *regexp.Regexp
	inEHTSection  bool
}

// NewDataParser 创建解析器
func NewDataParser() *DataParser {
	return &DataParser{
		reMeasurement: regexp.MustCompile(`^([+-]?\d+\.\d+),(\d+),(\d+)$`),
		reEHT: regexp.MustCompile(
			`^\s*(\d+)\s*,\s*([+\-][\d.]+(?:E[+\-]\d+)?)\s*,\s*`+
				`([+\-][\d.]+(?:E[+\-]\d+)?)\s*,\s*(\d+)\s*$`,
		),
		reSerial: regexp.MustCompile(`^\d{6}-\d{3}$`),
	}
}

func (p *DataParser) Reset() { p.inEHTSection = false }

// cleanLine 剥离串口监视器前缀，找到传感器数据起始字符
func cleanLine(line string) string {
	line = strings.TrimSpace(line)
	if line == "" {
		return line
	}
	for i, r := range line {
		if (r >= '0' && r <= '9') || r == '+' || r == '-' || r == '*' || r == ' ' ||
			(r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') {
			return line[i:]
		}
	}
	return line
}

// Parse 解析一行数据
func (p *DataParser) Parse(line string) ParseResult {
	line = cleanLine(line)
	if line == "" {
		return ParseResult{Type: "unknown", Raw: line}
	}

	// ── 测量数据: +057.957,600,00 ──
	if m := p.reMeasurement.FindStringSubmatch(line); m != nil {
		val, _ := strconv.ParseFloat(m[1], 64)
		return ParseResult{
			Type: "measurement", Value: val,
			Mode: m[2], Status: m[3],
		}
	}

	// ── EHT 校准系数 ──
	if m := p.reEHT.FindStringSubmatch(line); m != nil {
		return ParseResult{
			Type: "eht",
			Wavelength: m[1], C1: m[2], C2: m[3], C3: m[4],
		}
	}

	// ── EHT Coefficients 标记头 ──
	upper := strings.ToUpper(line)
	if strings.Contains(upper, "EHT") && strings.Contains(upper, "COEFFICIENT") {
		p.inEHTSection = true
		return ParseResult{Type: "info", Key: "eht_header", Info: line}
	}

	// ── 序列号 ──
	if p.reSerial.MatchString(line) {
		return ParseResult{Type: "info", Key: "serial_number", Info: line}
	}

	// ── 仪器类型 ──
	if strings.Contains(upper, "INSTRUMENT TYPE") {
		value := line
		if idx := strings.Index(line, "-"); idx >= 0 {
			value = strings.TrimSpace(line[idx+1:])
		}
		return ParseResult{Type: "info", Key: "instrument_type", Info: value}
	}

	// ── 固件版本 ──
	if strings.Contains(upper, "CODE VERSION") || strings.Contains(upper, "VERSION") {
		value := line
		if idx := strings.Index(line, "-"); idx >= 0 {
			value = strings.TrimSpace(line[idx+1:])
		}
		return ParseResult{Type: "info", Key: "firmware_version", Info: value}
	}

	// ── 传感器名称头 ──
	if strings.Contains(line, "UviLux") || strings.Contains(upper, "UVILUX") {
		return ParseResult{Type: "info", Key: "sensor_name", Info: strings.Trim(line, "* ")}
	}
	if strings.Contains(strings.ToLower(line), "chelsea") {
		return ParseResult{Type: "info", Key: "brand", Info: strings.Trim(line, "* ")}
	}

	return ParseResult{Type: "unknown", Raw: line}
}
