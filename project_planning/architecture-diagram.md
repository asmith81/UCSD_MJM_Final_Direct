# System Architecture Diagram: LMM Invoice Data Extraction Comparison

## Component Relationships Diagram

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                      Experiment Notebook                                   │
│                                                                                           │
│  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────┐   │
│  │  Configuration   │   │  Data Loading    │   │  Model+Prompt    │   │  Evaluation  │   │
│  │  Selection       │   │  & Preprocessing │   │  Execution       │   │  & Results   │   │
│  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘   └──────┬───────┘   │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┼────────────┘
            │                     │                     │                     │
            ▼                     ▼                     ▼                     ▼
┌───────────────────┐   ┌─────────────────┐   ┌────────────────────┐   ┌────────────────┐
│                   │   │                 │   │                    │   │                │
│  ConfigLoader     │   │  DataLoader     │   │  Model Factory     │   │  Evaluation    │
│                   │   │                 │   │                    │   │  Service       │
└─────────┬─────────┘   └────────┬────────┘   └──────────┬─────────┘   └────────┬───────┘
          │                      │                       │                      │
          ▼                      ▼                       │                      │
┌─────────────────┐   ┌──────────────────┐              │                      │
│                 │   │                  │              │                      │
│ Configuration   │   │ GroundTruth      │              │                      │
│ Objects         │   │ Manager          │              │                      │
│                 │   │                  │              │                      │
└─────────────────┘   └────────┬─────────┘              │                      │
                               │                        │                      │
                               ▼                        │                      │
                      ┌────────────────┐                │                      │
                      │                │                │                      │
                      │ Image          │                │                      │
                      │ Processor      │                │                      │
                      │                │                │                      │
                      └────────────────┘                │                      │
                                                        │                      │
                                                        ▼                      │
┌───────────────────────────────────────────┐  ┌────────────────────┐         │
│                                           │  │                    │         │
│  Prompt Factory                           │  │  Model             │         │
│                                           │  │  Implementation    │         │
│  ┌───────────────┐  ┌───────────────┐     │  │  ┌──────────────┐ │         │
│  │ Basic         │  │ Detailed      │     │  │  │ Pixtral      │ │         │
│  │ Prompt        │  │ Prompt        │     │  │  │ Model        │ │         │
│  └───────────────┘  └───────────────┘     │  │  └──────────────┘ │         │
│                                           │  │                    │         │
│  ┌───────────────┐  ┌───────────────┐     │  │  ┌──────────────┐ │         │
│  │ Few-Shot      │  │ Step-by-Step  │     │  │  │ LlamaVision  │ │         │
│  │ Prompt        │  │ Prompt        │     │◄─┼──┤ Model        │ │         │
│  └───────────────┘  └───────────────┘     │  │  └──────────────┘ │         │
│                                           │  │                    │         │
│  ┌───────────────┐                        │  │  ┌──────────────┐ │         │
│  │ Locational    │                        │  │  │ Doctr        │ │         │
│  │ Prompt        │                        │  │  │ Model        │ │         │
│  └───────────────┘                        │  │  └──────────────┘ │         │
│                                           │  │                    │         │
└───────────────────────────────────────────┘  └────────┬───────────┘         │
                                                        │                      │
                                                        ▼                      │
                                               ┌────────────────────┐         │
                                               │                    │         │
                                               │  Output            │         │
                                               │  Parser            │         │
                                               │                    │         │
                                               └────────┬───────────┘         │
                                                        │                     │
                                                        └─────────────────────┘
                                                                  │
                                                                  ▼
                                                       ┌────────────────────┐
                                                       │                    │
                                                       │  Metrics           │
                                                       │  Calculator        │
                                                       │                    │
                                                       └────────┬───────────┘
                                                                │
                                                                ▼
                                                       ┌────────────────────┐
                                                       │                    │
                                                       │  Results           │
                                                       │  Manager           │
                                                       │                    │
                                                       └────────┬───────────┘
                                                                │
                                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Analysis Notebook                                         │
