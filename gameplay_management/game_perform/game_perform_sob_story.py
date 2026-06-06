from gameplay_management.game_perform.game_perform_base import GamePerformBase
from prompts.gamePrompts import GamePromptLibrary


class GamePerformSobStory(GamePerformBase):

    _performance_model_name = "SobStory"
    _judge_model_name = "SobStoryJudge"
    _results_header = "🎭 SOB STORY results"

    @classmethod
    def display_name(cls, cfg):
        return "Perform your sob story"

    @classmethod
    def rules_description(cls, cfg):
        return "Each player performs, and is scored by their fellow contestants!"

    def _host_intro_text(self):
        return GamePromptLibrary.sob_story_host_intro

    def _performance_prompt(self):
        return GamePromptLibrary.sob_story_prompt

    def _performance_public_response_prompt(self):
        return "Your sob story. This is your performance — make it count."

    def _performance_thought_nudge(self):
        return "What are you really going for here? What impression do you want to leave?"

    def _take_stage_text(self, performer):
        return f"🎤 {performer.name} takes the stage..."

    def _judging_prompt(self, performer, story_text):
        return (
            f"{performer.name} just shared their sob story:\n\n"
            f"\"{story_text}\"\n\n"
            f"Give your honest (or strategic) score and critique. "
            f"Your public response is your spoken critique — everyone will hear it."
        )

    def _score_field_description(self, performer):
        return f"Your score for {performer.name}'s story. 1 = unmoved, 10 = devastated."

    def _judging_criteria_description(self):
        return (
            "What lens are you judging through? Emotional authenticity? Language? Is it beautifully expressed? "
            "Delivery? Strategic value to you? How you feel about this player personally?"
        )

    def _judge_public_response_prompt(self, performer):
        return (
            f"Your spoken critique of {performer.name}'s story. "
            "Be honest, be cutting, be generous — your call."
        )
