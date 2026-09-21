# CyberGRC – RAG-Based Cybersecurity Risk & Compliance Assistant

**CyberGRC** is a high-speed, local RAG (Retrieval-Augmented Generation) demonstration system designed to map enterprise cybersecurity findings against authoritative GRC (Governance, Risk, and Compliance) security controls—including **NIST SP 800-53 Rev. 5, NIST CSF 2.0, CIS Controls v8.1.2, CSA CCM v4.0.12, and NIST AI Risk Management Framework**.

---

## 1. Problem Statement
Security analysts, GRC auditors, and IT teams frequently encounter audit findings or vulnerability observations (e.g., *"Administrative accounts do not use MFA"*). Mapping these raw observations to exact compliance frameworks, identifying control gaps, and formulating grounded remediation actions manually is time-consuming and prone to human oversight.

---

## 2. Why GRC & Why RAG?
- **Why GRC?** Governance, Risk, and Compliance frameworks provide the authoritative baseline requirements for enterprise security.
- **Why RAG?** Generic LLMs hallucinate control numbers or invent non-existent regulatory citations. RAG ensures that every assessment and remediation recommendation is **strictly grounded** in real, retrieved framework control text.

---

## 3. Dataset & Knowledge Base
CyberGRC uses the authoritative Hugging Face dataset:
`Zeezhu/grc-security-frameworks`

Coverage includes:
- **NIST SP 800-53 Rev. 5** (1,216 controls)
- **CSA CAIQ / CCM v4.0** (475 controls)
- **NIST Cybersecurity Framework 2.0** (225 controls)
- **CIS Controls v8.1.2** (166 controls)
- **NIST AI RMF Playbook** (72 controls)

---

## 4. System Architecture

```
User Input (Finding + Impact/Likelihood)
                   │
                   ▼
            Streamlit UI
                   │
                   ▼
         Query Preprocessing
                   │
                   ▼
     SentenceTransformers Embedding
                   │
                   ▼
       Persistent ChromaDB Vector Store
                   │
                   ▼
         Top-K Control Retrieval
                   │
                   ▼
     Relevance Threshold Filter (e.g., 0.35)
        │                          │
  Pass (Sim >= 0.35)        Fail (Sim < 0.35)
        │                          │
        ▼                          ▼
   Risk Matrix &           Explicit Response:
   Gap Synthesis           "No sufficiently relevant
        │                   security control was retrieved."
        ▼
 Evidence-Grounded Report
```

---

## 5. Performance Optimization & Speed Targets
Previous RAG prototypes suffered from 3+ minute retrieval delays caused by re-embedding datasets on every query.

**CyberGRC eliminates query latency through:**
1. **One-Time Persistent Indexing**: Dataset embedding happens **ONCE** via `python scripts/build_index.py`.
2. **Local CPU Embedding**: Uses `sentence-transformers/all-MiniLM-L6-v2` cached in memory.
3. **Persisted VectorDB**: Loads ChromaDB index from disk (`vectorstore/`) in `< 500 ms` on app startup.
4. **Sub-second Query Latency**: Real-time retrieval operates in **< 50 ms** on standard laptop hardware.

---

## 6. Strict No-Fallback & Evidence-Only Architecture
- **No Ollama / No Gemma Required**: CyberGRC runs fully local and fast.
- **Evidence-Only Mode (Default)**: Synthesizes structured remediation reports directly from retrieved document metadata without calling external LLMs.
- **Strict Relevance Thresholding**: If no control passes the similarity threshold (`>= 0.35`), the system returns:
  > *"No sufficiently relevant security control was retrieved. Please refine the finding."*
- **No Hallucination**: The system never invents control IDs or relies on ungrounded model memory.

---

## 7. Transparent Risk Model
CyberGRC incorporates a transparent 5x5 matrix risk model:
$$\text{Risk Score} = \text{Impact (1-5)} \times \text{Likelihood (1-5)}$$

- **1–4**: `LOW` (Green)
- **5–9**: `MEDIUM` (Yellow)
- **10–16**: `HIGH` (Orange)
- **17–25**: `CRITICAL` (Red)

*Note: This is a demonstration risk model and does not replace an organization's formal risk methodology.*

---

## 8. How to Run

### Step 1: Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 2: Build Persistent Vector Index (Run ONCE)
```bash
python scripts/build_index.py
```

### Step 3: Run Benchmark & Evaluation Suite
```bash
python scripts/evaluate.py
```

### Step 4: Launch Streamlit Web Application
```bash
streamlit run app.py
```

---

## 9. Test Scenarios & Evaluation Queries

Try these test cases in the UI:

1. **MFA Finding**: `"Administrative accounts do not use MFA."`
   - *Retrieved*: NIST AC-2/IA-2, CIS-6, CSA IAM-02.
2. **Logging Finding**: `"Security logs are not centrally monitored."`
   - *Retrieved*: NIST AU-2/AU-6, CIS-8, CSA SEF-04.
3. **Excessive Privileges**: `"Employees have excessive privileges."`
   - *Retrieved*: NIST AC-6 (Least Privilege), CIS-5.
4. **Encryption Finding**: `"Sensitive data is not encrypted."`
   - *Retrieved*: NIST SC-28/SC-13, CIS-3, CSA DSP-05.
5. **Asset Inventory**: `"Organization does not maintain an asset inventory."`
   - *Retrieved*: CIS-1, NIST CM-8, CSA IVS-01.
6. **Cloud Storage**: `"Cloud storage is publicly accessible."`
   - *Retrieved*: CSA CCM IVS-02 / DSP-01, NIST AC-3.
7. **Negative Query (Negative Control)**: `"I want a recipe for chocolate cake."`
   - *Result*: Explicitly rejected with `"No sufficiently relevant security control was retrieved. Please refine the finding."`

---

## 10. Important Limitations & Disclaimers
- **Prototype Status**: CyberGRC is a cybersecurity assessment prototype for demonstration purposes.
- **Not a Certification**: It does not replace formal audit, legal review, or organizational risk assessment.
- **Version Awareness**: Organizations must verify current framework versions for formal compliance reporting.
- **Strict Evidence Grounding**: Recommendations are strictly derived from retrieved text.

