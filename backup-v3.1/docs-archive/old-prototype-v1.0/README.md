# Old Prototype v1.0 - Deprecated

**Version**: 1.0.0  
**Architecture**: v1.0 - Basic Monitoring  
**Status**: DEPRECATED - Migrated to v3.1 Plugin-based Architecture  
**Migration Date**: 2026-02-04

---

## Overview

This was the initial prototype demonstrating core monitoring concepts:
- Process monitoring via psutil
- Window title analysis via pygetwindow
- File system monitoring via watchdog
- Basic status fusion with weighted voting

## File Structure

```
old-prototype-v1.0/
├── VERSION.json           # Version metadata
├── README.md             # This file
├── EXPERIENCE_SUMMARY.md # Lessons learned
└── src/monitor/          # Original prototype code
    ├── base.py           # BaseMonitor class, Status enum
    ├── process_monitor.py # Process CPU monitoring
    ├── window_monitor.py  # Window title analysis
    ├── file_monitor.py    # File system events
    ├── status_fusion.py   # Weighted voting fusion
    └── __init__.py       # Module exports
```

---

## Key Components

### 1. BaseMonitor (base.py)
```python
class BaseMonitor(ABC):
    - callback: Optional status change callback
    - start()/stop(): Control monitoring
    - get_result(): Get MonitorResult
    - is_available()/is_running(): State queries
```

### 2. ProcessMonitor
- Uses `psutil` to monitor CPU usage
- Thresholds: idle<0.5%, running<3%, thinking<15%, working>15%
- Supports keyword matching on process name/cmdline

### 3. WindowMonitor
- Uses `pygetwindow` to get window titles
- Regex-based keyword matching for status inference
- Priority: ERROR > DONE > EXECUTING > WRITING > READING > THINKING

### 4. FileMonitor
- Uses `watchdog` to monitor file system changes
- Tracks Claude-related paths: ~/.claude/, ~/.claude-code-router/, ~/.config/claude/
- Activity-based status: none/low/medium/high

### 5. StatusFusion
- Weighted voting across all monitors
- Smoothing with history (last 10 results)
- Confidence calculation based on vote consistency

---

## Known Issues

1. **Synchronous Design**: All monitoring is blocking, no async support
2. **Tight Coupling**: Monitors directly call fusion, no event bus
3. **Platform Dependency**: Window monitoring only works on desktop OS with pygetwindow
4. **No Plugin System**: Hardcoded monitors, cannot be extended
5. **No Output Adapters**: No WebSocket/HTTP/Redis support
6. **Limited Error Handling**: Some edge cases not handled gracefully

---

## Migration Notes

This prototype was replaced by v3.1 Plugin-based Architecture. Key improvements in v3.1:

- ✅ Proper plugin interface with metadata
- ✅ Async/await support throughout
- ✅ Event bus for loose coupling
- ✅ Multiple output adapters (WebSocket/HTTP/Redis)
- ✅ Plugin registry for discovery
- ✅ Standardized StateEvent with serialization
- ✅ Better error handling and logging

---

## Testing

Original test commands:
```bash
# Test fusion
python scripts/test_fusion.py

# Monitor OpenCode
python scripts/monitor_opencode.py
```

---

## Author

AI-ClaudeCat Team  
**License**: MIT
