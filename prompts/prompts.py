class PromptLibrary:
    #Agent
    line_break = (f"\n{"="*50}")
    
    desc_message = "Say what you want- Your thoughts and feelings should come through. (Don't repeat other messages. Say little if you have nothing new to say.)"
    desc_agent_position_assessment = ("Based on your position in the scoreboard, what do you need to do? If it's a discussion round, what is your position in the upcoming round? Can you help yourself in some way?")
    desc_agent_speaking_style = (
        "Only populate if your speaking style has evolved or shifted during this round — "
        "If nothing has changed, leave this blank. Do NOT explain or comment on why no change is needed. "
        "A description of HOW you talk, HOW you express yourself. "
        "NO specific word or phrases. "
        "Approximately as long and detailed as the previous speaking style."
    )
    desc_basic_thought = "Your internal thoughts. Think in voice. Strategy, feelings, and private observations. "
   

    @staticmethod
    def final_words_prompt():
        return (
            f"---------------------------------------------------------------------\n"
            f"🛑 GAME OVER 🛑\n"
            f"You have just been ELIMINATED. Your game is finished.\n"
            f"Do not plan for the next round. Do not try to save yourself.\n"
            f"Your Goal: Give a memorable final statement. You can be gracious, angry, confused, or vengeful.\n"
            f"---------------------------------------------------------------------\n"
            f"Your Final Words:"
        )
        
   