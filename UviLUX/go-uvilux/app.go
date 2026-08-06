package main

import (
	"context"
	"fmt"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App 主应用结构体（方法绑定到前端）
type App struct {
	ctx    context.Context
	parser *DataParser
	logger *Logger
	worker *SerialWorker

	// 传感器信息
	sensorInfo SensorInfo

	// 统计数据
	dataCount   int
	currentMode string

	// EHT 系数
	ehtRows [][]string
}

// SensorInfo 传感器上电信息
type SensorInfo struct {
	SerialNumber    string `json:"serialNumber"`
	InstrumentType  string `json:"instrumentType"`
	FirmwareVersion string `json:"firmwareVersion"`
}

// NewApp 创建应用实例
func NewApp() *App {
	return &App{
		parser:      NewDataParser(),
		logger:      NewLogger(),
		currentMode: "-",
		ehtRows:     make([][]string, 0),
	}
}

// debugLog 输出调试信息到控制台和前端
func (a *App) debugLog(format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	// 输出到控制台（dev 模式可见）
	fmt.Println("[UviLUX]", msg)
	// 推送到前端调试面板
	if a.ctx != nil {
		ts := time.Now().Format("15:04:05.000")
		runtime.EventsEmit(a.ctx, "debug", ts+" "+msg)
	}
	runtime.LogPrint(a.ctx, msg)
}

// startup Wails 启动回调
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
	a.debugLog("应用启动完成")
}

// shutdown Wails 关闭回调
func (a *App) shutdown(ctx context.Context) {
	if a.worker != nil {
		a.worker.Stop()
	}
	a.logger.Close()
}

// ─────────────────────────────────────────────────
// 导出给前端的方法
// ─────────────────────────────────────────────────

// Connect 连接串口
func (a *App) Connect(port string, baudrate int) error {
	// 先断开已有连接
	if a.worker != nil {
		a.worker.Stop()
	}

	// 清空旧数据
	a.clearData()

	// 创建新的 worker
	a.worker = NewSerialWorker(port, baudrate)

	// 设置回调
	a.worker.OnStatus(func(status string) {
		a.debugLog("串口状态: %s", status)
		runtime.EventsEmit(a.ctx, "serial-status", status)

		switch status {
		case "connected":
			a.debugLog("串口 %s 已打开", port)
			a.logger.Open()
			runtime.EventsEmit(a.ctx, "log-status", map[string]string{
				"filename": a.logger.Basename(),
				"status":   "opened",
			})
		case "disconnected":
			a.debugLog("串口 %s 已关闭", port)
			a.logger.Close()
			runtime.EventsEmit(a.ctx, "log-status", map[string]string{
				"status": "closed",
			})
			// 其他状态（如 "error"）可在此添加，或忽略
		}
	})

	a.worker.OnData(func(line string) {
		a.debugLog("收到报文: %s", line)
		a.processLine(line)
	})

	a.worker.OnError(func(err error) {
		a.debugLog("串口错误: %v", err)
		runtime.EventsEmit(a.ctx, "serial-error", err.Error())
	})

	// 启动串口
	return a.worker.Start()
}

// Disconnect 断开串口
func (a *App) Disconnect() {
	if a.worker != nil {
		a.worker.Stop()
		a.worker = nil
	}
}

// ListPorts 获取可用串口列表
func (a *App) ListPorts() []string {
	return ListPorts()
}

// OpenFileDialog 打开文件选择对话框，返回所选文件路径
func (a *App) OpenFileDialog() (string, error) {
	filepath, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "选择数据日志文件",
		Filters: []runtime.FileFilter{
			{DisplayName: "Text files (*.txt)", Pattern: "*.txt"},
		},
	})
	if err != nil {
		a.debugLog("文件对话框错误: %v", err)
		return "", err
	}
	a.debugLog("用户选择了文件: %s", filepath)
	return filepath, nil
}

