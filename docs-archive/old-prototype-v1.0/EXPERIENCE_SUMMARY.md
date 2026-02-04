# Experience Summary - Old Prototype v1.0

**Document Version**: 1.0.0  
**Date**: 2026-02-04  
**Author**: AI-ClaudeCat Team

---

## What Went Well ✅

### 1. Modular Monitor Design
The separation into ProcessMonitor, WindowMonitor, FileMonitor, and StatusFusion was the right idea.

**Lesson**: Keep monitors independent, each focused on one data source.

**Apply to v3.1**: ✅ Plugins are independent and focus on single detection methods.

### 2. Callback System
The `_notify()` mechanism for status changes worked correctly.

**Lesson**: Callback pattern is good for decoupling detection from consumption.

**Apply to v3.1**: ✅ Event callbacks in BasePlugin, plus EventBus for broader distribution.

### 3. Confidence Scoring
The confidence system (0.0-1.0) helped with weighted voting.

**Lesson**: Confidence scores are essential for multi-source fusion.

**Apply to v3.1**: ✅ Kept in StateEvent with same 0.0-1.0 range.

### 4. Smooth Transition in StatusFusion
The history-based smoothing prevented flickering.

**Lesson**: Short-term history helps reduce noise in status detection.

**Apply to v3.1**: Consider adding similar smoothing to middleware fusion.

### 5. Keyword Patterns for Window Title
Regex-based title analysis was intuitive and effective.

**Lesson**: Window titles contain rich status hints.

**Apply to v3.1**: ✅ WindowPlugin should use similar pattern matching.

---

## What Didn't Work ❌

### 1. Synchronous Architecture
All monitors block on detection - this caused delays and made real-time updates difficult.

**Problem**:
```python
# Old - blocking call
cpu_percent = p.cpu_percent(interval=0.3)  # Blocks for 0.3s
```

**Impact**: UI updates were delayed, high CPU usage during polling.

**Fix in v3.1**: ✅ Full async/await support with asyncio.

### 2. Tight Coupling Between Monitors and Fusion
Monitors directly called fusion methods - no event bus.

**Problem**:
```python
# Old - direct coupling
self._notify(result)  # Calls fusion directly
```

**Impact**: Cannot easily add new output destinations (WebSocket, HTTP, etc.).

**Fix in v3.1**: ✅ EventBus pattern for loose coupling:
```
Plugin -> EventBus -> [WebSocket, HTTP, Redis, etc.]
```

### 3. No Plugin System
Hardcoded monitors - cannot extend at runtime.

**Problem**:
```python
# Old - must modify code to add new monitor
class CustomMonitor(BaseMonitor):  # But where to register?
```

**Impact**: Users cannot add custom detection methods.

**Fix in v3.1**: ✅ PluginRegistry with discovery and metadata.

### 4. Missing Output Adapters
No way to send status to other systems.

**Problem**: Only callback available, no standard output formats.

**Impact**: Cannot integrate with external systems or web frontends.

**Fix in v3.1**: ✅ WebSocket, HTTP REST, Redis Pub/Sub adapters.

### 5. Platform-Specific Code
pygetwindow only works on desktop OS with GUI.

**Problem**:
```python
# WindowMonitor fails on headless servers
import pygetwindow  # ImportError or empty results
```

**Impact**: Not portable, fails silently on servers.

**Fix in v3.1**: ✅ Optional plugins with graceful degradation.

### 6. No Serialization
MonitorResult cannot be easily serialized for network transfer.

**Problem**:
```python
# Can't send over network
result = {"status": "running", "confidence": 0.85}  # Custom dict, no schema
```

**Impact**: Cannot build distributed systems or web frontends.

**Fix in v3.1**: ✅ StateEvent.to_dict()/from_dict() with ISO timestamps.

### 7. Limited Error Handling
Some edge cases crashed the monitors.

**Examples**:
- psutil.AccessDenied when reading process info
- pygetwindow returning empty on some OS
- watchdog handler exceptions

**Impact**: Unstable, requires manual restart.

**Fix in v3.1**: ✅ Proper exception handling in each plugin.

---

## Technical Decisions to Keep

### 1. CPU-Based Status Thresholds
```python
THRESHOLDS = {
    "idle": 0.5,
    "running": 3.0,
    "thinking": 15.0,
    "working": 50.0,
}
```
These thresholds worked well for distinguishing AI tool states.

