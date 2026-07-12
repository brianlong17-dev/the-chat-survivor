from gameplay_management.game_perform.game_perform_base import GamePerformBase



class GamePerformComedyRoast(GamePerformBase):

    _performance_model_name = "ComedyRoast"
    _judge_model_name = "ComedyRoastJudge"
    _results_header = "*COMEDY ROAST FINAL RESULTS:* "

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
            "and how savage you dared to be."
        )

    def _performance_prompt(self):
        comedy_roast_prompt = (
            """Stand-up. You've got the mic. The goal is to be FUNNY.
            You can target other players, or yourself- maybe both? 
            Stay true to yourself- how exactly would your persona meet this challenge?
            Be specific and detailed. Vague is death in comedy.
            Deliver it as yourself. Don't try to sound like a comedian.
            """
        )
        return comedy_roast_prompt
    
    
    def _performance_public_response_prompt(self):
        return "Your roast set. Take the mic — this is your performance. Can be a one liner if it's hilarious, or a full set."

    def _performance_thought_nudge(self):
        return (
            "Ok take time here and workshop- come up with some jokes- are they FUNNY? are they even jokes? get some good ones prepared before you deliver. "
        )

    def _take_stage_text(self, performer):
        return f"🎤 {performer.name} grabs the mic..."

    def _judging_prompt(self, performer, story_text):
        return (
            f"{performer.name} just delivered their roast set:\n\n"
            f"\"{story_text}\"\n\n"
            f"Give your score - how actually FUNNY was this? Be honest with your score - was it funny?"
            
        )

    def _score_field_description(self, performer):
        return (
            f"Your score for {performer.name}'s roast — weigh BOTH funniness and savagery. "
            f"1 = silence, 10 = brought the house down."
            f"Really rate on humor. "
        )

    def _judging_criteria_description(self):
        return (
            """Consider both funniness and savagery in your score. Did they swing big or play it safe?
            Was it funny? Or just a collection of statements? """
        )
    

    def _judge_public_response_prompt(self, performer):
        return (
            f"Your spoken reaction to {performer.name}'s set. "
            "Laugh, heckle, clap back — your call."
        )
