# Dependency Injection Improvement Tasks

## Background
Our codebase effectively uses dependency injection as a core architectural pattern, as outlined in the project rules and implemented in Phase 1 components. As we move into Phase 2 and 3, we need to strengthen and standardize our approach to ensure maintainability and scalability.

## Current Implementation Status
- Phase 1 components (ConfigLoader, DataLoader, GroundTruthManager, ImageProcessor) have established a good foundation for DI
- Factory patterns have been implemented consistently
- Interface-based design is being followed
- Tests demonstrate the benefits of DI for mocking and isolation
- BaseModel abstract class implemented with proper DI patterns and comprehensive testing

## Improvement Tasks

### 1. Dependency Graph Documentation
- [ ] Create a visual diagram of current component dependencies for Phase 1
- [ ] Document the planned dependency graph for Phase 2 components
- [ ] Identify potential circular dependencies or complex dependency chains
- [ ] Add the dependency graph to the architecture documentation

### 2. Standardize Factory Classes for Phase 2-3
- [x] Ensure BaseModel follows established interface and DI patterns
- [ ] Complete ModelFactory implementation following existing factory patterns
- [x] Implement OutputParserFactory with proper registration and DI patterns
- [ ] Implement PromptFactory with consistent registration mechanisms
- [ ] Add detailed documentation to factory classes about their role in DI
- [ ] Update factory class tests to verify proper dependency handling

### 3. Dependency Container Evaluation
- [ ] Research lightweight DI containers compatible with our architecture
- [ ] Create a small proof of concept using the most promising option
- [ ] Test with Phase 1 components before introducing to Phase 2
- [ ] Document findings and make recommendations in an updated ADR

### 4. Component Granularity Review
- [ ] Identify any components with > 4 dependencies
- [ ] Review against the 5-argument constraint in project rules
- [ ] Propose refactoring strategies for complex components
- [ ] Update class structure to maintain clear separation of concerns

### 5. Enhance Constructor Documentation
- [ ] Add detailed docstrings for all constructor parameters
- [ ] Document the purpose and expected behavior of each dependency
- [ ] Highlight optional vs. required dependencies
- [ ] Expand existing test fixtures to validate dependency behavior

## Completion Criteria
- All Phase 2 and 3 components follow consistent DI patterns
- Factory classes handle dependency creation uniformly
- Component dependencies are clearly documented in code
- High-dependency components are refactored into more focused units
- A decision is made regarding potential DI container adoption

## Implementation Notes
- OutputParser system implemented with proper DI patterns:
  - BaseOutputParser interface with clear methods and dependencies
  - OutputParserFactory with registration mechanism and proper error handling
  - ExtractedFieldsOutputParser with injectable validator dependencies
  - High test coverage (85-100%) with test fixtures demonstrating DI benefits

## References
- [ADR-003: Dependency Injection Patterns](../docs/adr/003-dependency-injection-patterns.md)
- [Project Rules: Dependency Injection Section](project-rules.md)
- [Architecture Diagram](architecture-diagram.md) 