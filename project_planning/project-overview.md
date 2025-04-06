# Project Overview & Plan: LMM Invoice Data Extraction Comparison

## Project Summary
This project evaluates multiple open-source Large Multimodal Models (LMMs) on their ability to extract two specific fields of structured data from handwritten invoice images. The project will identify the optimal model and prompt combination through systematic comparison.

## Business Context
A local general contractor needs to automate the extraction of data from invoices that contain typed forms filled in by hand. This project will compare different models to identify the most effective solution for this task.

## Problem Statement
Evaluate and compare multiple open-source Large Multimodal Models (LMMs) on their ability to extract two specific fields ("Work Order Number" and "Total Cost") from handwritten invoice images, and determine the optimal prompt strategy for each model.

## Project Goals
1. Compare the performance of various open-source LMMs on invoice data extraction
2. Evaluate different prompting strategies for each model
3. Identify the best-performing model/prompt combination
4. Document findings with clear performance metrics and comparisons

## Project Scope
- Focus on extracting two specific data fields from invoice images:
  - Work Order Number
  - Total Cost
- Begin with 20 images for initial testing, expanding to ~150 for full evaluation
- Evaluate at least 3-5 open-source LMMs
- Test at least 3-5 different prompting strategies per model
- Implement a robust evaluation framework with clear metrics:
  - Exact match accuracy
  - Character Error Rate (CER)
- Document findings and model performance characteristics

## Out of Scope
- Fine-tuning and optimization of models
- Deployment outside the RunPod testing environment
- Integration with existing contractor systems
- Handling invoices with different formats/templates
- Extracting more than the two specified data fields
- Shared environment between notebooks

## Data Information
- The dataset consists of invoice images with typed forms filled in by hand
- Images are in JPG format, identified by a unique number in the filename (e.g., 12147.jpg)
- Ground truth data is provided in a CSV file that matches images by their unique ID
- Initial testing will use 20 images, with expansion to ~150 images for full evaluation
- Key fields and their specifications:
  - Work Order Number: 5-digit alphanumeric string, preserves leading zeros
  - Total Cost: Float with 2 decimal places, stored after cleaning (removing "$" and ",")
- Data type handling:
  - Ground truth data types are normalized during loading
  - Field-specific comparison strategies handle format variations
  - Robust validation ensures data integrity

## Testing Environment
- RunPod environment with approximately 94GB RAM and 150GB storage
- Jupyter notebooks with separate kernels for each experiment
- No shared environment variables between notebooks

## Core System Capabilities

1. **Model Management**: System to download, configure, and instantiate different LMMs based on configuration files
2. **Prompt Management**: Framework to store, select, and format different prompt templates for each model
3. **Image Handling**: Utilities to load and preprocess invoice images for model input
4. **Inference Pipeline**: Process to combine images with prompts, send to models, and capture responses
5. **Evaluation Framework**: System to calculate and compare performance metrics across model/prompt combinations

## Models to Evaluate
1. **Pixtral-12B** (https://huggingface.co/mistral-community/pixtral-12b)
   - Multimodal model based on Mistral architecture
   - Strong vision-language capabilities
   - Compatible with the Mistral ecosystem

2. **Llama-3.2-11B-Vision** (https://huggingface.co/meta-llama/Llama-3.2-11B-Vision)
   - Meta's vision-enabled large language model
   - Advanced vision-language understanding
   - Strong document analysis capabilities

3. **Doctr** (https://github.com/mindee/doctr)
   - Specialized document understanding model
   - Purpose-built for OCR and document processing
   - Potentially more optimized for structured document extraction

## Prompt Strategies to Test
1. **Direct Extraction**: Simple instructions to extract specific fields
2. **Detailed Instructions**: Detailed guidance on field locations and formats
3. **Few-shot Examples**: Examples of similar invoices and expected outputs
4. **Step-by-step Approach**: Guided reasoning process for finding and extracting fields
5. **Locational Prompting**: Spatial guidance indicating where fields are typically located on the page (e.g., "Work Order Number is usually found in the upper right corner")

## Evaluation Approach
- Use exact match accuracy as primary metric
- Use Character Error Rate (CER) as secondary metric
- Consider error analysis for non-exact matches as a future enhancement
- Compare performance across models and prompt types
- Visualize results for easy comparison

## Implementation Approach
- Implement with a clean, modular architecture
- Create self-contained experiment notebooks
- Use standardized formats for configuration and results
- Focus on simplicity and clarity in code
- Ensure strong separation of concerns
- Use dependency injection for component interactions

## Expected Deliverables
1. A modular, reproducible code repository
2. Comprehensive model comparison results and analysis
3. Detailed documentation of methodologies and findings
4. Recommended model/prompt combination with justification

## Success Criteria
- Clear identification of best-performing model/prompt combination
- Quantifiable metrics for extraction accuracy (exact match and CER)
- Reproducible evaluation framework
- Documentation of performance characteristics across models and prompts

## Future Enhancements

### Near-Term Enhancements

#### 1. Proprietary Model API Integration
- Integrate with Claude 3.7 Sonnet and other proprietary models via API
- Create adapter interface for API-based model evaluation
- Implement consistent evaluation framework across local and API models
- Compare performance of open-source vs. proprietary models
- Analyze cost-effectiveness of API-based solutions

### Longer-Term Enhancements

### 1. Advanced Error Analysis
- Implement detailed error categorization for non-exact matches
- Analyze patterns in extraction errors across models
- Develop visualization tools for error types and frequencies
- Create confusion matrices for field detection accuracy

### 2. Model Fine-Tuning
- Fine-tune the best-performing model on the full dataset
- Implement training pipeline with appropriate validation
- Test various fine-tuning approaches (adapter-based, full model, etc.)
- Measure performance improvements from fine-tuning

### 3. Model Optimization
- Implement quantization and pruning for deployment
- Test different optimization techniques (int8, int4, ONNX conversion)
- Benchmark performance/accuracy tradeoffs
- Create deployment packages for optimized models

### 4. Extended Field Extraction
- Expand to extract additional fields from invoices
- Test model performance on more complex field types
- Develop specialized prompt strategies for different field types
- Create field-specific evaluation metrics

### 5. Processing Pipeline Integration
- Develop end-to-end processing pipeline
- Integrate with document scanning/preprocessing
- Create API for automated extraction
- Implement batch processing capabilities

### 6. UI Development
- Create web interface for invoice processing
- Implement visual verification of extracted fields
- Develop correction interface for extraction errors
- Build dashboard for monitoring extraction performance
