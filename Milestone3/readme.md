# FranchiseOps AI – Milestone 3
### AI-Powered Franchise Operations and Knowledge Management System

## 1. Project Overview

FranchiseOps AI is an AI-powered franchise management platform designed to simplify franchise operations through intelligent automation, centralized knowledge management, and AI-driven assistance.

Milestone 3 focuses on expanding the knowledge base, improving the AI Copilot, implementing document-based question answering using Retrieval-Augmented Generation (RAG), enhancing AI agents, and integrating all components with the existing application.

## 2. Objectives

- Collect and integrate 150+ relevant websites and PDF documents.
- Develop a document-based RAG pipeline.
- Add 50+ domain-specific questions to the AI Copilot.
- Implement FAISS-based vector retrieval.
- Implement BM25-based keyword retrieval.
- Improve existing AI agents.
- Integrate and test all Milestone 3 components with the application.

## 3. Key Features

### 3.1 Document-Based RAG System
- Collects franchise-related PDF documents.
- Extracts text from documents.
- Splits extracted text into manageable chunks.
- Generates embeddings for document chunks.
- Uses FAISS for vector similarity search.
- Uses BM25 for keyword-based retrieval.

### 3.2 AI Copilot
- Supports 50+ predefined franchise-related questions.
- Matches user queries with taught questions.
- Retrieves information from the PDF knowledge base when required.
- Generates context-aware responses.

### 3.3 Hybrid Retrieval
- FAISS retrieves semantically relevant information.
- BM25 retrieves keyword-relevant information.
- Combines retrieval approaches to improve information discovery.

### 3.4 AI Agents

The platform includes six specialized agents:

1. Workforce Agent
2. Outlets Agent
3. Inventory Agent
4. Marketing Agent
5. Sentiment Agent
6. Audit Agent

## 4. Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Vector Search | FAISS |
| Keyword Search | BM25 |
| Document Processing | PDF Extraction |
| AI/ML | NLP and Language Models |
| Development Environment | Google Colab, VS Code |
| Version Control | Git and GitHub |

## 5. RAG Workflow

```text
       PDF Documents
             |
             v
       Text Extraction
             |
             v
        Text Chunking
             |
             v
    Embedding Generation
             |
       +-----+-----+
       |           |
       v           v
     FAISS        BM25
       |           |
       +-----+-----+
             |
             v
      Relevant Retrieval
             |
             v
       AI Copilot
             |
             v
      Generated Response
```

## 6. Copilot Workflow

The AI Copilot uses two knowledge sources:

1. **Taught Questions:** Checks the predefined database containing 50+ franchise-related questions and answers.
2. **RAG Knowledge Base:** If a suitable taught question is not found, retrieves relevant information from indexed PDF documents.

This approach combines predefined knowledge with document-based question answering.

## 7. Milestone 3 Project Structure

```text
Milestone3/
│
├── FranchiseOpsAI_code.py
├── README.md
│
│
├── screenshots/
│   ├── login.png
│   ├── dashboard.png
│   ├── ai_copilot.png
│   ├── copilot_response.png
│  

```

## 8. Application Screenshots

### 8.1 Login Page

![Login Page](screenshots/login.jpeg)

### 8.2 Dashboard

![Dashboard](screenshots/dashboard.jpeg)

### 8.3 AI Copilot

![AI Copilot](screenshots/ai_copilot.jpeg)

### 8.4 Copilot Response

![Copilot Response](screenshots/copilot_response.jpeg)

## 9. Milestone 3 Deliverables

| Deliverable | Target |
|---|---|
| Website and PDF knowledge sources | 150+ |
| Copilot taught questions | 50+ |
| PDF-based RAG implementation | Completed |
| FAISS vector retrieval | Integrated |
| BM25 keyword retrieval | Integrated |
| AI agents | Enhanced |
| Application integration | Testing and validation |

## 10. Testing and Validation

- Verify PDF text extraction.
- Validate document chunking and indexing.
- Test FAISS vector retrieval.
- Test BM25 keyword retrieval.
- Verify Copilot taught-question matching.
- Test RAG fallback responses.
- Validate AI agent functionality.
- Test complete application integration.

## 11. Expected Outcome

Milestone 3 aims to deliver an enhanced FranchiseOps AI platform with an expanded knowledge base, intelligent Copilot, hybrid document retrieval, improved AI agents, and seamless integration with the existing application.

## 12. Team Contributions

| Team Member | Contributions |
|---|---|
| **Palak Agrawal** | AI Copilot,PPT |
| **Nuthi Sathwika** | RAG integration,Agents simulator|
| **Pullaiahgari Lahari** | taught questions for AI Copilot  |
| **Shruthi Borde** |project integration ,git|
|**Paramashivam**|- |
---

<div align="center">

## 💙 FranchiseOps AI

**Built as part of Infosys Springboard Internship 7.0**

*Transforming franchise operations through secure access, intelligent automation and data-driven insights.*

</div>

