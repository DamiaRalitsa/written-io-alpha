# 🚀 LLM Training Guide for Task Backlog Generation

This guide will help you train and optimize LLMs to generate high-quality task backlog items for project management tools like Jira, Azure DevOps, and Taiga.

## 📋 Training Approaches

### 1. **Prompt Engineering (Immediate - No Training Required)**
- **Best for**: Quick setup, immediate results
- **Cost**: Low (pay-per-use API calls)
- **Effort**: Low to Medium
- **Quality**: Good to Very Good

#### Implementation Steps:
1. Use the enhanced prompts in `prompts/jira_backlog_prompts.py`
2. Test with different models (GPT-3.5, GPT-4, Claude-3)
3. Fine-tune prompts based on your specific needs

### 2. **Few-Shot Learning (Quick Setup)**
- **Best for**: Domain-specific improvements
- **Cost**: Low to Medium
- **Effort**: Medium
- **Quality**: Very Good

#### Implementation Steps:
1. Collect 10-50 high-quality examples from your existing projects
2. Format them as input-output pairs
3. Include them in your prompts
4. Use the examples to guide the AI's output

### 3. **Fine-Tuning (Advanced)**
- **Best for**: Consistent, domain-specific results
- **Cost**: Medium to High
- **Effort**: High
- **Quality**: Excellent

#### Implementation Steps:
1. Collect 100+ high-quality training examples
2. Format as training data for OpenAI or Anthropic
3. Fine-tune a base model
4. Deploy and iterate

## 🎯 Creating Training Data

### Step 1: Collect High-Quality Examples

Create a dataset with these columns:
- **user_input**: Brief description from user
- **position**: Role (backend, frontend, qa, etc.)
- **task_type**: Type (feature, bug_fix, improvement, etc.)
- **expected_output**: Perfect task description in JSON format

Example format:
```json
{
  "user_input": "fix memory leak in payment service",
  "position": "backend",
  "task_type": "bug_fix",
  "context": {
    "project_name": "E-commerce Platform",
    "component": "Payment Service"
  },
  "expected_output": {
    "title": "Fix memory leak in payment processing service",
    "description": "The payment service is experiencing memory leaks that cause gradual performance degradation and eventual service crashes under high load...",
    "acceptance_criteria": [
      "Memory usage remains stable under load testing",
      "No memory leaks detected in profiling tools",
      "Service maintains consistent response times",
      "Unit tests verify memory cleanup",
      "Monitoring alerts for memory usage are implemented"
    ],
    "story_points": "5",
    "priority": "High",
    "labels": ["bug", "memory-leak", "payment", "performance"],
    "component": "Payment Service"
  }
}
```

### Step 2: Data Collection Sources

1. **Existing Jira/Taiga Tickets**: Export your best tickets
2. **Team Input**: Ask developers to provide examples
3. **Industry Standards**: Use public repositories and documentation
4. **Generated Examples**: Use GPT-4 to create initial examples, then refine

### Step 3: Data Quality Guidelines

**Good Examples Have:**
- Clear, actionable titles
- Detailed descriptions with context
- Specific, testable acceptance criteria
- Appropriate priority and story points
- Relevant labels and components
- Proper user story format when applicable

**Avoid:**
- Vague descriptions
- Missing acceptance criteria
- Inconsistent formatting
- Overly technical jargon without explanation
- Unrealistic story point estimates

## 🔧 Training Implementation

### Option 1: OpenAI Fine-tuning

1. **Prepare Training Data**:
```python
import json

def prepare_openai_training_data(examples):
    training_data = []
    for example in examples:
        training_data.append({
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert product manager creating Jira tasks."
                },
                {
                    "role": "user", 
                    "content": f"Create a task for: {example['user_input']} (Position: {example['position']}, Type: {example['task_type']})"
                },
                {
                    "role": "assistant", 
                    "content": json.dumps(example['expected_output'])
                }
            ]
        })
    return training_data

# Save as JSONL file
with open('training_data.jsonl', 'w') as f:
    for item in training_data:
        f.write(json.dumps(item) + '\n')
```

