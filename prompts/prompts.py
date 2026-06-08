class PromptLibrary:
    #Agent
    line_break = (f"\n{"="*50}")
    
    desc_agent_updated_game_strategy = ("Only populate if you want to update your game strategy. "
                                          "Based on how the game works, what is the smartest strategy?")
    desc_message = "Say what you want- Your thoughts and feelings should come through. (Don't repeat other messages. Say little if you have nothing new to say.)"
    desc_agent_lifeLessons = ("A new lesson to you mind that you will take forward. This will shape your future descisions. Take key lessons only, so you don't cloud your decision making.")
    desc_agent_position_assessment = ("Based on your position in the scoreboard, what do you need to do? If it's a discussion round, what is your position in the upcoming round? Can you help yourself in some way?")
    desc_agent_speaking_style = (
        "Only populate if your speaking style has evolved or shifted during this round — "
        "If nothing has changed, leave this blank. Do NOT explain or comment on why no change is needed. "
        "A description of HOW you talk, HOW you express yourself. "
        "NO specific word or phrases. "
        "Approximately as long and detailed as the previous speaking style."
    )
    desc_basic_thought = "Your internal thoughts. Strategy, feelings, and private observations."
    desc_basic_public_response = "What you actually say out loud to the group. Stay in character!"
   

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
        
   