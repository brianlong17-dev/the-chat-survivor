from gameplay_management.game_perform.game_perform_base import GamePerformBase



class GamePerformComedyRoast(GamePerformBase):

    _performance_model_name = "ComedyRoast"
    _judge_model_name = "ComedyRoastJudge"
    _results_header = "🔥 COMEDY ROAST results"

    @classmethod
    def display_name(cls, cfg):
        return "Comedy Roast"

    @classmethod
    def rules_description(cls, cfg):
        return "Do your stand-up set — roast yourself, the group, or a single rival. Peers score 1-10."

    def _host_intro_text(self):
        return (
            "🔥 COMEDY ROAST!\n"
            "Time to find out who's actually funny under pressure. "
            "Each of you gets the mic for a roast set — and you choose the target: "
            "roast yourself, roast the whole group, or pick one rival and go for the jugular. "
            "Your fellow contestants will score 1-10 — weighing BOTH how funny you were "
            "and how savage you dared to be. Self-deprecation is safe. Going after someone? "
            "They'll remember."
        )

    def _performance_prompt(self):
        comedy_roast_prompt = (
            "Stand-up. You've got the mic. Pick one:\n"
            "  • Yourself — own your flaws.\n"
            "  • The group — the whole cast, the game, this absurd situation.\n"
            "  • One player — name them, get specific.\n"
            "Be specific, not clever. Name real things — what someone "
            "actually did in this game, a true detail. Vague is death.\n"
            "Keep it short. Do it as yourself — don't try to sound like a comedian."
        )
        return comedy_roast_prompt
    
    
    def _performance_public_response_prompt(self):
        return "Your roast set. Take the mic — this is your performance. Can be a one liner or a full set."

    def _performance_thought_nudge(self):
        return (
            "Which strategy are you taking — self-roast, roast the whole group, or pick one player? "
            "What do you find FUNNY? What would be funny with the crowd?"
        )

    def _take_stage_text(self, performer):
        return f"🎤 {performer.name} grabs the mic..."

    def _judging_prompt(self, performer, story_text):
        return (
            f"{performer.name} just delivered their roast set:\n\n"
            f"\"{story_text}\"\n\n"
            f"Give your score and your spoken reaction. "
            f"Your public response is what the room hears. Should be brief."
            
        )

    def _score_field_description(self, performer):
        return (
            f"Your score for {performer.name}'s roast — weigh BOTH funniness and savagery. "
            f"1 = silence, 10 = brought the house down."
            f"Please give credit when someone is ACTUALLY funny. It's only fair. "
        )

    def _judging_criteria_description(self):
        return (
            "Consider BOTH axes when assigning your single 1-10 score: "
            "(a) FUNNINESS — did it actually land, was it clever, well-delivered? "
            "(b) SAVAGERY — did they take a real risk, or play it safe? "
            "A safe, mildly funny self-roast and a brutal but unfunny attack should both score mid. "
            "Top scores need both. Don't forget: if they came for you, that's allowed to colour your score — "
            "but everyone is watching how you judge."
        )
    

    def _judge_public_response_prompt(self, performer):
        return (
            f"Your spoken reaction to {performer.name}'s set. "
            "Laugh, heckle, clap back — your call."
        )
