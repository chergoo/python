package main

import (
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// Logger 日志文件管理器
type Logger struct {
	file     *os.File
	filename string
	logDir   string
}

// NewLogger 创建日志管理器
func NewLogger() *Logger {
	home, _ := os.UserHomeDir()
	logDir := filepath.Join(home, "Desktop", "UviLUX_logs")
	os.MkdirAll(logDir, 0755)
	return &Logger{logDir: logDir}
}

// Open 创建新的日志文件
func (l *Logger) Open() error {
	l.Close()

	timestamp := time.Now().Format("20060102_150405")
	l.filename = filepath.Join(l.logDir, fmt.Sprintf("uvilux_%s.txt", timestamp))

	f, err := os.Create(l.filename)
	if err != nil {
		return fmt.Errorf("无法创建日志文件: %w", err)
	}

	header := fmt.Sprintf("# UviLUX 原始数据日志\n# 开始时间: %s\n# ==========\n",
		time.Now().Format("2006-01-02 15:04:05"))
	f.WriteString(header)
	f.Sync()

	l.file = f
	return nil
}

// Write 写入一行原始数据
func (l *Logger) Write(line string) {
	if l.file == nil {
		return
	}
	ts := time.Now().Format("2006-01-02 15:04:05.000")
	l.file.WriteString(fmt.Sprintf("[%s] %s\n", ts, line))
	l.file.Sync()
}

// Close 关闭日志文件
func (l *Logger) Close() {
	if l.file != nil {
		footer := fmt.Sprintf("# ==========\n# 结束时间: %s\n",
			time.Now().Format("2006-01-02 15:04:05"))
		l.file.WriteString(footer)
		l.file.Close()
		l.file = nil
	}
}

// Basename 返回日志文件名（不含路径）
func (l *Logger) Basename() string {
	if l.filename == "" {
		return "-"
	}
	return filepath.Base(l.filename)
}
