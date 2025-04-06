# ADR 001: Ground Truth Data Types and Comparison Strategy

## Status
Accepted

## Context
The system needs to compare LLM outputs against ground truth data for invoice field extraction. Two critical fields require comparison:

1. **Total Amount**
   - Ground truth currently stores as object due to comma separators
   - Values represent dollar amounts with 2 decimal places
   - LLM may return various formats ("$140", "140.00", "1,234.56")

2. **Work Order Number**
   - Currently stored as object
   - Could be 5-digit number with leading zeros
   - Potentially contains alpha-numeric values
   - Format preservation is critical

## Decision
1. **Total Amount Field**
   - Store in ground truth as float with 2 decimal places
   - Clean data during ground truth loading:
     - Strip "$" and "," characters
     - Parse to float
     - Validate: positive number with ≤ 2 decimal places
   - Implement comparison helper that normalizes LLM output to float
   - Use small epsilon (0.01) for float comparisons

2. **Work Order Number Field**
   - Keep as object type in ground truth
   - Preserve exact format including leading zeros
   - Implement case-insensitive comparison for alpha characters
   - Require exact match after normalization

## Consequences
### Positive
- Clear separation between storage and comparison logic
- Proper data type validation at load time
- Flexible comparison strategies for different field types
- Better error detection in LLM outputs

### Negative
- More complex comparison logic needed
- Need to handle various LLM output formats
- Additional validation required during data loading

## Implementation Notes
1. Data cleaning happens in GroundTruthManager during load
2. Comparison logic lives in separate evaluation component
3. Need to log/track unparseable LLM outputs
4. Consider adding data quality metrics 