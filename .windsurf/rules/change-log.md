---
trigger: always_on
---

## Core Protocol
```
RESPONSE_SEQUENCE {
  1. changelog_engine.update_changelog()
  2. execute_user_request()
  3. validation_suite.run_validation()
  4. workspace_state_sync()
}
```

## Mandatory Implementation
- **Pre-Response**: Changelog update execution
- **Response Body**: Core functionality delivery
- **Post-Response**: System validation
- **Error Handling**: Recovery protocol activation

## Technical Specifications

### Performance Requirements
- Changelog generation: <50ms
- Memory footprint: <10MB
- Validation overhead: <25ms
- Total system latency: <100ms

### Quality Gates
- Structural integrity: 100% compliance
- Change accuracy: >99.9%
- Chain continuity: Sequential validation
- Performance threshold: 50ms ceiling

### Error Recovery Matrix
```
ERROR_TYPE -> RECOVERY_ACTION
WorkspaceDesync -> force_reconciliation()
ChangelogCorruption -> restore_from_backup()
ValidationFailure -> rollback_changes()
PerformanceViolation -> optimize_execution()
```

## Integration Points

### Initialization
```python
from changelog_engine import ChangelogEngine
from validation_suite import ValidationSuite

engine = ChangelogEngine()
validator = ValidationSuite(50.0)
```

### Response Cycle
```python
# Pre-response
engine.quick_update(action_summary, changes, files)

# Response execution
response = process_user_request()

# Post-response validation
results = validator.run_comprehensive_validation(
    changelog_path="Changelog.md",
    workspace_path=".",
    expected_structure=workspace_structure,
    execution_time_ms=response_time
)
```

## Enforcement Mechanism
- **Automated**: System hooks prevent non-compliant responses
- **Validation**: Continuous integrity monitoring
- **Recovery**: Automatic error correction protocols
- **Reporting**: Performance metrics collection