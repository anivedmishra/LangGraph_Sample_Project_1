# Story Writer Graph 📖
**Powered by LangGraph + OpenAI**

Turn any one-line story idea into a complete, polished story using a parallel LangGraph pipeline.

---

## What It Does

The Story Writer Graph takes a user's story idea and runs it through a multi-node LangGraph pipeline:
START
|
+---> create_characters --------+
|                               |
+---> create_plot_outline ------+---> decide_story_length
|                               |         |
+---> create_setting_and_tone --+    (conditional)
/          
short?         expanded?
|               |
write_short_story   write_expanded_story
|               |
END             END

| Node | Role |
|------|------|
| `create_characters` | Designs 2-3 main characters with names, personalities, and roles |
| `create_plot_outline` | Builds beginning, middle, and ending of the story |
| `create_setting_and_tone` | Defines setting, mood, and genre |
| `decide_story_length` | Reads all 3 outputs and decides short vs expanded |
| `write_short_story` | Writes a focused 300-400 word story |
| `write_expanded_story` | Writes a rich 600-900 word multi-scene story |

---

## LangGraph Concepts Used

| Concept | Where |
|---------|-------|
| Pydantic State | `StoryState` class holds all data flowing through the graph |
| Parallel Nodes | 3 specialist nodes run at the same time from START |
| Fan-in | All 3 feed into `decide_story_length` |
| Conditional Edges | Routes to short or expanded story based on decision |
| StateGraph | Wires all nodes and edges together |

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/anivedmishra/LangGraph_Sample_Project_1.git
cd story-writer-graph
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your real key:
OPENAI_API_KEY=sk-your-real-key-here

### 5. Run the graph
```bash
python3 story_writer_graph.py
```

### Example
Your story idea: > a robot who learns to feel emotions

The graph will run all 3 specialist nodes in parallel, decide on story length, then print your complete story.

---

## Project Structure
story-writer-graph/
├── story_writer_graph.py   # Main LangGraph file
├── requirements.txt        # Python dependencies
├── .env.example            # API key template (never commit .env)
├── .gitignore              # Keeps secrets out of GitHub
├── archive/                # Reference files from original repo
└── README.md               # This file

---

## ⚠️ Important
Never commit your `.env` file. It is listed in `.gitignore`. Only `.env.example` with a placeholder goes to GitHub.
