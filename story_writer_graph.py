import sys
import operator
import json
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()


class StoryState(BaseModel):
    story_idea: str = ""
    characters: str = ""
    plot_outline: str = ""
    setting_and_tone: str = ""
    needs_expanded_story: bool = False
    decision_reason: str = ""
    final_story: str = ""
    messages: Annotated[list, operator.add] = []


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8)


def create_characters(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a creative character designer. "
        f"The user has this story idea: '{state.story_idea}'. "
        f"Create 2-3 compelling main characters for this story. "
        f"For each character include: name, age, personality, and their role in the story. "
        f"Keep it concise and vivid."
    )
    return {
        "characters": response.content,
        "messages": [f"[create_characters] Done"]
    }


def create_plot_outline(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a skilled story plotter. "
        f"The user has this story idea: '{state.story_idea}'. "
        f"Create a clear plot outline with three parts: "
        f"Beginning (how the story starts), "
        f"Middle (the conflict and key events), "
        f"and Ending (how it resolves). "
        f"Keep each part to 2-3 sentences."
    )
    return {
        "plot_outline": response.content,
        "messages": [f"[create_plot_outline] Done"]
    }


def create_setting_and_tone(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a creative world-builder. "
        f"The user has this story idea: '{state.story_idea}'. "
        f"Define the setting (time period and location), "
        f"the mood (e.g. dark, hopeful, mysterious), "
        f"and the genre (e.g. sci-fi, romance, thriller). "
        f"Keep it concise and atmospheric."
    )
    return {
        "setting_and_tone": response.content,
        "messages": [f"[create_setting_and_tone] Done"]
    }


def decide_story_length(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a story editor. The user's idea is: '{state.story_idea}'.\n\n"
        f"Here is what the specialists have created:\n\n"
        f"CHARACTERS:\n{state.characters}\n\n"
        f"PLOT OUTLINE:\n{state.plot_outline}\n\n"
        f"SETTING AND TONE:\n{state.setting_and_tone}\n\n"
        f"Decide: does this story idea have enough complexity for an EXPANDED story "
        f"(600-900 words, rich detail, multiple scenes) "
        f"or is a SHORT story better (300-400 words, focused, single scene)?\n\n"
        f"Reply STRICTLY in this JSON format (no other text):\n"
        f'{{"needs_expanded_story": true/false, "reason": "one sentence explanation"}}'
    )
    try:
        result = json.loads(response.content)
        needs_expanded = result["needs_expanded_story"]
        reason = result["reason"]
    except (json.JSONDecodeError, KeyError):
        needs_expanded = False
        reason = "Could not parse decision, defaulting to short story."

    return {
        "needs_expanded_story": needs_expanded,
        "decision_reason": reason,
        "messages": [f"[decide_story_length] expanded={needs_expanded}"]
    }


def write_short_story(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a talented fiction author. "
        f"Write a short story (300-400 words) based on these elements:\n\n"
        f"STORY IDEA: {state.story_idea}\n"
        f"CHARACTERS: {state.characters}\n"
        f"PLOT: {state.plot_outline}\n"
        f"SETTING AND TONE: {state.setting_and_tone}\n\n"
        f"Give the story a compelling title on the first line. "
        f"Write in third-person past tense. "
        f"Keep it focused on a single powerful scene. "
        f"End with a memorable closing line."
    )
    return {
        "final_story": f"SHORT STORY (300-400 words)\n{'='*45}\n{response.content}",
        "messages": [f"[write_short_story] Done"]
    }


def write_expanded_story(state: StoryState) -> dict:
    response = llm.invoke(
        f"You are a talented fiction author. "
        f"Write an expanded short story (600-900 words) based on these elements:\n\n"
        f"STORY IDEA: {state.story_idea}\n"
        f"CHARACTERS: {state.characters}\n"
        f"PLOT: {state.plot_outline}\n"
        f"SETTING AND TONE: {state.setting_and_tone}\n\n"
        f"Give the story a compelling title on the first line. "
        f"Write in third-person past tense. "
        f"Include multiple scenes that follow the beginning, middle, and ending. "
        f"Use vivid sensory language and dialogue. "
        f"End with a satisfying and memorable conclusion."
    )
    return {
        "final_story": f"EXPANDED STORY (600-900 words)\n{'='*45}\n{response.content}",
        "messages": [f"[write_expanded_story] Done"]
    }


def route_after_decision(state: StoryState) -> str:
    if state.needs_expanded_story:
        return "expanded"
    else:
        return "short"


graph = StateGraph(StoryState)

graph.add_node("create_characters", create_characters)
graph.add_node("create_plot_outline", create_plot_outline)
graph.add_node("create_setting_and_tone", create_setting_and_tone)
graph.add_node("decide_story_length", decide_story_length)
graph.add_node("write_short_story", write_short_story)
graph.add_node("write_expanded_story", write_expanded_story)

graph.add_edge(START, "create_characters")
graph.add_edge(START, "create_plot_outline")
graph.add_edge(START, "create_setting_and_tone")

graph.add_edge("create_characters", "decide_story_length")
graph.add_edge("create_plot_outline", "decide_story_length")
graph.add_edge("create_setting_and_tone", "decide_story_length")

graph.add_conditional_edges(
    "decide_story_length",
    route_after_decision,
    {
        "short": "write_short_story",
        "expanded": "write_expanded_story",
    }
)

graph.add_edge("write_short_story", END)
graph.add_edge("write_expanded_story", END)

app = graph.compile()


def run_story_graph(story_idea: str):
    print("=" * 55)
    print("  STORY WRITER GRAPH")
    print(f"  Your idea: \"{story_idea}\"")
    print("=" * 55)

    result = app.invoke({
        "story_idea": story_idea,
        "messages": [],
    })

    print("\n" + "=" * 55)
    print("  YOUR STORY")
    print("=" * 55)
    print(f"\n{result['final_story']}")

    print("\n" + "-" * 55)
    print("  NODE LOG")
    print("-" * 55)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  STORY WRITER GRAPH")
    print("  Powered by LangGraph + OpenAI")
    print("=" * 55)
    print("\n  Give me a story idea and I'll build it into")
    print("  a complete story for you.")
    print("  Type 'quit' to exit.\n")

    while True:
        story_idea = input("  Your story idea: > ").strip()

        if story_idea.lower() in ("quit", "exit", "q"):
            print("\n  Happy storytelling! Goodbye!\n")
            break

        if not story_idea:
            continue

        run_story_graph(story_idea)
        print("\n")