// ReplayFile 文件回放（由前端触发文件选择后传路径）
func (a *App) ReplayFile(filepath string) error {
	a.Disconnect()
	a.clearData()

	data, err := os.ReadFile(filepath)
	if err != nil {
		return fmt.Errorf("读取文件失败: %w", err)
	}

	lines := strings.Split(string(data), "\n")
	tsRe := regexp.MustCompile(
		`^\[(\d{4}-\d{2}-\d{2}\s+)?(\d{2}:\d{2}:\d{2}\.\d{3})\]`,
	)

	// 累积结果，最后一次性推送
	type point struct {
		X float64 `json:"x"`
		Y float64 `json:"y"`
	}
	var points []point

	for _, rawLine := range lines {
		line := strings.TrimSpace(rawLine)
		if line == "" {
			continue
		}

		var ts time.Time
		if m := tsRe.FindStringSubmatch(line); m != nil {
			tsStr := m[0][1 : len(m[0])-1]
			if parsed, err := time.Parse("2006-01-02 15:04:05.000", tsStr); err == nil {
				ts = parsed
			} else if parsed, err := time.Parse("15:04:05.000", tsStr); err == nil {
				ts = parsed
			}
			line = line[len(m[0]):]
		}

		line = cleanLine(line)
		if line == "" {
			continue
		}

		result := a.parser.Parse(line)

		switch result.Type {
		case "measurement":
			if ts.IsZero() {
				ts = time.Now()
			}
			a.dataCount++
			a.currentMode = result.Mode
			points = append(points, point{
				X: float64(ts.UnixNano()) / 1e9,
				Y: result.Value,
			})

		case "eht":
			a.ehtRows = append(a.ehtRows, []string{
				result.Wavelength, result.C1, result.C2, result.C3,
			})

		case "info":
			switch result.Key {
			case "serial_number":
				a.sensorInfo.SerialNumber = result.Info
			case "instrument_type":
				a.sensorInfo.InstrumentType = result.Info
			case "firmware_version":
				a.sensorInfo.FirmwareVersion = result.Info
			}
		}
	}

	// 一次性推送所有结果到前端
	runtime.EventsEmit(a.ctx, "replay-data", map[string]interface{}{
		"points":     points,
		"sensorInfo": a.sensorInfo,
		"ehtRows":    a.ehtRows,
		"dataCount":  a.dataCount,
		"mode":       a.currentMode,
	})

	return nil
}

// ClearData 清空数据
func (a *App) ClearData() {
	a.clearData()
	runtime.EventsEmit(a.ctx, "clear-chart", nil)
}

// ─────────────────────────────────────────────────
// 内部方法
// ─────────────────────────────────────────────────

// clearData 清空所有数据状态
func (a *App) clearData() {
	a.sensorInfo = SensorInfo{}
	a.ehtRows = make([][]string, 0)
	a.dataCount = 0
	a.currentMode = "-"
	a.parser.Reset()
}

// processLine 处理一行数据并推送事件
func (a *App) processLine(line string) {
	// 记录日志
	a.logger.Write(line)

	// 解析
	result := a.parser.Parse(line)

	switch result.Type {
	case "measurement":
		a.dataCount++
		a.currentMode = result.Mode
		runtime.EventsEmit(a.ctx, "measurement", map[string]interface{}{
			"timestamp": time.Now().UnixNano() / 1e9,
			"value":     result.Value,
			"mode":      result.Mode,
			"count":     a.dataCount,
			"status":    result.Status,
		})

	case "eht":
		a.ehtRows = append(a.ehtRows, []string{
			result.Wavelength, result.C1, result.C2, result.C3,
		})
		a.debugLog("EHT系数: λ=%s C1=%s C2=%s C3=%s", result.Wavelength, result.C1, result.C2, result.C3)
		runtime.EventsEmit(a.ctx, "eht-update", a.ehtRows)

	case "info":
		switch result.Key {
		case "serial_number":
			a.sensorInfo.SerialNumber = result.Info
			a.debugLog("传感器信息: 序列号=%s", result.Info)
		case "instrument_type":
			a.sensorInfo.InstrumentType = result.Info
			a.debugLog("传感器信息: 类型=%s", result.Info)
		case "firmware_version":
			a.sensorInfo.FirmwareVersion = result.Info
			a.debugLog("传感器信息: 固件=%s", result.Info)
		default:
			a.debugLog("传感器信息: %s=%s", result.Key, result.Info)
		}
		runtime.EventsEmit(a.ctx, "info-update", a.sensorInfo)

	case "unknown":
		a.debugLog("未识别报文: %s", line)

		// "unknown" 忽略
	}
}
