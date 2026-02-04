# Plugin System - v3.1

**Directory**: `src/plugins/`  
**Purpose**: Plugin implementations for AI tool monitoring

---

## STRUCTURE

```
src/plugins/
├── AGENTS.md         # This file
├── __init__.py       # Module exports
├── base.py           # Plugin base classes + interfaces
└── process.py        # Process monitoring plugin
```

---

## WHERE TO LOOK

| Task | File | Notes |
|------|------|-------|
| Create new plugin | `base.py` | Extend BasePlugin ABC |
| Process monitoring | `process.py` | Reference implementation |
| StateEvent format | `base.py` | StateEvent dataclass |

---

## CONVENTIONS (THIS DIR)

### New Plugin Template
```python
# -*- coding: utf-8 -*-
"""
[Plugin name] - [Brief description]
"""

from .base import BasePlugin, PluginMetadata, PluginType, StateEvent, Status

class MyPlugin(BasePlugin):
    """My custom plugin"""
    
    THRESHOLDS = {...}  # Define thresholds
    
    def __init__(self, name: str):
        super().__init__(name)
        self._metadata = PluginMetadata(
            name=name,
            version="1.0.0",
            author="AI-ClaudeCat",
            description="...",
            plugin_type=PluginType.CUSTOM,
            supported_software=[...],
        )
    
    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata
    
    def check_available(self) -> bool:
        ...
    
    async def detect(self) -> StateEvent | None:
        ...
    
    def start(self) -> None:
        self._running = True
    
    def stop(self) -> None:
        self._running = False
```

### Required Methods
| Method | Required | Returns |
|--------|----------|---------|
| `metadata` | ✅ | PluginMetadata |
| `check_available()` | ✅ | bool |
| `detect()` | ✅ | StateEvent \| None |
| `start()` | ✅ | None |
| `stop()` | ✅ | None |

---

## PLUGINS

### ProcessPlugin (done)
- **File**: `process.py`
- **Type**: PluginType.PROCESS
- **Detection**: CPU usage via psutil
- **States**: idle → running → thinking → working
- **Status**: ✅ Implemented, tested