### 2. Weighted Voting for Fusion
The weighted voting system was simple and effective:
```python
votes[status] += result.confidence * weight
```

### 3. Activity-Based File Monitoring
Tracking file activity events (create/modify/delete) correlated well with AI tool activity.

### 4. Priority-Based Title Analysis
Checking ERROR/DONE first prevented missing critical states.

---

## Technical Decisions to Change

### 1. Instead of Direct Callbacks → EventBus
**Old**:
```python
monitor.set_callback(fusion.on_monitor_result)
```

**v3.1**:
```python
event_bus.subscribe(PluginType.PROCESS, handler)
event_bus.publish(StateEvent(...))
```

### 2. Instead of Hardcoded Monitors → Plugin System
**Old**: Write code, restart app

**v3.1**: Plugin discovery + hot-reload (future)

### 3. Instead of Blocking I/O → Async I/O
**Old**:
```python
cpu = p.cpu_percent(interval=0.3)  # Blocks!
```

**v3.1**:
```python
cpu = await asyncio.to_thread(p.cpu_percent, interval=0.1)
```

### 4. Instead of Internal State → Serializable Events
**Old**:
```python
result = MonitorResult(...)  # Internal class
```

**v3.1**:
```python
event = StateEvent(...)  # Can be JSON serialized
event.to_dict()  # {"status": "running", ...}
```

---

## Metrics to Reuse

| Metric | Old Value | Notes |
|--------|-----------|-------|
| CPU thresholds | 0.5/3/15/50 % | Works well |
| Title confidence | 0.6-0.95 | Prioritize ERROR/DONE |
| File activity window | 1 second | Good for batching |
| History smoothing | 10 entries | Prevents flicker |
| Vote threshold | 80% of max | Good for consensus |

---

## Code Patterns to Keep

### 1. Defensive Exception Handling
```python
try:
    result = monitor.get_result()
except (psutil.NoSuchProcess, psutil.AccessDenied):
    result = MonitorResult(Status.UNKNOWN, ...)
```

### 2. Status Change Detection
```python
if current.status != last.status:
    notify_change(current)
```

### 3. Confidence Calibration
- NOT_RUNNING: 1.0 (certain)
- ERROR/DONE: 0.95 (clear indicators)
- THINKING/WORKING: 0.8-0.85 (likely)
- RUNNING/IDLE: 0.6-0.9 (ambiguous)

---

## Code Patterns to Avoid

### 1. Blocking Sleep in Loops
```python
# BAD
while True:
    check_status()
    time.sleep(2)  # Blocks!
```

**Better**:
```python
# GOOD
while True:
    check_status()
    await asyncio.sleep(2)
```

### 2. Global State
```python
# BAD
monitors = []  # Global list

class Monitor:
    def __init__(self):
        monitors.append(self)  # Side effect
```

**Better**:
```python
# GOOD
registry = PluginRegistry()

class Plugin:
    def __init__(self, name: str):
        registry.register(self)  # Explicit registration
```

### 3. Magic Numbers
```python
# BAD
if cpu > 15:  # What does 15 mean?
```

**Better**:
```python
# GOOD
THRESHOLDS = {"thinking": 15.0}
if cpu > THRESHOLDS["thinking"]:
```

---

## Testing Lessons

### What to Test
1. Status transitions (A→B→C)
2. Confidence scoring at boundaries
3. Error conditions (missing processes, permissions)
4. Multiple monitors running simultaneously
5. Event ordering and timing

### How to Test
- Mock psutil/window for unit tests
- Use fake file system for file monitor tests
- Test with real processes when possible

---

## Documentation Improvements

### Old Documentation
- Inline code comments only
- No API documentation
- No migration guides

### New Documentation (v3.1)
- Markdown docs in `docs/`
- API documentation in docstrings
- Migration guides for version changes
- Example plugins in `examples/`

---

## Conclusion

The v1.0 prototype validated core concepts:
- ✅ Process monitoring works
- ✅ Window title analysis works
- ✅ File activity tracking works
- ✅ Weighted fusion produces reasonable results

The v3.1 rewrite addresses architectural limitations while preserving these validated concepts.

---

**Next Steps**: See v3.1 Plugin-based Architecture in `docs/插件化架构详细设计.md`