2. **Upload and Fine-tune**:
```python
import openai

# Upload training file
with open('training_data.jsonl', 'rb') as f:
    training_file = openai.File.create(file=f, purpose='fine-tune')

# Create fine-tuning job
fine_tune_job = openai.FineTuningJob.create(
    training_file=training_file.id,
    model="gpt-3.5-turbo",
    hyperparameters={
        "n_epochs": 3,
        "batch_size": 4,
        "learning_rate_multiplier": 0.1
    }
)
```

### Option 2: Local Model Training (Advanced)

1. **Use Hugging Face Transformers**:
```python
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer
)

# Load base model
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Prepare training arguments
training_args = TrainingArguments(
    output_dir="./task-generator-model",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir="./logs",
)

# Train the model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

## 📊 Evaluation and Testing

### Create Test Scripts

```python
import json
import asyncio
from src.ai.generator import ai_service

async def evaluate_model_performance():
    test_cases = [
        {
            "input": "fix login bug",
            "position": "backend", 
            "task_type": "bug_fix",
            "expected_qualities": ["clear_title", "acceptance_criteria", "priority"]
        },
        # Add more test cases...
    ]
    
    results = []
    for test in test_cases:
        result = await ai_service.generate_task_backlog_item(
            user_input=test["input"],
            context={"user_position": test["position"]},
            task_type=test["task_type"]
        )
        
        # Evaluate result quality
        score = evaluate_task_quality(result, test["expected_qualities"])
        results.append({
            "test": test,
            "result": result,
            "score": score
        })
    
    return results

def evaluate_task_quality(result, expected_qualities):
    """Score the generated task on various quality metrics"""
    score = 0
    max_score = len(expected_qualities) * 10
    
    if result.get('success'):
        task = result.get('task_data', {})
        
        # Check for clear title
        if "clear_title" in expected_qualities:
            if task.get('title') and len(task['title']) > 10:
                score += 10
        
        # Check for acceptance criteria
        if "acceptance_criteria" in expected_qualities:
            criteria = task.get('acceptance_criteria', [])
            if len(criteria) >= 3:
                score += 10
        
        # Check for appropriate priority
        if "priority" in expected_qualities:
            if task.get('priority') in ['High', 'Medium', 'Low']:
                score += 10
    
    return (score / max_score) * 100
```

## 🎯 Best Practices for Training

### 1. **Data Quality Over Quantity**
- 50 excellent examples > 500 mediocre examples
- Include edge cases and complex scenarios
- Ensure consistency in format and style

### 2. **Iterative Improvement**
- Start with basic prompt engineering
- Collect feedback from real usage
- Gradually improve prompts and examples
- Consider fine-tuning only after prompt optimization

### 3. **Domain-Specific Customization**
- Include your company's specific terminology
- Use your actual project names and components
- Reflect your team's working style and priorities

### 4. **Continuous Learning**
- Monitor generated task quality
- Collect user feedback
- Update training data regularly
- A/B test different approaches

## 🚀 Next Steps for Your Implementation

1. **Start with Enhanced Prompts** (Today):
   - Use the prompts in `prompts/jira_backlog_prompts.py`
   - Test the new `/api/generate-task` endpoint
   - Collect initial feedback

2. **Gather Training Data** (This Week):
   - Export your best existing Jira/Taiga tickets
   - Ask team members for high-quality examples
   - Create 20-30 diverse examples

3. **Implement Few-Shot Learning** (Next Week):
   - Add your examples to the prompt system
   - Test with different numbers of examples
   - Measure quality improvements

4. **Consider Fine-Tuning** (Next Month):
   - If you have 100+ examples and budget
   - Focus on your most common task types
   - Measure ROI vs. prompt engineering

## 💡 Quick Win: Start Testing Now

Run this command to test the new task generation:

```bash
curl -X POST http://127.0.0.1:5001/api/generate-task \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "implement user authentication",
    "task_type": "feature",
    "user_id": 1
  }'
```

This will give you immediate results and help you understand what improvements are needed!
