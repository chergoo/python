package main

import (
	"fmt"
	"strings"
	"sync"
	"time"

	"go.bug.st/serial"
)

// SerialWorker 后台串口读取（回调模式）
type SerialWorker struct {
	portName string
	baudrate int
	port     serial.Port
	stopCh   chan struct{}
	onData   func(line string)
	onStatus func(status string)
	onError  func(err error)

	mu           sync.Mutex
	lineBuf      []byte        // 累积的原始字节
	lastReceived time.Time     // 最后收到数据的时间
	flushTimeout time.Duration // 空闲超时阈值
	stopped      bool
}

func NewSerialWorker(portName string, baudrate int) *SerialWorker {
	return &SerialWorker{
		portName:     portName,
		baudrate:     baudrate,
		stopCh:       make(chan struct{}),
		flushTimeout: 200 * time.Millisecond,
		lastReceived: time.Now(),
		lineBuf:      make([]byte, 0, 1024),
	}
}

// SetFlushTimeout 设置空闲超时时间
func (w *SerialWorker) SetFlushTimeout(d time.Duration) {
	w.flushTimeout = d
}

func (w *SerialWorker) OnData(fn func(line string)) {
	w.onData = fn
}

func (w *SerialWorker) OnStatus(fn func(status string)) {
	w.onStatus = fn
}

func (w *SerialWorker) OnError(fn func(err error)) {
	w.onError = fn
}

func (w *SerialWorker) Start() error {
	fmt.Printf("[SerialWorker] 正在打开 %s (baud=%d)...\n", w.portName, w.baudrate)
	mode := &serial.Mode{
		BaudRate: w.baudrate,
		DataBits: 8,
		Parity:   serial.NoParity,
		StopBits: serial.OneStopBit,
	}
	port, err := serial.Open(w.portName, mode)
	if err != nil {
		fmt.Printf("[SerialWorker] 打开失败: %v\n", err)
		return fmt.Errorf("无法打开串口 %s: %w", w.portName, err)
	}
	if err := port.SetReadTimeout(500 * time.Millisecond); err != nil {
		port.Close()
		fmt.Printf("[SerialWorker] 设置超时失败: %v\n", err)
		return fmt.Errorf("设置超时失败: %w", err)
	}
	fmt.Printf("[SerialWorker] %s 已打开，启动读取和刷新 goroutine\n", w.portName)
	w.port = port
	if w.onStatus != nil {
		w.onStatus("connected")
	}
	go w.readLoop()
	go w.flushLoop()
	return nil
}

// readLoop 负责读取串口数据并处理换行分割
func (w *SerialWorker) readLoop() {
	defer func() {
		w.mu.Lock()
		w.stopped = true
		w.mu.Unlock()
		if w.port != nil {
			w.port.Close()
		}
		if w.onStatus != nil {
			w.onStatus("disconnected")
		}
	}()

	buf := make([]byte, 1024)
	for {
		select {
		case <-w.stopCh:
			return
		default:
		}

		n, err := w.port.Read(buf)
		if err != nil {
			// 超时错误忽略（由 flushLoop 处理空闲刷新）
			if ne, ok := err.(interface{ Timeout() bool }); ok && ne.Timeout() {
				continue
			}
			if w.onError != nil {
				w.onError(err)
			}
			time.Sleep(10 * time.Millisecond)
			continue
		}

		if n == 0 {
			continue
		}

		// 加锁处理接收到的字节
		w.mu.Lock()
		for i := 0; i < n; i++ {
			b := buf[i]
			if b == '\r' || b == '\n' {
				// 遇到换行，推送当前行（如果有内容）
				if len(w.lineBuf) > 0 {
					line := strings.ToValidUTF8(string(w.lineBuf), "\uFFFD")
					w.lineBuf = w.lineBuf[:0]
					line = strings.TrimSpace(line)
					if line != "" && w.onData != nil {
						w.onData(line)
					}
				}
			} else {
				w.lineBuf = append(w.lineBuf, b)
			}
		}
		w.lastReceived = time.Now()
		w.mu.Unlock()
	}
}

// flushLoop 定时检查空闲超时，强制推送累积数据
func (w *SerialWorker) flushLoop() {
	ticker := time.NewTicker(50 * time.Millisecond) // 每 50ms 检查一次
	defer ticker.Stop()

	for {
		select {
		case <-w.stopCh:
			return
		case <-ticker.C:
			w.mu.Lock()
			if len(w.lineBuf) > 0 && time.Since(w.lastReceived) > w.flushTimeout {
				line := strings.ToValidUTF8(string(w.lineBuf), "\uFFFD")
				w.lineBuf = w.lineBuf[:0]
				line = strings.TrimSpace(line)
				if line != "" && w.onData != nil {
					w.onData(line)
				}
			}
			w.mu.Unlock()
		}
	}
}

func (w *SerialWorker) Stop() {
	w.mu.Lock()
	defer w.mu.Unlock()
	if !w.stopped {
		close(w.stopCh)
	}
}

func (w *SerialWorker) IsRunning() bool {
	w.mu.Lock()
	defer w.mu.Unlock()
	return !w.stopped
}

// ListPorts 返回可用串口列表
func ListPorts() []string {
	ports, err := serial.GetPortsList()
	if err != nil {
		return nil
	}
	return ports
}