│                                                                                            │
│   ┌──────────────────┐   ┌────────────────────┐   ┌────────────────────┐                   │
│   │  Results         │   │  Comparative       │   │  Visualization     │                   │
│   │  Loading         │   │  Analysis          │   │  Generation        │                   │
│   └──────────────────┘   └────────────────────┘   └────────────────────┘                   │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Core Components

1. **ConfigLoader**
   - Loads YAML configuration files
   - Validates configuration structure
   - Creates configuration objects

2. **DataLoader**
   - Loads invoice images from directory
   - Reads ground truth CSV file
   - Maps images to their ground truth data

3. **GroundTruthManager**
   - Parses and validates ground truth data
   - Handles normalization of field values
   - Provides access to ground truth by image ID

4. **ImageProcessor**
   - Performs basic preprocessing on images
   - Normalizes image sizes and formats
   - Prepares images for model input

5. **ModelFactory**
   - Creates model instances based on configuration
   - Handles model loading and initialization
   - Provides consistent interface for all models

6. **Model Implementations**
   - **PixtralModel**: Implementation for Pixtral-12B
   - **LlamaVisionModel**: Implementation for Llama-3.2-11B-Vision
   - **DoctrModel**: Implementation for Doctr
   - Each implements standard interface defined by BaseModel

7. **PromptFactory**
   - Creates prompt generators based on configuration
   - Manages prompt template selection
   - Provides consistent interface for all prompt strategies

8. **Prompt Implementations**
   - **BasicPromptGenerator**: Direct extraction prompts
   - **DetailedPromptGenerator**: Detailed instruction prompts
   - **FewShotPromptGenerator**: Few-shot example prompts
   - **StepByStepPromptGenerator**: Guided extraction prompts
   - **LocationalPromptGenerator**: Spatial location prompts
   - Each implements standard interface defined by BasePromptGenerator

9. **OutputParser**
   - Extracts structured data from model outputs
   - Normalizes extracted field values
   - Handles model-specific output formats

10. **EvaluationService**
    - Orchestrates the evaluation process
    - Compares extracted fields to ground truth
    - Calculates performance metrics

11. **MetricsCalculator**
    - Calculates exact match accuracy
    - Calculates Character Error Rate (CER)
    - Provides standardized metric values

12. **ResultsManager**
    - Saves experiment results to disk
    - Loads results for analysis
    - Maintains standardized result format

### Notebook Components

1. **Experiment Notebook**
   - Thin UI for configuring and running experiments
   - Self-contained with all necessary imports
   - Saves results to standardized format

2. **Analysis Notebook**
   - Aggregates results from multiple experiments
   - Creates comparative visualizations
   - Identifies best-performing model/prompt combinations

## Data Flow

1. **Configuration Flow**
   - Configuration files → ConfigLoader → Configuration Objects → Components

2. **Data Preparation Flow**
   - Images → DataLoader → ImageProcessor → Processed Images
   - CSV → DataLoader → GroundTruthManager → Structured Ground Truth

3. **Model Execution Flow**
   - Model Configuration → ModelFactory → Model Implementation
   - Prompt Configuration → PromptFactory → Prompt Generator
   - Processed Image + Prompt → Model → Raw Output → OutputParser → Extracted Fields

4. **Evaluation Flow**
   - Extracted Fields + Ground Truth → EvaluationService → MetricsCalculator → Metrics
   - Metrics → ResultsManager → Saved Results

5. **Analysis Flow**
   - Saved Results → Analysis Notebook → Visualizations and Comparisons

## Implementation Notes

1. **Dependency Injection**
   - All components receive dependencies via constructors
   - No global state or singletons
   - Clear tracing of dependencies through the system

2. **Separation of Concerns**
   - Each component has a single responsibility
   - Components communicate through well-defined interfaces
   - Implementation details hidden behind abstractions

3. **Configuration-Driven Design**
   - All behavior configurable through YAML files
   - No hardcoded model or prompt configurations
   - Clear separation between configuration and code

4. **Notebook as Thin UI**
   - Notebooks contain minimal logic
   - Focus on configuration, execution, and visualization
   - All business logic in the component layer
