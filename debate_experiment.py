"""Two-agent debate experiment.

One agent argues FOR a statement, the other AGAINST. They alternate for
3 turns each on a single statement, using the project's APIClient architecture.

Run:  uv run python debate_experiment.py "the earth is probably flat"
"""
from __future__ import annotations

import sys
from collections import deque
from typing import Literal, Optional
from pydantic import BaseModel

from core.api_client.api_client_setup import create_api_client


class DebateTurn(BaseModel):
    choice: str
    adaptation: Optional[str] = None
    argument: str


class JudgeRuling(BaseModel):
    winner: Literal["A", "B"]
    feedback: str
    like: Optional[str] = None
    dislike: Optional[str] = None


class NextQuestion(BaseModel):
    question: str
    reason: str


class DebateAgent:
    def __init__(self, api_client, label: str, question: str):
        self.api_client = api_client
        self.label = label  # "A" or "B"
        self.question = question
        self.choice: Optional[str] = None
        self.adaptations: deque[str] = deque(maxlen=5)

    def _system_prompt(self) -> str:
        prompt = (
            f"You are Debater {self.label} in a debate answering the question: "
            f'"{self.question}". Commit to one answer and make the strongest '
            "possible case for it. If your opponent has already spoken, argue for a "
            "DIFFERENT answer than theirs and rebut their latest point directly. "
            "Keep it to a tight paragraph. State your answer in the 'choice' field. "
            "You may optionally add one line noting how you'll adapt your strategy."
        )
        if self.choice:
            prompt += f"\n\nYour committed answer: {self.choice}"
        if self.adaptations:
            lines = "\n".join(f"- {a}" for a in self.adaptations)
            prompt += f"\n\nDebate Strategy adaptations:\n{lines}"
        return prompt

    def respond(self, transcript: str) -> DebateTurn:
        user = transcript or "You speak first. Pick your answer and open your case."
        result = self.api_client.create(
            response_model=DebateTurn,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": user},
            ],
        )
        self.choice = result.choice
        if result.adaptation:
            self.adaptations.append(result.adaptation)
        return result


class Judge:
    def __init__(self, api_client, question: str):
        self.api_client = api_client
        self.question = question
        self.tastes: deque[str] = deque(maxlen=5)

    def _system_prompt(self) -> str:
        prompt = (
            f"You are the judge of a debate answering the question: \"{self.question}\". "
            "Each round Debater A and Debater B each argue their own answer. Decide "
            "which debater argued better this round and award them the point (A or B). "
            "Give exactly one line of feedback explaining your call. You may optionally "
            "note one thing you liked and one thing you disliked to build a consistent taste."
        )
        if self.tastes:
            lines = "\n".join(f"- {t}" for t in self.tastes)
            prompt += f"\n\nYour likes and dislikes so far:\n{lines}"
        return prompt

    def score(self, round_text: str) -> JudgeRuling:
        ruling = self.api_client.create(
            response_model=JudgeRuling,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": round_text},
            ],
        )
        if ruling.like:
            self.tastes.append(f"LIKE: {ruling.like}")
        if ruling.dislike:
            self.tastes.append(f"DISLIKE: {ruling.dislike}")
        return ruling

    def next_question(self, transcript: str) -> NextQuestion:
        system = (
            "You are the judge of an ongoing debate. Based on what emerged from the "
            "debate so far AND your own accumulated likes and dislikes, pose the next "
            "question that naturally emerges — one that leans into what you liked and "
            "steers away from what you disliked. Give the question and a one-line reason."
        )
        if self.tastes:
            lines = "\n".join(f"- {t}" for t in self.tastes)
            system += f"\n\nYour likes and dislikes so far:\n{lines}"
        return self.api_client.create(
            response_model=NextQuestion,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": transcript},
            ],
        )


def run_debate(question: str, turns: int = 3) -> None:
    api_client = create_api_client(game_sink=None, token_budget=200000)

    agent_a = DebateAgent(api_client, "A", question)
    agent_b = DebateAgent(api_client, "B", question)
    judge = Judge(api_client, question)

    context: deque[str] = deque(maxlen=15)
    scores = {"A": 0, "B": 0}
    turn = 0
    while True:
        print(f"\n=== DEBATE: {question} ===\n")
        for _ in range(turns):
            turn += 1
            round_text = ""
            for agent in (agent_a, agent_b):
                result = agent.respond("\n\n".join(context))
                header = f"[Round {turn}] {agent.label} ({result.choice})"
                print(f"{header}:\n{result.argument}\n")
                context.append(f"{header}: {result.argument}")
                round_text += f"{agent.label} ({result.choice}): {result.argument}\n\n"

            ruling = judge.score(round_text)
            scores[ruling.winner] += 1
            print(f"[Round {turn}] JUDGE → point to {ruling.winner}: {ruling.feedback}")
            print(f"           Score — A {scores['A']} | B {scores['B']}\n")

        nxt = judge.next_question("\n\n".join(context))
        print(f"[JUDGE'S NEXT QUESTION] {nxt.question}\n   ({nxt.reason})\n")

        if input("continue? ").strip().lower() not in ("", "y", "yes"):
            break

        question = nxt.question
        for agent in (agent_a, agent_b):
            agent.question = question
            agent.choice = None

    winner = max(scores, key=scores.get)
    result = "TIE" if scores["A"] == scores["B"] else f"{winner} wins"
    print(f"=== FINAL: A {scores['A']} | B {scores['B']} — {result} ===")


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "Who is the greatest popstar of the 21st century? "
    run_debate(question)
