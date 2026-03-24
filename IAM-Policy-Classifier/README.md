'''
iam_policy_classifier/
│
├── classifier/
│ ├── __init__.py
│ ├── engine.py # The core: connecting to LLM and returning a result
│ ├── prompt.py # The security prompt (separated!)
│ └── schemas.py # Structured Output
│
├── policies/
│ ├── weak_policy.json
│ ├── strong_policy.json
│ ├── strong/ ....
│ ├── weak/....
├── generator/ 
│   ├── agent.py        # The Generator Agent (LLM-based)
│   ├── schemas.py      # Output structure (policy + label)
├── prompt/
│    ├── classifier.yaml
 │   └── generator.yaml
├── providers/
│ ├── base.py # General LLM interface
│ ├── openai_provider.py # OpenAI implementation
│ └── ollama_provider.py # (Optional) Local model
│
├── generate_policies.py
├── run_demo.py # Full run + print
├── config.py # Keys / model / temperature
├── requirements.txt
└── README.md # A brief explanation of the architecture
'''
